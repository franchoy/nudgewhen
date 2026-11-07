package io.github.franchoy.nudgewhen.data

import io.github.franchoy.nudgewhen.domain.Reminder
import io.github.franchoy.nudgewhen.domain.ReminderController
import io.github.franchoy.nudgewhen.domain.ReminderStore
import org.junit.After
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import java.io.File
import java.nio.file.Files
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.time.format.ResolverStyle
import java.util.Base64

class FileReminderStoreTest {

    private lateinit var tempDir: File

    @Before
    fun setUp() {
        tempDir = Files.createTempDirectory("nwr-store-").toFile()
    }

    @After
    fun tearDown() {
        deleteRecursively(tempDir)
    }

    private fun deleteRecursively(file: File) {
        if (!file.exists()) return
        if (file.isDirectory) {
            file.listFiles()?.forEach { deleteRecursively(it) }
        }
        file.delete()
    }

    private fun target(): File = File(tempDir, "reminders.nwr")

    private fun newStore(): FileReminderStore = FileReminderStore(target())

    // ----------------------------------------------------------------
    // Missing file / header-only / round-trip
    // ----------------------------------------------------------------

    @Test
    fun P3_01_missing_file_load_returns_empty_list() {
        assertFalse(target().exists())
        assertEquals(emptyList<Reminder>(), newStore().load())
    }

    @Test
    fun P3_02_NWR1_header_only_file_load_returns_empty_list() {
        val file = target()
        file.writeText("NWR1")
        assertEquals(emptyList<Reminder>(), newStore().load())
    }

    @Test
    fun P3_02b_NWR2_header_only_file_load_returns_empty_list() {
        val file = target()
        file.writeText("NWR2")
        assertEquals(emptyList<Reminder>(), newStore().load())
    }

    @Test
    fun P3_03_save_empty_list_writes_exact_NWR3_header_without_trailing_LF() {
        val store = newStore()
        store.save(emptyList())
        val bytes = target().readBytes()
        assertArrayEquals("NWR3".toByteArray(Charsets.UTF_8), bytes)
        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR3", text)
        assertFalse(text.endsWith("\n"))
    }

    @Test
    fun P3_04_one_reminder_writes_NWR3_LF_wire_format_with_padding_done_zero_absent_time_and_round_trips() {
        val store = newStore()
        val reminder = Reminder("id-1", "Hello")
        store.save(listOf(reminder))

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR3\nid-1\tSGVsbG8=\t0\t-", text)

        val firstRecord = text.substringAfter('\n')
        val tabs = firstRecord.count { it == '\t' }
        assertEquals(3, tabs)
        val fields = firstRecord.split("\t")
        assertEquals(4, fields.size)
        assertEquals("id-1", fields[0])
        val encodedSegment = fields[1]
        assertTrue("expected Base64URL padding", encodedSegment.contains('='))
        val doneSegment = fields[2]
        assertEquals("0", doneSegment)
        val timeSegment = fields[3]
        assertEquals("-", timeSegment)

        assertEquals(listOf(reminder), newStore().load())
    }

    @Test
    fun P3_05_multiple_reminders_round_trip_in_exact_input_order_with_default_done_false() {
        val store = newStore()
        val reminders = listOf(
            Reminder("a", "first"),
            Reminder("b", "second"),
            Reminder("c", "third"),
            Reminder("d", "fourth"),
        )
        store.save(reminders)
        assertEquals(reminders, newStore().load())
    }

    @Test
    fun P3_06_id_with_ordinary_spaces_round_trips_unchanged_and_is_not_trimmed() {
        val store = newStore()
        val reminder = Reminder("  spaced id  ", "content")
        store.save(listOf(reminder))
        assertEquals(listOf(reminder), newStore().load())
    }

    @Test
    fun P3_07_arbitrary_unicode_reminder_text_round_trips_exactly() {
        val store = newStore()
        val unicodeText = "Héllo 👋 世界 — Ω∞"
        val reminder = Reminder("u-1", unicodeText)
        store.save(listOf(reminder))
        assertEquals(listOf(reminder), newStore().load())
    }

    @Test
    fun P3_08_reminder_text_with_TAB_CR_LF_round_trips_exactly_via_Base64URL_in_NWR3() {
        val store = newStore()
        val trickyText = "line1\tcol\nline2\rcol2"
        val reminder = Reminder("tricky", trickyText)
        store.save(listOf(reminder))

        val text = target().readText(Charsets.UTF_8)
        val lines = text.split("\n")
        assertEquals(2, lines.size)
        assertEquals("NWR3", lines[0])
        val record = lines[1]
        assertEquals(3, record.count { it == '\t' })
        val firstTab = record.indexOf('\t')
        val secondTab = record.indexOf('\t', firstTab + 1)
        val thirdTab = record.indexOf('\t', secondTab + 1)
        assertTrue(secondTab > firstTab)
        assertTrue(thirdTab > secondTab)
        val encoded = record.substring(firstTab + 1, secondTab)
        val doneLiteral = record.substring(secondTab + 1, thirdTab)
        val timeLiteral = record.substring(thirdTab + 1)
        assertEquals("0", doneLiteral)
        assertEquals("-", timeLiteral)
        assertNotEquals('=', encoded[0])
        assertFalse("TAB must not appear in encoded form", encoded.contains('\t'))
        assertFalse("CR must not appear in encoded form", encoded.contains('\r'))
        assertFalse("LF must not appear in encoded form", encoded.contains('\n'))

        assertEquals(listOf(reminder), newStore().load())
    }

    @Test
    fun P3_09_new_instance_restores_previously_saved_list() {
        val storeA = newStore()
        val reminders = listOf(
            Reminder("alpha", "one"),
            Reminder("beta", "two"),
        )
        storeA.save(reminders)

        val storeB = newStore()
        assertEquals(reminders, storeB.load())
    }

    @Test
    fun P3_10_real_controller_with_real_store_remove_persists_remaining_in_order() {
        val storeA = newStore()
        val idSequence = ArrayList<String>()
        var counter = 0
        val controllerA = ReminderController(
            storeA,
            idGenerator = {
                counter += 1
                val id = "gen-$counter"
                idSequence.add(id)
                id
            },
        )
        controllerA.create("first")
        controllerA.create("second")
        controllerA.create("third")
        val removedId = idSequence[1]
        controllerA.remove(removedId)

        val storeB = newStore()
        val controllerB = ReminderController(storeB) { "unused" }
        val remaining = controllerB.reminders
        assertEquals(listOf(idSequence[0], idSequence[2]), remaining.map { it.id })
        assertEquals(listOf("first", "third"), remaining.map { it.text })
    }

    // ----------------------------------------------------------------
    // Load-time error cases (NWR1 path)
    // ----------------------------------------------------------------

