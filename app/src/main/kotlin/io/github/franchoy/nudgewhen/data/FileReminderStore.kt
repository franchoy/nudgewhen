package io.github.franchoy.nudgewhen.data

import io.github.franchoy.nudgewhen.domain.Reminder
import io.github.franchoy.nudgewhen.domain.ReminderStore
import java.io.File
import java.nio.ByteBuffer
import java.nio.CharBuffer
import java.nio.charset.CharacterCodingException
import java.nio.charset.CodingErrorAction
import java.nio.charset.StandardCharsets
import java.time.DateTimeException
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.time.format.ResolverStyle
import java.util.Base64

/**
 * File-backed [ReminderStore] using a line-oriented wire format.
 *
 * Three header versions are supported on load:
 *
 *   NWR1
 *   <id><TAB><base64url-encoded-utf-8-text>
 *   ...
 *
 *   NWR2
 *   <id><TAB><base64url-encoded-utf-8-text><TAB><done-literal>
 *   ...
 *
 *   NWR3
 *   <id><TAB><base64url-encoded-utf-8-text><TAB><done-literal><TAB><time-literal>
 *   ...
 *
 * `done-literal` is `0` for `done = false` and `1` for `done = true`.
 *
 * `time-literal` is `-` for an absent reminder time, or a minute-precision
 * local wall-clock timestamp written as `uuuu-MM-dd'T'HH:mm`, for example
 * `2024-01-31T08:30`.
 *
 * Records are separated by a single LF (`\n`). There is no trailing LF after
 * the final record, and `save(emptyList())` produces exactly the header line
 * `NWR3`. ID grammar rules and Base64URL-with-padding are used both when
 * loading and when saving.
 *
 * Backward compatibility on load:
 * - NWR1 records load with `done = false` and `time = null`.
 * - NWR2 records load with their stored `done` value and `time = null`.
 * - NWR3 records load with their stored `done` value and their stored time.
 *
 * NWR1 and NWR2 are read-only formats: loading never rewrites the file. The
 * first later successful persistence-changing save rewrites the same file as
 * NWR3 (lazy in-place format migration). No migration flag, no separate
 * migration file and no load-time rewrite are performed.
 *
 * Headers other than `NWR1`, `NWR2` and `NWR3` are rejected with
 * `IllegalStateException`.
 *
 * Date/time validation:
 * - One explicitly constructed strict formatter is used in both directions:
 *   `DateTimeFormatter.ofPattern("uuuu-MM-dd'T'HH:mm").withResolverStyle(ResolverStyle.STRICT)`.
 * - A loaded time literal is parsed with that formatter, is rejected when the
 *   year is outside `1..9999` or when seconds/nanoseconds are non-zero, and
 *   is then re-serialized with the very same formatter. The re-serialized
 *   text must be exactly equal to the original literal, so only canonical
 *   timestamps are accepted.
 * - A save-side time is accepted when it is `null`, when seconds and
 *   nanoseconds are zero and when the year is inside `1..9999`; otherwise an
 *   `IllegalArgumentException` is raised.
 * - Malformed persisted data raises `IllegalStateException`.
 *
 * Validation correctness boundary:
 * - `save` validates the complete input list before opening/truncating the
 *   target file, so a failed validation cannot destroy an existing valid
 *   file on disk.
 * - `save` serializes the complete output in memory before writing.
 * - Legacy-format lazy migration to NWR3 is provided by controller-level
 *   no-save paths (same-state `setDone`, same-state `setTime` and
 *   normalized-identical `edit`), which do not invoke `save`. The first
 *   successful persistence-changing save rewrites the complete file as NWR3.
 * - This implementation does not promise preservation of old on-disk bytes
 *   after an actual filesystem I/O failure during write, and it does not
 *   claim crash-safe atomic filesystem replacement.
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
        if (header != HEADER_NWR1 && header != HEADER_NWR2 && header != HEADER_NWR3) {
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
            val timeLiteral: String?

            if (header == HEADER_NWR3) {
                val secondTab = record.indexOf('\t', firstTab + 1)
                if (secondTab < 0) {
                    throw IllegalStateException(
                        "NWR3 reminder record missing done field TAB separator",
                    )
                }
                val thirdTab = record.indexOf('\t', secondTab + 1)
                if (thirdTab < 0) {
                    throw IllegalStateException(
                        "NWR3 reminder record missing time field TAB separator",
                    )
                }
                if (record.indexOf('\t', thirdTab + 1) >= 0) {
                    throw IllegalStateException(
                        "NWR3 reminder record with extra TAB separator",
                    )
                }
                id = record.substring(0, firstTab)
                encodedText = record.substring(firstTab + 1, secondTab)
                doneLiteral = record.substring(secondTab + 1, thirdTab)
                timeLiteral = record.substring(thirdTab + 1)
            } else if (header == HEADER_NWR2) {
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
                timeLiteral = null
            } else {
                if (record.indexOf('\t', firstTab + 1) >= 0) {
                    throw IllegalStateException("Reminder record with multiple TAB separators")
                }
                id = record.substring(0, firstTab)
                encodedText = record.substring(firstTab + 1)
                doneLiteral = null
                timeLiteral = null
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
            val time: LocalDateTime? = when {
                timeLiteral == null -> null
                timeLiteral == ABSENT_TIME_LITERAL -> null
                else -> parseLoadedTime(timeLiteral, id)
            }
            reminders.add(Reminder(id, decodedText, done, time))
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
            validateSaveTime(reminder.time)
        }

        val encoded: ByteArray = serialize(reminders)
        file.writeBytes(encoded)
    }

    private fun serialize(reminders: List<Reminder>): ByteArray {
        val builder = StringBuilder()
        builder.append(HEADER_NWR3)
        for (reminder in reminders) {
            val textBytes = reminder.text.toByteArray(StandardCharsets.UTF_8)
            val encodedText = Base64.getUrlEncoder().encodeToString(textBytes)
            builder.append('\n')
            builder.append(reminder.id)
            builder.append('\t')
            builder.append(encodedText)
            builder.append('\t')
            builder.append(if (reminder.done) "1" else "0")
            builder.append('\t')
            val time = reminder.time
            builder.append(if (time == null) ABSENT_TIME_LITERAL else formatSaveTime(time))
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

    private fun validateSaveTime(time: LocalDateTime?) {
        if (time == null) return

        if (time.second != 0 || time.nano != 0) {
            throw IllegalArgumentException(
                "Reminder time must have minute precision: $time",
            )
        }

        if (time.year < MIN_TIME_YEAR || time.year > MAX_TIME_YEAR) {
            throw IllegalArgumentException(
                "Reminder time year is outside the accepted bounds " +
                    "$MIN_TIME_YEAR..$MAX_TIME_YEAR: $time",
            )
        }
    }

    private fun formatSaveTime(time: LocalDateTime): String = TIME_FORMATTER.format(time)

    private fun parseLoadedTime(literal: String, id: String): LocalDateTime {
        val parsed: LocalDateTime = try {
            LocalDateTime.parse(literal, TIME_FORMATTER)
        } catch (e: DateTimeException) {
            throw IllegalStateException(
                "Invalid time literal for reminder id: $id",
                e,
            )
        }

        if (parsed.year < MIN_TIME_YEAR || parsed.year > MAX_TIME_YEAR) {
            throw IllegalStateException(
                "Time literal year outside the accepted bounds for reminder id: $id",
            )
        }

        if (parsed.second != 0 || parsed.nano != 0) {
            throw IllegalStateException(
                "Time literal with non-zero seconds or nanoseconds for reminder id: $id",
            )
        }

        // Canonical-form gate: the parsed value is re-serialized with the very
        // same strict formatter and the result must equal the original literal
        // exactly. Any non-canonical spelling is rejected.
        val canonical: String = TIME_FORMATTER.format(parsed)
        if (canonical != literal) {
            throw IllegalStateException(
                "Non-canonical time literal for reminder id: $id",
            )
        }

        return parsed
    }

    companion object {
        const val HEADER_NWR1: String = "NWR1"
        const val HEADER_NWR2: String = "NWR2"
        const val HEADER_NWR3: String = "NWR3"

        private const val ABSENT_TIME_LITERAL: String = "-"
        private const val MIN_TIME_YEAR: Int = 1
        private const val MAX_TIME_YEAR: Int = 9999

        private val TIME_FORMATTER: DateTimeFormatter = DateTimeFormatter
            .ofPattern("uuuu-MM-dd'T'HH:mm")
            .withResolverStyle(ResolverStyle.STRICT)
    }
}
