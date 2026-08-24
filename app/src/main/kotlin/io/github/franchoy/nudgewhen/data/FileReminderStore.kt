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
 * File-backed [ReminderStore] using a simple line-oriented wire format:
 *
 *   NWR1
 *   <id><TAB><base64url-encoded-utf-8-text>
 *   ...
 *
 * Records are separated by a single LF (`\n`). There is no trailing LF after
 * the final record, and `save(emptyList())` produces exactly the header line
 * `NWR1`. ID grammar rules and Base64URL-with-padding are used both when
 * loading and when saving.
 *
 * Validation correctness boundary:
 * - `save` validates the complete input list before opening/truncating the
 *   target file, so a failed validation cannot destroy an existing valid
 *   file on disk.
 * - `save` serializes the complete output in memory before writing.
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

        if (lines[0] != HEADER) {
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
            if (record.indexOf('\t', firstTab + 1) >= 0) {
                throw IllegalStateException("Reminder record with multiple TAB separators")
            }

            val id = record.substring(0, firstTab)
            val encodedText = record.substring(firstTab + 1)

            validateLoadedId(id)
            if (!seenIds.add(id)) {
                throw IllegalStateException("Duplicate reminder id: $id")
            }

            val decodedText: String = decodeBase64UrlToText(encodedText, id)
            reminders.add(Reminder(id, decodedText))
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
        builder.append(HEADER)
        for (reminder in reminders) {
            val textBytes = reminder.text.toByteArray(StandardCharsets.UTF_8)
            val encodedText = Base64.getUrlEncoder().encodeToString(textBytes)
            builder.append('\n')
            builder.append(reminder.id)
            builder.append('\t')
            builder.append(encodedText)
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
        const val HEADER: String = "NWR1"
    }
}