    @Test
    fun P3_11_existing_empty_file_rejected_with_IllegalStateException() {
        val file = target()
        file.writeBytes(ByteArray(0))
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3_12_wrong_header_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("WRONG\nid-1\tSGVsbG8=\t0")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3_12b_unsupported_header_NWR4_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR4\nid-1\tSGVsbG8=\t0\t-")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3_13_blank_reminder_record_rejected_with_IllegalStateException() {
        val file = target()
        file.parentFile?.mkdirs()
        file.writeBytes(
            ("NWR1\nid-1\tSGVsbG8=\n\nid-2\tV29ybGQ=").toByteArray(Charsets.UTF_8),
        )
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3_14_record_without_TAB_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR1\nnot-a-record")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3_15_multiple_TAB_separators_attempted_TAB_id_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR1\nbad\tid\thidden")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3_16_empty_loaded_id_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR1\n\tSGVsbG8=")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3_17_loaded_id_containing_CR_rejected_with_IllegalStateException() {
        val file = target()
        val bytes = "NWR1\nbad\rid\tSGVsbG8=".toByteArray(Charsets.UTF_8)
        file.writeBytes(bytes)
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3_18_raw_LF_attempted_id_rejected_as_malformed_multiline_record() {
        val file = target()
        file.writeText("NWR1\nbad\nid\tSGVsbG8=")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3_19_invalid_Base64URL_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR1\nid-1\t!!!notbase64!!!")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3_20_Base64URL_decoding_to_invalid_UTF8_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR1\nid-1\t_w==")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3_21_duplicate_loaded_ids_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR1\nsame\taGVsbG8=\nsame\tZ29vZGJ5ZQ==")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3_22_valid_followed_by_malformed_rejects_complete_load_no_partial_result() {
        val file = target()
        file.writeText("NWR1\nvalid-id\tSGVsbG8=\nnot-a-record")
        val store = newStore()
        assertThrows(IllegalStateException::class.java) { store.load() }
    }

    @Test
    fun P3_23_trailing_LF_blank_final_record_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR1\nid-1\tSGVsbG8=\n")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    // ----------------------------------------------------------------
    // Save-time validation
    // ----------------------------------------------------------------

    @Test
    fun P3_24_save_rejects_empty_id_with_IllegalArgumentException() {
        val store = newStore()
        assertThrows(IllegalArgumentException::class.java) {
            store.save(listOf(Reminder("", "text")))
        }
    }

    @Test
    fun P3_25_save_rejects_TAB_containing_id_with_IllegalArgumentException() {
        val store = newStore()
        assertThrows(IllegalArgumentException::class.java) {
            store.save(listOf(Reminder("a\tb", "text")))
        }
    }

    @Test
    fun P3_26_save_rejects_CR_containing_id_with_IllegalArgumentException() {
        val store = newStore()
        assertThrows(IllegalArgumentException::class.java) {
            store.save(listOf(Reminder("a\rb", "text")))
        }
    }

    @Test
    fun P3_27_save_rejects_LF_containing_id_with_IllegalArgumentException() {
        val store = newStore()
        assertThrows(IllegalArgumentException::class.java) {
            store.save(listOf(Reminder("a\nb", "text")))
        }
    }

    @Test
    fun P3_28_save_rejects_duplicate_ids_with_IllegalArgumentException() {
        val store = newStore()
        assertThrows(IllegalArgumentException::class.java) {
            store.save(
                listOf(
                    Reminder("dup", "first"),
                    Reminder("dup", "second"),
                ),
            )
        }
    }

    @Test
    fun P3_29_save_validates_complete_list_before_writing_invalid_later_id_preserves_existing_file() {
        val store = newStore()
        val valid = listOf(
            Reminder("a", "alpha"),
            Reminder("b", "beta"),
        )
        store.save(valid)

        val beforeBytes = target().readBytes()
        val beforeText = target().readText(Charsets.UTF_8)

        val invalid = listOf(
            Reminder("a", "alpha"),
            Reminder("bad\tid", "bogus"),
        )
        assertThrows(IllegalArgumentException::class.java) {
            store.save(invalid)
        }

        val afterBytes = target().readBytes()
        assertArrayEquals(beforeBytes, afterBytes)
        assertEquals(beforeText, target().readText(Charsets.UTF_8))
    }

    // ----------------------------------------------------------------
    // Edit semantics with default done = false
    // ----------------------------------------------------------------

    @Test
    fun P3E_01_edit_persists_changed_text_across_reload() {
        val store = newStore()
        store.save(listOf(Reminder("edit-1", "original")))
        val controller = ReminderController(store) { "unused" }

        assertTrue(controller.edit("edit-1", "changed"))

        val reloaded = newStore().load()
        assertEquals(1, reloaded.size)
        assertEquals("edit-1", reloaded[0].id)
        assertEquals("changed", reloaded[0].text)
    }

    @Test
    fun P3E_02_edit_preserves_reminder_id_after_reload() {
        val store = newStore()
        store.save(
            listOf(
                Reminder("a", "first"),
                Reminder("b", "second"),
                Reminder("c", "third"),
            ),
        )
        val controller = ReminderController(store) { "unused" }

        assertTrue(controller.edit("b", "edited-second"))

        val reloaded = newStore().load()
        assertEquals(listOf("a", "b", "c"), reloaded.map { it.id })
        val edited = reloaded.first { it.text == "edited-second" }
        assertEquals("b", edited.id)
    }

    @Test
    fun P3E_03_edit_preserves_reminder_index_after_reload() {
        val store = newStore()
        store.save(
            listOf(
                Reminder("a", "first"),
                Reminder("b", "second"),
                Reminder("c", "third"),
            ),
        )
        val controller = ReminderController(store) { "unused" }

        assertTrue(controller.edit("b", "edited-second"))

        val reloaded = newStore().load()
        assertEquals(3, reloaded.size)
        assertEquals(1, reloaded.indexOfFirst { it.id == "b" })
    }

    @Test
    fun P3E_04_edit_leaves_neighbors_order_and_unrelated_content_unchanged() {
        val store = newStore()
        store.save(
            listOf(
                Reminder("a", "first"),
                Reminder("b", "second"),
                Reminder("c", "third"),
                Reminder("d", "fourth"),
            ),
        )
        val controller = ReminderController(store) { "unused" }

        assertTrue(controller.edit("b", "edited-second"))

        val reloaded = newStore().load()
        assertEquals(
            listOf(
                Reminder("a", "first"),
                Reminder("b", "edited-second"),
                Reminder("c", "third"),
                Reminder("d", "fourth"),
            ),
            reloaded,
        )
    }

    @Test
    fun P3E_05_new_controller_with_new_store_restores_edited_text() {
        val storeA = newStore()
        storeA.save(listOf(Reminder("restore-id", "before")))
        val controllerA = ReminderController(storeA) { "unused" }

        assertTrue(controllerA.edit("restore-id", "after"))

        val storeB = newStore()
        val controllerB = ReminderController(storeB) { "unused" }
        assertEquals(
            listOf(Reminder("restore-id", "after")),
            controllerB.reminders,
        )
    }

    // ----------------------------------------------------------------
    // Revised: NWR1 load → save → NWR3 lazy migration
    // ----------------------------------------------------------------

    @Test
    fun P3E_06_NWR1_load_edit_save_migrates_file_to_NWR3_and_reloads_with_default_done_false() {
        val file = target()
        file.writeText("NWR1\nfirst-id\tZmlyc3Q=\nsecond-id\tc2Vjb25k")

        val store = newStore()
        val controller = ReminderController(store) { "unused" }
        assertEquals(
            listOf(
                Reminder("first-id", "first"),
                Reminder("second-id", "second"),
            ),
            controller.reminders,
        )

        assertTrue(controller.edit("first-id", "edited-first"))

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR3", text.substringBefore('\n'))
        val lines = text.split("\n")
        assertEquals(3, lines.size)
        assertFalse(text.endsWith("\n"))

        val reloaded = newStore().load()
        assertEquals(
            listOf(
                Reminder("first-id", "edited-first"),
                Reminder("second-id", "second"),
            ),
            reloaded,
        )
    }

    @Test
    fun P3E_07_NWR1_first_save_migrates_header_to_NWR3() {
        val file = target()
        file.writeText("NWR1\nheader-id\tYmVmb3Jl")

        val store = newStore()
        val controller = ReminderController(store) { "unused" }

        assertTrue(controller.edit("header-id", "after"))

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR3", text.substringBefore('\n'))
    }

    @Test
    fun P3E_08_record_grammar_is_NWR3_three_TABs_with_done_literal_and_absent_time_after_save() {
        val file = target()
        file.writeText("NWR1\ngrammar-a\tYWxwaGE=\ngrammar-b\tYmV0YQ==")

        val store = newStore()
        val controller = ReminderController(store) { "unused" }

        assertTrue(controller.edit("grammar-a", "alpha-edited"))

        val text = target().readText(Charsets.UTF_8)
        val lines = text.split("\n")
        assertEquals("NWR3", lines[0])
        assertEquals(3, lines.size)
        assertFalse(text.endsWith("\n"))

        val expectedById = mapOf(
            "grammar-a" to "alpha-edited",
            "grammar-b" to "beta",
        )

        for (i in 1..2) {
            val record = lines[i]
            assertEquals(3, record.count { it == '\t' })
            val firstTab = record.indexOf('\t')
            val secondTab = record.indexOf('\t', firstTab + 1)
            val thirdTab = record.indexOf('\t', secondTab + 1)
            assertTrue(secondTab > firstTab)
            assertTrue(thirdTab > secondTab)
            val id = record.substring(0, firstTab)
            val encoded = record.substring(firstTab + 1, secondTab)
            val doneLiteral = record.substring(secondTab + 1, thirdTab)
            val timeLiteral = record.substring(thirdTab + 1)
            assertEquals("0", doneLiteral)
            assertEquals("-", timeLiteral)
            assertTrue("unexpected id: $id", expectedById.containsKey(id))
            assertFalse("TAB must not appear in encoded form", encoded.contains('\t'))
            assertFalse("CR must not appear in encoded form", encoded.contains('\r'))
            assertFalse("LF must not appear in encoded form", encoded.contains('\n'))
            val decodedBytes = Base64.getUrlDecoder().decode(encoded)
            val decodedText = decodedBytes.toString(Charsets.UTF_8)
            assertEquals(expectedById[id], decodedText)
        }
    }

    @Test
    fun P3E_10_NWR1_edit_save_migrates_to_NWR3_records_with_done_literal_zero_and_absent_time() {
        val file = target()
        file.writeText("NWR1\nmig-id1\tZmlyc3Q=\nmig-id2\tc2Vjb25k")

        val store = newStore()
        val controller = ReminderController(store) { "unused" }
        assertEquals(
            listOf(
                Reminder("mig-id1", "first"),
                Reminder("mig-id2", "second"),
            ),
            controller.reminders,
        )

        assertTrue(controller.edit("mig-id1", "edited-first"))

        val text = target().readText(Charsets.UTF_8)
        val lines = text.split("\n")
        assertEquals("NWR3", lines[0])
        assertEquals(3, lines.size)
        assertFalse(text.endsWith("\n"))

        for (i in 1..2) {
            val record = lines[i]
            assertEquals(3, record.count { it == '\t' })
            val firstTab = record.indexOf('\t')
            val secondTab = record.indexOf('\t', firstTab + 1)
            val thirdTab = record.indexOf('\t', secondTab + 1)
            assertTrue(firstTab > 0)
            assertTrue(secondTab > firstTab)
            assertTrue(thirdTab > secondTab)
            val encoded = record.substring(firstTab + 1, secondTab)
            val doneLiteral = record.substring(secondTab + 1, thirdTab)
            val timeLiteral = record.substring(thirdTab + 1)
            assertEquals("0", doneLiteral)
            assertEquals("-", timeLiteral)
            assertFalse(encoded.contains('\t'))
            assertFalse(encoded.contains('\r'))
            assertFalse(encoded.contains('\n'))
            // Must decode as valid Base64URL + UTF-8
            Base64.getUrlDecoder().decode(encoded)
        }

        val reloaded = newStore().load()
        assertEquals(
            listOf(
                Reminder("mig-id1", "edited-first"),
                Reminder("mig-id2", "second"),
            ),
            reloaded,
        )
    }

    @Test
    fun P3E_09_unicode_edited_text_round_trips_exactly() {
        val store = newStore()
        store.save(listOf(Reminder("unicode-edit", "before")))
        val controller = ReminderController(store) { "unused" }
        val unicodeText = "Héllo 👋 世界 — Ω∞ café 🌟"

        assertTrue(controller.edit("unicode-edit", unicodeText))

        val reloaded = newStore().load()
        assertEquals(1, reloaded.size)
        assertEquals("unicode-edit", reloaded[0].id)
        assertEquals(unicodeText, reloaded[0].text)
    }

    // ----------------------------------------------------------------
    // NWR2/NWR3 done-field round-trip and parser rejection
    // ----------------------------------------------------------------

    @Test
    fun P3NWR2_01_NWR3_write_emits_true_done_record_with_absent_time() {
        val store = newStore()
        val reminder = Reminder("id-1", "Hello", done = true)
        store.save(listOf(reminder))

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR3\nid-1\tSGVsbG8=\t1\t-", text)

        assertEquals(listOf(reminder), newStore().load())
    }

    @Test
    fun P3NWR2_02_mixed_false_true_NWR3_write_round_trip_preserves_exact_input_order() {
        val store = newStore()
        val reminders = listOf(
            Reminder("a", "Hello", done = false),
            Reminder("b", "World", done = true),
            Reminder("c", "first", done = false),
            Reminder("d", "second", done = true),
        )
        store.save(reminders)

        val text = target().readText(Charsets.UTF_8)
        assertEquals(
            "NWR3\na\tSGVsbG8=\t0\t-\nb\tV29ybGQ=\t1\t-\nc\tZmlyc3Q=\t0\t-\nd\tc2Vjb25k\t1\t-",
            text,
        )

        val reloaded = newStore().load()
        assertEquals(reminders, reloaded)
    }

    @Test
    fun P3NWR2_03_legacy_NWR1_load_assigns_done_false_to_every_reminder() {
        val file = target()
        file.writeText("NWR1\nfirst-id\tZmlyc3Q=\nsecond-id\tc2Vjb25k")

        val loaded = newStore().load()
        assertEquals(
            listOf(
                Reminder("first-id", "first", done = false),
                Reminder("second-id", "second", done = false),
            ),
            loaded,
        )
    }

    @Test
    fun P3NWR2_04_NWR1_load_only_does_not_rewrite_file_bytes() {
        val file = target()
        file.writeText("NWR1\nfirst-id\tZmlyc3Q=\nsecond-id\tc2Vjb25k")
        val beforeBytes = file.readBytes()

        val loaded = newStore().load()
        assertEquals(2, loaded.size)

        val afterBytes = file.readBytes()
        assertArrayEquals(beforeBytes, afterBytes)
        assertEquals("NWR1", file.readText(Charsets.UTF_8).substringBefore('\n'))
    }

    @Test
    fun P3NWR2_05_NWR1_setDone_false_to_true_migrates_to_NWR3_with_done_true_on_reload() {
        val file = target()
        file.writeText("NWR1\nx\tWQ==\ny\tWQ==")

        val store = newStore()
        val controller = ReminderController(store) { "unused" }
        assertEquals(
            listOf(
                Reminder("x", "Y", done = false),
                Reminder("y", "Y", done = false),
            ),
            controller.reminders,
        )

        assertTrue(controller.setDone("x", true))

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR3", text.substringBefore('\n'))

        val storeB = newStore()
        val controllerB = ReminderController(storeB) { "unused" }
        val reloaded = controllerB.reminders
        assertEquals(2, reloaded.size)
        assertEquals(0, reloaded.indexOfFirst { it.id == "x" })
        assertEquals(1, reloaded.indexOfFirst { it.id == "y" })
        assertEquals("Y", reloaded[0].text)
        assertEquals("Y", reloaded[1].text)
        assertEquals(
            listOf(
                Reminder("x", "Y", done = true),
                Reminder("y", "Y", done = false),
            ),
            reloaded,
        )
    }

    @Test
    fun P3NWR2_06_persisted_NWR2_true_to_false_round_trip_real_controller_reload() {
        val file = target()
        file.writeText("NWR2\na\tSGVsbG8=\t1\nb\tV29ybGQ=\t0")

        val reminders = listOf(
            Reminder("a", "Hello", done = true),
            Reminder("b", "World", done = false),
        )

        val controller = ReminderController(newStore()) { "unused" }
        val loaded = controller.reminders
        assertEquals(reminders, loaded)

        assertTrue(controller.setDone("a", false))

        val reloadedController = ReminderController(newStore()) { "unused" }
        assertEquals(
            listOf(
                Reminder("a", "Hello", done = false),
                Reminder("b", "World", done = false),
            ),
            reloadedController.reminders,
        )
    }

    @Test
    fun P3NWR2_07_edit_persisted_NWR2_done_true_changes_text_but_done_remains_true() {
        val file = target()
        file.writeText("NWR2\nedit-true\tYmVmb3Jl\t1")

        val controller = ReminderController(newStore()) { "unused" }
        assertEquals(
            listOf(Reminder("edit-true", "before", done = true)),
            controller.reminders,
        )

        assertTrue(controller.edit("edit-true", "after"))

        val reloadedController = ReminderController(newStore()) { "unused" }
        assertEquals(
            listOf(Reminder("edit-true", "after", done = true)),
            reloadedController.reminders,
        )
    }

    @Test
    fun P3NWR2_08_NWR1_changed_edit_migrates_file_to_NWR3_with_correct_records() {
        val file = target()
        file.writeText("NWR1\nmig-id1\tZmlyc3Q=\nmig-id2\tc2Vjb25k")

        val store = newStore()
        val controller = ReminderController(store) { "unused" }
        assertTrue(controller.edit("mig-id1", "edited-first"))

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR3", text.substringBefore('\n'))
        assertEquals(
            "NWR3\nmig-id1\tZWRpdGVkLWZpcnN0\t0\t-\nmig-id2\tc2Vjb25k\t0\t-",
            text,
        )

        val reloadedController = ReminderController(newStore()) { "unused" }
        assertEquals(
            listOf(
                Reminder("mig-id1", "edited-first"),
                Reminder("mig-id2", "second"),
            ),
            reloadedController.reminders,
        )
    }

    @Test
    fun P3NWR2_09_NWR1_create_migrates_file_to_NWR3_with_normal_idGenerator_use() {
        val file = target()
        file.writeText("NWR1\nexisting-id\tZXhpc3Rpbmc=")

        val store = newStore()
        val generatedIds = ArrayList<String>()
        var counter = 0
        val controller = ReminderController(
            store,
            idGenerator = {
                counter += 1
                val id = "gen-$counter"
                generatedIds.add(id)
                id
            },
        )

        controller.create("new-text")

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR3", text.substringBefore('\n'))
        assertEquals(3, text.split("\n").size)
        assertFalse(text.endsWith("\n"))

        val reloadedController = ReminderController(newStore()) { "unused" }
        assertEquals(2, reloadedController.reminders.size)
        assertEquals("existing-id", reloadedController.reminders[0].id)
        assertEquals("existing", reloadedController.reminders[0].text)
        assertEquals(generatedIds[0], reloadedController.reminders[1].id)
        assertEquals("new-text", reloadedController.reminders[1].text)
    }

    @Test
    fun P3NWR2_10_NWR1_remove_migrates_file_to_NWR3() {
        val file = target()
        file.writeText("NWR1\nkeep-id\tZmlyc3Q=\nremove-id\tc2Vjb25k\nextra-id\tdGhpcmQ=")

        val store = newStore()
        val controller = ReminderController(store) { "unused" }
        controller.remove("remove-id")

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR3", text.substringBefore('\n'))
        assertEquals(
            "NWR3\nkeep-id\tZmlyc3Q=\t0\t-\nextra-id\tdGhpcmQ=\t0\t-",
            text,
        )

        val reloadedController = ReminderController(newStore()) { "unused" }
        assertEquals(
            listOf(
                Reminder("keep-id", "first"),
                Reminder("extra-id", "third"),
            ),
            reloadedController.reminders,
        )
    }

    @Test
    fun P3NWR2_11_NWR1_same_state_setDone_returns_true_and_does_not_change_file_bytes() {
        val file = target()
        file.writeText("NWR1\nx\tWQ==")
        val beforeBytes = file.readBytes()

        val controller = ReminderController(newStore()) { "unused" }
        assertEquals(
            listOf(Reminder("x", "Y", done = false)),
            controller.reminders,
        )

        assertTrue(controller.setDone("x", false))

        val afterBytes = file.readBytes()
        assertArrayEquals(beforeBytes, afterBytes)
        assertEquals("NWR1", file.readText(Charsets.UTF_8).substringBefore('\n'))
    }

    @Test
    fun P3NWR2_12_NWR1_normalized_identical_edit_returns_true_and_does_not_change_file_bytes() {
        val file = target()
        file.writeText("NWR1\nx\tWQ==")
        val beforeBytes = file.readBytes()

        val controller = ReminderController(newStore()) { "unused" }
        assertEquals(
            listOf(Reminder("x", "Y", done = false)),
            controller.reminders,
        )

        assertTrue(controller.edit("x", "Y"))

        val afterBytes = file.readBytes()
        assertArrayEquals(beforeBytes, afterBytes)
        assertEquals("NWR1", file.readText(Charsets.UTF_8).substringBefore('\n'))
    }

    // ----------------------------------------------------------------
    // NWR2 parser rejections
    // ----------------------------------------------------------------

    @Test
    fun P3NWR2_REJECTS_a_invalid_done_literal_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR2\nid-1\tSGVsbG8=\tX")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3NWR2_REJECTS_b_missing_done_field_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR2\nid-1\tSGVsbG8=")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3NWR2_REJECTS_c_extra_field_extra_TAB_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR2\nid-1\tSGVsbG8=\t1\textra")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3NWR2_REJECTS_d_invalid_Base64URL_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR2\nid-1\t!!!notbase64!!!\t1")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3NWR2_REJECTS_e_decoded_invalid_UTF8_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR2\nid-1\t_w==\t1")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3NWR2_REJECTS_f_duplicate_ids_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR2\nsame\taGVsbG8=\t1\nsame\tZ29vZGJ5ZQ==\t0")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3NWR2_REJECTS_g_blank_record_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR2\nid-1\tSGVsbG8=\t1\n\nid-2\tV29ybGQ=\t0")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3NWR2_REJECTS_h_trailing_LF_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR2\nid-1\tSGVsbG8=\t1\n")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    // ----------------------------------------------------------------
    // NWR3 initial proof
    // ----------------------------------------------------------------

    @Test
    fun P3NWR3_A01_NWR3_header_only_file_loads_empty_list() {
        val file = target()
        file.writeText("NWR3")
        assertEquals(emptyList<Reminder>(), newStore().load())
    }

    @Test
    fun P3NWR3_A02_explicit_NWR3_fixture_loads_present_and_absent_times_with_both_done_states() {
        val file = target()
        file.writeText(
            "NWR3\nt-1\tSGVsbG8=\t1\t2024-01-02T03:04\nt-2\tV29ybGQ=\t0\t-",
        )

        val loaded = newStore().load()
        assertEquals(2, loaded.size)
        assertEquals("t-1", loaded[0].id)
        assertEquals("Hello", loaded[0].text)
        assertTrue(loaded[0].done)
        assertEquals(java.time.LocalDateTime.of(2024, 1, 2, 3, 4), loaded[0].time)
        assertEquals("t-2", loaded[1].id)
        assertEquals("World", loaded[1].text)
        assertFalse(loaded[1].done)
        assertEquals(null, loaded[1].time)
    }

    @Test
    fun P3NWR3_A03_explicit_NWR2_fixture_loads_stored_done_values_with_null_time_without_rewriting_bytes() {
        val file = target()
        file.writeText("NWR2\nn-1\tSGVsbG8=\t1\nn-2\tV29ybGQ=\t0")
        val beforeBytes = file.readBytes()

        val loaded = newStore().load()
        assertEquals(2, loaded.size)
        assertEquals("n-1", loaded[0].id)
        assertTrue(loaded[0].done)
        assertEquals(null, loaded[0].time)
        assertEquals("n-2", loaded[1].id)
        assertFalse(loaded[1].done)
        assertEquals(null, loaded[1].time)

        assertArrayEquals(beforeBytes, file.readBytes())
        assertEquals("NWR2", file.readText(Charsets.UTF_8).substringBefore('\n'))
    }

    @Test
    fun P3NWR3_A04_NWR2_setTime_null_noop_preserves_original_file_bytes_and_header() {
        val file = target()
        file.writeText("NWR2\nn-1\tSGVsbG8=\t1\nn-2\tV29ybGQ=\t0")
        val beforeBytes = file.readBytes()

        val controller = ReminderController(newStore()) { "unused" }
        assertEquals(2, controller.reminders.size)

        assertTrue(controller.setTime("n-1", null))

        assertArrayEquals(beforeBytes, file.readBytes())
        assertEquals("NWR2", file.readText(Charsets.UTF_8).substringBefore('\n'))
    }

    @Test
    fun P3NWR3_A05_NWR1_setTime_null_noop_preserves_original_file_bytes_and_header() {
        val file = target()
        file.writeText("NWR1\nn-1\tSGVsbG8=\nn-2\tV29ybGQ=")
        val beforeBytes = file.readBytes()

        val controller = ReminderController(newStore()) { "unused" }
        assertEquals(2, controller.reminders.size)

        assertTrue(controller.setTime("n-1", null))

        assertArrayEquals(beforeBytes, file.readBytes())
        assertEquals("NWR1", file.readText(Charsets.UTF_8).substringBefore('\n'))
    }

    @Test
    fun P3NWR3_A06_effective_setTime_on_legacy_NWR2_migrates_to_NWR3_preserving_other_fields_and_order() {
        val file = target()
        file.writeText("NWR2\ns-1\tSGVsbG8=\t1\ns-2\tV29ybGQ=\t0")

        val controller = ReminderController(newStore()) { "unused" }
        assertTrue(controller.setTime("s-1", java.time.LocalDateTime.of(2024, 3, 4, 5, 6)))

        val text = file.readText(Charsets.UTF_8)
        assertEquals("NWR3", text.substringBefore('\n'))
        assertEquals(
            "NWR3\ns-1\tSGVsbG8=\t1\t2024-03-04T05:06\ns-2\tV29ybGQ=\t0\t-",
            text,
        )
        assertFalse(text.endsWith("\n"))

        val reloaded = newStore().load()
        assertEquals(2, reloaded.size)
        assertEquals("s-1", reloaded[0].id)
        assertEquals("Hello", reloaded[0].text)
        assertTrue(reloaded[0].done)
        assertEquals(java.time.LocalDateTime.of(2024, 3, 4, 5, 6), reloaded[0].time)
        assertEquals("s-2", reloaded[1].id)
        assertEquals("World", reloaded[1].text)
        assertFalse(reloaded[1].done)
        assertEquals(null, reloaded[1].time)
    }

    @Test
    fun P3NWR3_A07_malformed_NWR3_records_rejected_with_IllegalStateException() {
        val file = target()

        // Missing time-field TAB separator.
        file.writeText("NWR3\nm-1\tSGVsbG8=\t0")
        assertThrows(IllegalStateException::class.java) { newStore().load() }

        // Extra TAB separator.
        file.writeText("NWR3\nm-1\tSGVsbG8=\t0\t-\textra")
        assertThrows(IllegalStateException::class.java) { newStore().load() }

        // Impossible calendar date.
        file.writeText("NWR3\nm-1\tSGVsbG8=\t0\t2024-02-30T10:00")
        assertThrows(IllegalStateException::class.java) { newStore().load() }

        // Non-zero seconds.
        file.writeText("NWR3\nm-1\tSGVsbG8=\t0\t2024-01-01T10:00:30")
        assertThrows(IllegalStateException::class.java) { newStore().load() }

        // UTC offset instead of a local wall-clock time.
        file.writeText("NWR3\nm-1\tSGVsbG8=\t0\t2024-01-01T10:00+01:00")
        assertThrows(IllegalStateException::class.java) { newStore().load() }

        // Unsigned five-digit year: rejected during strict parsing, before
        // reaching the canonical re-serialization comparison.
        file.writeText("NWR3\nm-1\tSGVsbG8=\t0\t02024-01-01T10:00")
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3NWR3_A08_save_with_invalid_later_time_raises_IllegalArgumentException_and_preserves_previous_bytes() {
        val store = newStore()
        store.save(
            listOf(
                Reminder("s-1", "Hello"),
                Reminder("s-2", "World"),
            ),
        )
        val beforeBytes = target().readBytes()
        val beforeText = target().readText(Charsets.UTF_8)

        assertThrows(IllegalArgumentException::class.java) {
            store.save(
                listOf(
                    Reminder("s-1", "Hello"),
                    Reminder(
                        "s-2",
                        "World",
                        time = java.time.LocalDateTime.of(2024, 1, 1, 10, 0, 30),
                    ),
                ),
            )
        }

        assertArrayEquals(beforeBytes, target().readBytes())
        assertEquals(beforeText, target().readText(Charsets.UTF_8))

        assertThrows(IllegalArgumentException::class.java) {
            store.save(
                listOf(
                    Reminder("s-1", "Hello"),
                    Reminder(
                        "s-2",
                        "World",
                        time = java.time.LocalDateTime.of(0, 1, 1, 10, 0),
                    ),
                ),
            )
        }

        assertArrayEquals(beforeBytes, target().readBytes())
        assertEquals(beforeText, target().readText(Charsets.UTF_8))
    }

    // ----------------------------------------------------------------
    // Build B: deterministic NWR3 persistence proof
    // ----------------------------------------------------------------

    @Test
    fun P3NWR3_B01_present_time_writes_exact_canonical_NWR3_bytes() {
        val reminder = Reminder("id-1", "Hello", time = LocalDateTime.of(2024, 1, 31, 8, 30))
        newStore().save(listOf(reminder))
        val expected = "NWR3\nid-1\tSGVsbG8=\t0\t2024-01-31T08:30"
        assertArrayEquals(expected.toByteArray(Charsets.UTF_8), target().readBytes())
        assertEquals(listOf(reminder), newStore().load())
    }

    @Test
    fun P3NWR3_B02_mixed_times_and_done_states_round_trip_in_original_order() {
        val reminders = listOf(
            Reminder("a", "Hello", done = false, time = LocalDateTime.of(2024, 1, 2, 3, 4)),
            Reminder("b", "World", done = true, time = null),
            Reminder("c", "first", done = true, time = LocalDateTime.of(2024, 12, 31, 23, 59)),
            Reminder("d", "second", done = false, time = null),
        )
        newStore().save(reminders)
        val expected = "NWR3\na\tSGVsbG8=\t0\t2024-01-02T03:04\n" +
            "b\tV29ybGQ=\t1\t-\n" +
            "c\tZmlyc3Q=\t1\t2024-12-31T23:59\n" +
            "d\tc2Vjb25k\t0\t-"
        assertArrayEquals(expected.toByteArray(Charsets.UTF_8), target().readBytes())
        val loaded = newStore().load()
        assertEquals(reminders, loaded)
        assertEquals(listOf("a", "b", "c", "d"), loaded.map { it.id })
    }

    @Test
    fun P3NWR3_B03_repeated_identical_save_is_byte_identical() {
        val reminders = listOf(
            Reminder("a", "Hello", time = LocalDateTime.of(2024, 1, 2, 3, 4)),
            Reminder("b", "World", done = true),
        )
        newStore().save(reminders)
        val original = target().readBytes()
        newStore().save(reminders)
        assertArrayEquals(original, target().readBytes())
        assertEquals(reminders, newStore().load())
    }

    @Test
    fun P3NWR3_B04_set_change_clear_time_survive_controller_restarts() {
        newStore().save(listOf(Reminder("t-1", "Hello")))
        val first = LocalDateTime.of(2024, 1, 31, 8, 30)
        val second = LocalDateTime.of(2025, 2, 1, 9, 15)

        assertTrue(ReminderController(newStore()) { "unused" }.setTime("t-1", first))
        assertEquals(
            listOf(Reminder("t-1", "Hello", time = first)),
            ReminderController(newStore()) { "unused" }.reminders,
        )
        assertEquals("NWR3\nt-1\tSGVsbG8=\t0\t2024-01-31T08:30", target().readText(Charsets.UTF_8))

        assertTrue(ReminderController(newStore()) { "unused" }.setTime("t-1", second))
        assertEquals(
            listOf(Reminder("t-1", "Hello", time = second)),
            ReminderController(newStore()) { "unused" }.reminders,
        )
        assertEquals("NWR3\nt-1\tSGVsbG8=\t0\t2025-02-01T09:15", target().readText(Charsets.UTF_8))

        assertTrue(ReminderController(newStore()) { "unused" }.setTime("t-1", null))
        assertEquals(
            listOf(Reminder("t-1", "Hello")),
            ReminderController(newStore()) { "unused" }.reminders,
        )
        assertEquals("NWR3\nt-1\tSGVsbG8=\t0\t-", target().readText(Charsets.UTF_8))
    }

    @Test
    fun P3NWR3_B05_change_time_preserves_all_other_fields_and_neighbor_positions() {
        val first = Reminder("a", "first", done = false, time = LocalDateTime.of(2024, 1, 1, 10, 0))
        val middle = Reminder("b", "second", done = true)
        val last = Reminder("c", "third", done = false, time = LocalDateTime.of(2024, 1, 3, 10, 0))
        newStore().save(listOf(first, middle, last))
        val updatedTime = LocalDateTime.of(2024, 2, 2, 11, 11)
        assertTrue(ReminderController(newStore()) { "unused" }.setTime("b", updatedTime))
        val loaded = ReminderController(newStore()) { "unused" }.reminders
        assertEquals(listOf(first, middle.copy(time = updatedTime), last), loaded)
        assertEquals(listOf("a", "b", "c"), loaded.map { it.id })
        assertEquals(listOf("first", "second", "third"), loaded.map { it.text })
        assertEquals(listOf(false, true, false), loaded.map { it.done })
        assertEquals(0, loaded.indexOfFirst { it.id == "a" })
        assertEquals(1, loaded.indexOfFirst { it.id == "b" })
        assertEquals(2, loaded.indexOfFirst { it.id == "c" })
    }

    @Test
    fun P3NWR3_B06_unicode_text_with_time_round_trips_and_is_encoded_correctly() {
        val text = "Héllo 👋 世界 — Ω∞"
        val reminder = Reminder("u-1", text, time = LocalDateTime.of(2024, 5, 6, 7, 8))
        newStore().save(listOf(reminder))
        val fields = target().readText(Charsets.UTF_8).substringAfter('\n').split("\t")
        assertEquals(4, fields.size)
        assertEquals("u-1", fields[0])
        assertArrayEquals(text.toByteArray(Charsets.UTF_8), Base64.getUrlDecoder().decode(fields[1]))
        assertEquals("0", fields[2])
        assertEquals("2024-05-06T07:08", fields[3])
        assertEquals(listOf(reminder), newStore().load())
    }

    @Test
    fun P3NWR3_B07_same_non_null_time_is_a_byte_preserving_noop() {
        val time = LocalDateTime.of(2024, 1, 31, 8, 30)
        newStore().save(listOf(Reminder("t-1", "Hello", time = time)))
        val before = target().readBytes()
        assertTrue(ReminderController(newStore()) { "unused" }.setTime("t-1", time))
        assertArrayEquals(before, target().readBytes())
    }

    @Test
    fun P3NWR3_B08_same_done_value_is_a_byte_preserving_NWR3_noop() {
        newStore().save(listOf(Reminder("d-1", "Hello", done = true, time = LocalDateTime.of(2024, 1, 31, 8, 30))))
        val before = target().readBytes()
        assertTrue(ReminderController(newStore()) { "unused" }.setDone("d-1", true))
        assertArrayEquals(before, target().readBytes())
    }

    @Test
    fun P3NWR3_B09_identical_edit_is_a_byte_preserving_NWR3_noop() {
        newStore().save(listOf(Reminder("e-1", "Hello", time = LocalDateTime.of(2024, 1, 31, 8, 30))))
        val before = target().readBytes()
        assertTrue(ReminderController(newStore()) { "unused" }.edit("e-1", "Hello"))
        assertArrayEquals(before, target().readBytes())
    }

    @Test
    fun P3NWR3_B10_effective_NWR1_setTime_migrates_same_file_to_NWR3() {
        val file = target()
        file.writeText("NWR1\nfirst-id\tZmlyc3Q=\nsecond-id\tc2Vjb25k", Charsets.UTF_8)
        val before = file.readBytes()
        val time = LocalDateTime.of(2024, 7, 8, 9, 10)
        assertTrue(ReminderController(newStore()) { "unused" }.setTime("first-id", time))
        val expected = "NWR3\nfirst-id\tZmlyc3Q=\t0\t2024-07-08T09:10\nsecond-id\tc2Vjb25k\t0\t-"
        assertArrayEquals(expected.toByteArray(Charsets.UTF_8), file.readBytes())
        assertFalse("migration must change the original bytes", before.contentEquals(file.readBytes()))
        assertEquals(
            listOf(Reminder("first-id", "first", time = time), Reminder("second-id", "second")),
            newStore().load(),
        )
    }

    @Test
    fun P3NWR3_B11_NWR2_effective_change_migrates_preserving_other_done_values_and_order() {
        val file = target()
        file.writeText("NWR2\na\tSGVsbG8=\t1\nb\tV29ybGQ=\t0\nc\tZmlyc3Q=\t0", Charsets.UTF_8)
        assertTrue(ReminderController(newStore()) { "unused" }.setDone("b", true))
        val expected = "NWR3\na\tSGVsbG8=\t1\t-\nb\tV29ybGQ=\t1\t-\nc\tZmlyc3Q=\t0\t-"
        assertEquals(expected, file.readText(Charsets.UTF_8))
        assertEquals(
            listOf(
                Reminder("a", "Hello", done = true),
                Reminder("b", "World", done = true),
                Reminder("c", "first", done = false),
            ),
            newStore().load(),
        )
    }

    @Test
    fun P3NWR3_B12_all_legacy_noops_preserve_bytes_without_migration() {
        val file = target()
        file.writeText("NWR1\nx\tWQ==", Charsets.UTF_8)
        val nwr1Before = file.readBytes()
        val nwr1 = ReminderController(newStore()) { "unused" }
        assertTrue(nwr1.setTime("x", null))
        assertArrayEquals(nwr1Before, file.readBytes())
        assertTrue(nwr1.setDone("x", false))
        assertArrayEquals(nwr1Before, file.readBytes())
        assertTrue(nwr1.edit("x", "Y"))
        assertArrayEquals(nwr1Before, file.readBytes())
        assertEquals("NWR1", file.readText(Charsets.UTF_8).substringBefore('\n'))

        file.writeText("NWR2\nx\tWQ==\t1", Charsets.UTF_8)
        val nwr2Before = file.readBytes()
        val nwr2 = ReminderController(newStore()) { "unused" }
        assertTrue(nwr2.setTime("x", null))
        assertArrayEquals(nwr2Before, file.readBytes())
        assertTrue(nwr2.setDone("x", true))
        assertArrayEquals(nwr2Before, file.readBytes())
        assertTrue(nwr2.edit("x", "Y"))
        assertArrayEquals(nwr2Before, file.readBytes())
        assertEquals("NWR2", file.readText(Charsets.UTF_8).substringBefore('\n'))
    }

    @Test
    fun P3NWR3_B13_year_0001_loads_and_round_trips_exactly() {
        val expected = "NWR3\nmin-year\tSGVsbG8=\t0\t0001-01-01T00:00"
        target().writeText(expected, Charsets.UTF_8)
        val loaded = newStore().load()
        assertEquals(listOf(Reminder("min-year", "Hello", time = LocalDateTime.of(1, 1, 1, 0, 0))), loaded)
        newStore().save(loaded)
        assertArrayEquals(expected.toByteArray(Charsets.UTF_8), target().readBytes())
        assertEquals(loaded, newStore().load())
    }

    @Test
    fun P3NWR3_B14_year_9999_loads_and_round_trips_exactly() {
        val expected = "NWR3\nmax-year\tV29ybGQ=\t1\t9999-12-31T23:59"
        target().writeText(expected, Charsets.UTF_8)
        val loaded = newStore().load()
        assertEquals(
            listOf(Reminder("max-year", "World", done = true, time = LocalDateTime.of(9999, 12, 31, 23, 59))),
            loaded,
        )
        newStore().save(loaded)
        assertArrayEquals(expected.toByteArray(Charsets.UTF_8), target().readBytes())
        assertEquals(loaded, newStore().load())
    }

    @Test
    fun P3NWR3_B15_valid_leap_day_is_accepted_and_round_trips() {
        val expected = "NWR3\nleap\tSGVsbG8=\t0\t2024-02-29T09:30"
        target().writeText(expected, Charsets.UTF_8)
        val loaded = newStore().load()
        assertEquals(
            listOf(Reminder("leap", "Hello", time = LocalDateTime.of(2024, 2, 29, 9, 30))),
            loaded,
        )
        newStore().save(loaded)
        assertArrayEquals(expected.toByteArray(Charsets.UTF_8), target().readBytes())
    }

    @Test
    fun P3NWR3_B16_malformed_date_spellings_are_rejected() {
        assertInvalidNwr3Time("missing time", "2024-01-01")
        assertInvalidNwr3Time("single-digit month", "2024-1-01T10:00")
        assertInvalidNwr3Time("wrong date-time separator", "2024-01-01 10:00")
        assertInvalidNwr3Time("nonsense", "not-a-date")
        assertInvalidNwr3Time("trailing garbage", "2024-01-01T10:00extra")
        assertInvalidNwr3Time("unsigned over-padded year", "02024-01-01T10:00")
    }

    @Test
    fun P3NWR3_B17_sign_prefixed_year_proves_canonical_parse_serialize_gate() {
        val formatter = DateTimeFormatter.ofPattern("uuuu-MM-dd'T'HH:mm")
            .withResolverStyle(ResolverStyle.STRICT)
        val literal = "+02024-01-01T10:00"
        val parsed = LocalDateTime.parse(literal, formatter)
        assertEquals(LocalDateTime.of(2024, 1, 1, 10, 0), parsed)
        val canonical = formatter.format(parsed)
        assertEquals("2024-01-01T10:00", canonical)
        assertNotEquals(literal, canonical)
        assertInvalidNwr3Time("parseable but non-canonical year", literal)
    }

    @Test
    fun P3NWR3_B18_empty_missing_and_extra_NWR3_fields_are_rejected() {
        assertInvalidNwr3Wire("empty fourth field", "NWR3\nf-1\tSGVsbG8=\t0\t")
        assertInvalidNwr3Wire("missing time TAB", "NWR3\nf-2\tSGVsbG8=\t0")
        assertInvalidNwr3Wire("missing done TAB", "NWR3\nf-3\tSGVsbG8=")
        assertInvalidNwr3Wire("extra TAB", "NWR3\nf-4\tSGVsbG8=\t0\t-\textra")
    }

    @Test
    fun P3NWR3_B19_invalid_NWR3_done_literals_are_rejected() {
        assertInvalidNwr3Wire("done 2", "NWR3\nd-2\tSGVsbG8=\t2\t-")
        assertInvalidNwr3Wire("done -1", "NWR3\nd-neg\tSGVsbG8=\t-1\t-")
        assertInvalidNwr3Wire("done x", "NWR3\nd-x\tSGVsbG8=\tx\t-")
        assertInvalidNwr3Wire("done true", "NWR3\nd-word\tSGVsbG8=\ttrue\t-")
        assertInvalidNwr3Wire("empty done", "NWR3\td-empty\tSGVsbG8=\t\t-")
    }

    @Test
    fun P3NWR3_B20_invalid_calendar_values_are_rejected() {
        assertInvalidNwr3Time("non-leap February 29", "2023-02-29T10:00")
        assertInvalidNwr3Time("February 30", "2024-02-30T10:00")
        assertInvalidNwr3Time("month 13", "2024-13-01T10:00")
        assertInvalidNwr3Time("hour 24", "2024-01-01T24:00")
        assertInvalidNwr3Time("minute 60", "2024-01-01T10:60")
    }

    @Test
    fun P3NWR3_B21_seconds_fraction_offset_and_zone_suffixes_are_rejected() {
        assertInvalidNwr3Time("seconds", "2024-01-01T10:00:30")
        assertInvalidNwr3Time("fractional seconds", "2024-01-01T10:00:30.500")
        assertInvalidNwr3Time("UTC offset", "2024-01-01T10:00+01:00")
        assertInvalidNwr3Time("Z suffix", "2024-01-01T10:00Z")
        assertInvalidNwr3Time("named zone", "2024-01-01T10:00[Europe/Madrid]")
    }

    @Test
    fun P3NWR3_B22_year_zero_and_above_9999_are_rejected() {
        assertInvalidNwr3Time("year zero", "0000-01-01T10:00")
        assertInvalidNwr3Time("unsigned year 10000", "10000-01-01T10:00")
        assertInvalidNwr3Time("signed year 10000", "+010000-01-01T10:00")
    }

    @Test
    fun P3NWR3_B23_duplicate_ids_blank_records_trailing_LF_and_empty_file_are_rejected() {
        assertInvalidNwr3Wire(
            "duplicate IDs",
            "NWR3\nsame\tSGVsbG8=\t0\t-\nsame\tV29ybGQ=\t1\t-",
        )
        assertInvalidNwr3Wire(
            "blank record",
            "NWR3\nb-1\tSGVsbG8=\t0\t-\n\nb-2\tV29ybGQ=\t1\t-",
        )
        assertInvalidNwr3Wire("trailing LF", "NWR3\nt-1\tSGVsbG8=\t0\t-\n")
        assertInvalidNwr3Wire("empty file", "")
    }

    @Test
    fun P3NWR3_B24_invalid_base64_utf8_and_ids_are_rejected() {
        assertInvalidNwr3Wire("invalid Base64URL", "NWR3\nb64\t!!!notbase64!!!\t0\t-")
        assertInvalidNwr3Wire("invalid decoded UTF-8", "NWR3\nutf8\t_w==\t0\t-")
        assertInvalidNwr3Wire("empty ID", "NWR3\n\tSGVsbG8=\t0\t-")
        assertInvalidNwr3Wire("CR within ID", "NWR3\nbad\rid\tSGVsbG8=\t0\t-")
        assertInvalidNwr3Wire("TAB within apparent ID", "NWR3\nbad\tid\tSGVsbG8=\t0\t-")
    }

    @Test
    fun P3NWR3_B25_malformed_record_in_either_position_rejects_entire_load() {
        assertInvalidNwr3Wire(
            "valid then malformed must not return partial list",
            "NWR3\nvalid\tSGVsbG8=\t0\t-\nnot-a-record",
        )
        assertInvalidNwr3Wire(
            "malformed then valid must not return partial list",
            "NWR3\nnot-a-record\nvalid\tSGVsbG8=\t0\t-",
        )
    }

    @Test
    fun P3NWR3_B26_direct_save_rejects_nonzero_nanoseconds() {
        assertThrows(IllegalArgumentException::class.java) {
            newStore().save(listOf(Reminder("n-1", "Hello", time = LocalDateTime.of(2024, 1, 1, 10, 0, 0, 1))))
        }
    }

    @Test
    fun P3NWR3_B27_direct_save_rejects_year_10000() {
        assertThrows(IllegalArgumentException::class.java) {
            newStore().save(listOf(Reminder("y-1", "Hello", time = LocalDateTime.of(10000, 1, 1, 10, 0))))
        }
    }

    @Test
    fun P3NWR3_B28_invalid_later_reminder_cannot_partially_overwrite_file() {
        val initial = listOf(Reminder("a", "alpha", time = LocalDateTime.of(2024, 1, 1, 10, 0)))
        newStore().save(initial)
        val before = target().readBytes()
        assertThrows(IllegalArgumentException::class.java) {
            newStore().save(
                listOf(
                    Reminder("a", "alpha changed", time = LocalDateTime.of(2024, 1, 1, 10, 0)),
                    Reminder("b", "beta", time = LocalDateTime.of(2024, 1, 1, 10, 0, 0, 1)),
                ),
            )
        }
        assertArrayEquals(before, target().readBytes())
        assertEquals(initial, newStore().load())
    }

    @Test
    fun P3NWR3_B29_rejected_save_preserves_valid_NWR3_bytes_and_reload_values() {
        val initial = listOf(
            Reminder("a", "alpha", time = LocalDateTime.of(2024, 1, 1, 10, 0)),
            Reminder("b", "beta", done = true),
        )
        newStore().save(initial)
        val before = target().readBytes()
        assertThrows(IllegalArgumentException::class.java) {
            newStore().save(
                listOf(
                    initial[0],
                    Reminder("b", "beta", done = true, time = LocalDateTime.of(10000, 1, 1, 10, 0)),
                ),
            )
        }
        assertArrayEquals(before, target().readBytes())
        assertEquals(initial, newStore().load())
    }

    @Test
    fun P3NWR3_B30_rejected_save_does_not_create_absent_file() {
        assertFalse(target().exists())
        assertThrows(IllegalArgumentException::class.java) {
            newStore().save(listOf(Reminder("n-1", "Hello", time = LocalDateTime.of(2024, 1, 1, 10, 0, 0, 1))))
        }
        assertFalse(target().exists())
    }

    @Test
    fun P3NWR3_B31_rejected_save_preserves_original_NWR2_bytes_without_migration() {
        val original = "NWR2\nlegacy-id\tSGVsbG8=\t1"
        target().writeText(original, Charsets.UTF_8)
        val before = target().readBytes()
        assertThrows(IllegalArgumentException::class.java) {
            newStore().save(
                listOf(Reminder("legacy-id", "Hello", done = true, time = LocalDateTime.of(10000, 1, 1, 10, 0))),
            )
        }
        assertArrayEquals(before, target().readBytes())
        assertEquals(original, target().readText(Charsets.UTF_8))
        assertEquals(listOf(Reminder("legacy-id", "Hello", done = true)), newStore().load())
    }

    private fun assertInvalidNwr3Time(reason: String, literal: String) {
        assertInvalidNwr3Wire(reason, "NWR3\ninvalid-time\tSGVsbG8=\t0\t$literal")
    }

    private fun assertInvalidNwr3Wire(reason: String, wire: String) {
        target().writeText(wire, Charsets.UTF_8)
        assertThrows("NWR3 fixture rejected: $reason", IllegalStateException::class.java) {
            newStore().load()
        }
    }

    @Suppress("unused")
    private fun touchAllBranches(
        store: ReminderStore,
    ): List<Reminder> = store.load()
}
