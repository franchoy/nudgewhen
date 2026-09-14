package io.github.franchoy.nudgewhen.data

import io.github.franchoy.nudgewhen.domain.Reminder
import io.github.franchoy.nudgewhen.domain.ReminderStore
import java.io.File
import java.nio.ByteBuffer
import java.nio.CharBuffer
import java.nio.charset.CharacterCodingException
import java.nio.charset.CodingErrorAction
import java.nio.charset.StandardCharsets
import java.util.Base64

/**
 * File-backed [ReminderStore] using a line-oriented wire format.
 *
 * Two header versions are supported on load:
 *
 *   NWR1
 *   <id><TAB><base64url-encoded-utf-8-text>
 *   ...
 *
 *   NWR2
 *   <id><TAB><base64url-encoded-utf-8-text><TAB><done-literal>
 *   ...
 *
 * `done-literal` is `0` for `done = false` and `1` for `done = true`.
 *
 * Records are separated by a single LF (`\n`). There is no trailing LF after
 * the final record, and `save(emptyList())` produces exactly the header line
 * `NWR2`. ID grammar rules and Base64URL-with-padding are used both when
 * loading and when saving.
 *
 * NWR1 records are loaded with `done = false`; NWR1 is read-only. The first
 * later successful ordinary `save` rewrites the same file as NWR2 (lazy
 * in-place format migration). No migration flag and no load-time rewrite
 * are performed.
 *
 * Headers other than `NWR1` and `NWR2` are rejected with
 * `IllegalStateException`.
 *
 * Validation correctness boundary:
 * - `save` validates the complete input list before opening/truncating the
 *   target file, so a failed validation cannot destroy an existing valid
 *   file on disk.
 * - `save` serializes the complete output in memory before writing.
 * - NWR1-on-disk lazy migration to NWR2 is provided by controller-level
 *   no-save paths (same-state `setDone` and normalized-identical `edit`),
 *   which do not invoke `save`. The first successful `save` rewrites the
 *   complete file as NWR2.
 * - This implementation does not promise preservation of old on-disk bytes
 *   after an actual filesystem I/O failure during write.
 */
class FileReminderStore(
    private val file: File,
) : ReminderStore {

    override fun load(): List<Reminder> {
        if (!file.exists()) return emptyList()

        val rawBytes = file.readBytes()

        val fileText: String = decodeStrictUtf8(rawBytes, "persistence file")

        if (fileText.isEmpty()) {
            throw IllegalStateException("Empty persistence file")
        }

        val lines: List<String> = splitLogicalLines(fileText)

        if (lines.isEmpty()) {
            throw IllegalStateException("Empty persistence file")
        }

        val header = lines[0]
        if (header != HEADER_NWR1 && header != HEADER_NWR2) {
            throw IllegalStateException("Unsupported persistence file header")
        }

        val records: List<String> = lines.drop(1)
        val reminders = ArrayList<Reminder>(records.size)
        val seenIds = HashSet<String>(records.size)

        for (record in records) {
            if (record.isEmpty()) {
                throw IllegalStateException("Blank reminder record")
            }

            val firstTab = record.indexOf('\t')
            if (firstTab < 0) {
                throw IllegalStateException("Reminder record without TAB separator")
            }

            val id: String
            val encodedText: String
            val doneLiteral: String?

            if (header == HEADER_NWR2) {
                val secondTab = record.indexOf('\t', firstTab + 1)
                if (secondTab < 0) {
                    throw IllegalStateException(
                        "NWR2 reminder record missing done field TAB separator",
                    )
                }
                if (record.indexOf('\t', secondTab + 1) >= 0) {
                    throw IllegalStateException(
                        "NWR2 reminder record with extra TAB separator",
                    )
                }
                id = record.substring(0, firstTab)
                encodedText = record.substring(firstTab + 1, secondTab)
                doneLiteral = record.substring(secondTab + 1)
            } else {
                if (record.indexOf('\t', firstTab + 1) >= 0) {
                    throw IllegalStateException("Reminder record with multiple TAB separators")
                }
                id = record.substring(0, firstTab)
                encodedText = record.substring(firstTab + 1)
                doneLiteral = null
            }

            validateLoadedId(id)
            if (!seenIds.add(id)) {
                throw IllegalStateException("Duplicate reminder id: $id")
            }

            val decodedText: String = decodeBase64UrlToText(encodedText, id)
            val done: Boolean = when (doneLiteral) {
                null -> false
                "0" -> false
                "1" -> true
                else -> throw IllegalStateException(
                    "Invalid done literal for reminder id: $id",
                )
            }
            reminders.add(Reminder(id, decodedText, done))
        }

        return reminders
    }

    override fun save(reminders: List<Reminder>) {
        val seenIds = HashSet<String>(reminders.size)
        for (reminder in reminders) {
            validateSaveId(reminder.id)
            if (!seenIds.add(reminder.id)) {
                throw IllegalArgumentException("Duplicate reminder id: ${reminder.id}")
            }
        }

        val encoded: ByteArray = serialize(reminders)
        file.writeBytes(encoded)
    }

    private fun serialize(reminders: List<Reminder>): ByteArray {
        val builder = StringBuilder()
        builder.append(HEADER_NWR2)
        for (reminder in reminders) {
            val textBytes = reminder.text.toByteArray(StandardCharsets.UTF_8)
            val encodedText = Base64.getUrlEncoder().encodeToString(textBytes)
            builder.append('\n')
            builder.append(reminder.id)
            builder.append('\t')
            builder.append(encodedText)
            builder.append('\t')
            builder.append(if (reminder.done) "1" else "0")
        }
        return builder.toString().toByteArray(StandardCharsets.UTF_8)
    }

    private fun validateSaveId(id: String) {
        if (id.isEmpty() ||
            id.contains('\t') ||
            id.contains('\r') ||
            id.contains('\n')
        ) {
            throw IllegalArgumentException("Invalid reminder id")
        }
    }

    private fun validateLoadedId(id: String) {
        if (id.isEmpty()) {
            throw IllegalStateException("Empty reminder id")
        }
        if (id.contains('\t')) {
            throw IllegalStateException("Reminder id contains TAB")
        }
        if (id.contains('\r')) {
            throw IllegalStateException("Reminder id contains CR")
        }
        // An LF in a loaded ID would already have split the record into
        // multiple logical lines, so this case is reported at split time.
    }

    private fun splitLogicalLines(text: String): List<String> {
        // Persistence records use LF as the only line separator.
        if (text.endsWith("\n")) {
            throw IllegalStateException("Trailing LF in persistence file")
        }
        return text.split("\n")
    }

    private fun decodeBase64UrlToText(encoded: String, id: String): String {
        val decodedBytes: ByteArray = try {
            Base64.getUrlDecoder().decode(encoded)
        } catch (e: IllegalArgumentException) {
            throw IllegalStateException(
                "Invalid Base64URL for reminder id: $id",
                e,
            )
        }
        return decodeStrictUtf8(decodedBytes, "reminder id $id")
    }

    private fun decodeStrictUtf8(bytes: ByteArray, source: String): String {
        val decoder = StandardCharsets.UTF_8.newDecoder()
            .onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT)
        try {
            val charBuffer: CharBuffer = decoder.decode(ByteBuffer.wrap(bytes))
            return charBuffer.toString()
        } catch (e: CharacterCodingException) {
            throw IllegalStateException(
                "Malformed UTF-8 in $source",
                e,
            )
        }
    }

    companion object {
        const val HEADER_NWR1: String = "NWR1"
        const val HEADER_NWR2: String = "NWR2"
    }
}
