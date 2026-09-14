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
    fun P3_03_save_empty_list_writes_exact_NWR2_header_without_trailing_LF() {
        val store = newStore()
        store.save(emptyList())
        val bytes = target().readBytes()
        assertArrayEquals("NWR2".toByteArray(Charsets.UTF_8), bytes)
        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR2", text)
        assertFalse(text.endsWith("\n"))
    }

    @Test
    fun P3_04_one_reminder_writes_NWR2_LF_wire_format_with_padding_done_zero_and_round_trips() {
        val store = newStore()
        val reminder = Reminder("id-1", "Hello")
        store.save(listOf(reminder))

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR2\nid-1\tSGVsbG8=\t0", text)

        val firstRecord = text.substringAfter('\n')
        val tabs = firstRecord.count { it == '\t' }
        assertEquals(2, tabs)
        val encodedSegment = firstRecord.substringAfter('\t').substringBefore('\t')
        assertTrue("expected Base64URL padding", encodedSegment.contains('='))

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
    fun P3_08_reminder_text_with_TAB_CR_LF_round_trips_exactly_via_Base64URL_in_NWR2() {
        val store = newStore()
        val trickyText = "line1\tcol\nline2\rcol2"
        val reminder = Reminder("tricky", trickyText)
        store.save(listOf(reminder))

        val text = target().readText(Charsets.UTF_8)
        val lines = text.split("\n")
        assertEquals(2, lines.size)
        assertEquals("NWR2", lines[0])
        val record = lines[1]
        assertEquals(2, record.count { it == '\t' })
        val firstTab = record.indexOf('\t')
        val secondTab = record.indexOf('\t', firstTab + 1)
        assertTrue(secondTab > firstTab)
        val encoded = record.substring(firstTab + 1, secondTab)
        val doneLiteral = record.substring(secondTab + 1)
        assertEquals("0", doneLiteral)
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
    fun P3_12b_unsupported_header_NWR3_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("NWR3\nid-1\tSGVsbG8=\t0")
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
    // Revised: NWR1 load → save → NWR2 lazy migration
    // ----------------------------------------------------------------

    @Test
    fun P3E_06_NWR1_load_edit_save_migrates_file_to_NWR2_and_reloads_with_default_done_false() {
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
        assertEquals("NWR2", text.substringBefore('\n'))
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
    fun P3E_07_NWR1_first_save_migrates_header_to_NWR2() {
        val file = target()
        file.writeText("NWR1\nheader-id\tYmVmb3Jl")

        val store = newStore()
        val controller = ReminderController(store) { "unused" }

        assertTrue(controller.edit("header-id", "after"))

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR2", text.substringBefore('\n'))
    }

    @Test
    fun P3E_08_record_grammar_is_NWR2_two_TABs_and_done_literal_after_save() {
        val file = target()
        file.writeText("NWR1\ngrammar-a\tYWxwaGE=\ngrammar-b\tYmV0YQ==")

        val store = newStore()
        val controller = ReminderController(store) { "unused" }

        assertTrue(controller.edit("grammar-a", "alpha-edited"))

        val text = target().readText(Charsets.UTF_8)
        val lines = text.split("\n")
        assertEquals("NWR2", lines[0])
        assertEquals(3, lines.size)
        assertFalse(text.endsWith("\n"))

        val expectedById = mapOf(
            "grammar-a" to "alpha-edited",
            "grammar-b" to "beta",
        )

        for (i in 1..2) {
            val record = lines[i]
            assertEquals(2, record.count { it == '\t' })
            val firstTab = record.indexOf('\t')
            val secondTab = record.indexOf('\t', firstTab + 1)
            assertTrue(secondTab > firstTab)
            val id = record.substring(0, firstTab)
            val encoded = record.substring(firstTab + 1, secondTab)
            val doneLiteral = record.substring(secondTab + 1)
            assertEquals("0", doneLiteral)
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
    fun P3E_10_NWR1_edit_save_migrates_to_NWR2_records_with_done_literal_zero() {
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
        assertEquals("NWR2", lines[0])
        assertEquals(3, lines.size)
        assertFalse(text.endsWith("\n"))

        for (i in 1..2) {
            val record = lines[i]
            assertEquals(2, record.count { it == '\t' })
            val firstTab = record.indexOf('\t')
            val secondTab = record.indexOf('\t', firstTab + 1)
            assertTrue(firstTab > 0)
            assertTrue(secondTab > firstTab)
            val encoded = record.substring(firstTab + 1, secondTab)
            val doneLiteral = record.substring(secondTab + 1)
            assertEquals("0", doneLiteral)
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
    // NWR2 done-field round-trip and parser rejection
    // ----------------------------------------------------------------

    @Test
    fun P3NWR2_01_NWR2_true_record_writes_exact_bytes_with_done_one() {
        val store = newStore()
        val reminder = Reminder("id-1", "Hello", done = true)
        store.save(listOf(reminder))

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR2\nid-1\tSGVsbG8=\t1", text)

        assertEquals(listOf(reminder), newStore().load())
    }

    @Test
    fun P3NWR2_02_mixed_false_true_NWR2_round_trip_preserves_exact_input_order() {
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
            "NWR2\na\tSGVsbG8=\t0\nb\tV29ybGQ=\t1\nc\tZmlyc3Q=\t0\nd\tc2Vjb25k\t1",
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
    fun P3NWR2_05_NWR1_setDone_false_to_true_migrates_to_NWR2_with_done_true_on_reload() {
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
        assertEquals("NWR2", text.substringBefore('\n'))

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
        val store = newStore()
        val reminders = listOf(
            Reminder("a", "Hello", done = true),
            Reminder("b", "World", done = false),
        )
        store.save(reminders)

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
        val store = newStore()
        store.save(listOf(Reminder("edit-true", "before", done = true)))

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
    fun P3NWR2_08_NWR1_changed_edit_migrates_file_to_NWR2_with_correct_records() {
        val file = target()
        file.writeText("NWR1\nmig-id1\tZmlyc3Q=\nmig-id2\tc2Vjb25k")

        val store = newStore()
        val controller = ReminderController(store) { "unused" }
        assertTrue(controller.edit("mig-id1", "edited-first"))

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR2", text.substringBefore('\n'))
        assertEquals(
            "NWR2\nmig-id1\tZWRpdGVkLWZpcnN0\t0\nmig-id2\tc2Vjb25k\t0",
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
    fun P3NWR2_09_NWR1_create_migrates_file_to_NWR2_with_normal_idGenerator_use() {
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
        assertEquals("NWR2", text.substringBefore('\n'))
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
    fun P3NWR2_10_NWR1_remove_migrates_file_to_NWR2() {
        val file = target()
        file.writeText("NWR1\nkeep-id\tZmlyc3Q=\nremove-id\tc2Vjb25k\nextra-id\tdGhpcmQ=")

        val store = newStore()
        val controller = ReminderController(store) { "unused" }
        controller.remove("remove-id")

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR2", text.substringBefore('\n'))
        assertEquals(
            "NWR2\nkeep-id\tZmlyc3Q=\t0\nextra-id\tdGhpcmQ=\t0",
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

    @Suppress("unused")
    private fun touchAllBranches(
        store: ReminderStore,
    ): List<Reminder> = store.load()
}
