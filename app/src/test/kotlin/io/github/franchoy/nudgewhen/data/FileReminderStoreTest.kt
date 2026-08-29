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
        tempDir = Files.createTempDirectory("nwr1-store-").toFile()
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

    private fun target(): File = File(tempDir, "reminders.nwr1")

    private fun newStore(): FileReminderStore = FileReminderStore(target())

    @Test
    fun P3_01_missing_file_load_returns_empty_list() {
        assertFalse(target().exists())
        assertEquals(emptyList<Reminder>(), newStore().load())
    }

    @Test
    fun P3_02_header_only_file_load_returns_empty_list() {
        val file = target()
        file.writeText("NWR1")
        assertEquals(emptyList<Reminder>(), newStore().load())
    }

    @Test
    fun P3_03_save_empty_list_writes_exact_header_without_trailing_LF() {
        val store = newStore()
        store.save(emptyList())
        val bytes = target().readBytes()
        assertArrayEquals("NWR1".toByteArray(Charsets.UTF_8), bytes)
        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR1", text)
        assertFalse(text.endsWith("\n"))
    }

    @Test
    fun P3_04_one_reminder_writes_LF_wire_format_with_padding_and_round_trips() {
        val store = newStore()
        val reminder = Reminder("id-1", "Hello")
        store.save(listOf(reminder))

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR1\nid-1\tSGVsbG8=", text)

        val encodedSegment = text.substringAfter('\t')
        assertTrue("expected Base64URL padding", encodedSegment.contains('='))

        assertEquals(listOf(reminder), newStore().load())
    }

    @Test
    fun P3_05_multiple_reminders_round_trip_in_exact_input_order() {
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
    fun P3_08_reminder_text_with_TAB_CR_LF_round_trips_exactly_via_Base64URL() {
        val store = newStore()
        val trickyText = "line1\tcol\nline2\rcol2"
        val reminder = Reminder("tricky", trickyText)
        store.save(listOf(reminder))

        val text = target().readText(Charsets.UTF_8)
        val lines = text.split("\n")
        assertEquals(2, lines.size)
        assertEquals("NWR1", lines[0])
        val record = lines[1]
        assertEquals(1, record.count { it == '\t' })
        val encoded = record.substringAfter('\t')
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

    @Test
    fun P3_11_existing_empty_file_rejected_with_IllegalStateException() {
        val file = target()
        file.writeBytes(ByteArray(0))
        assertThrows(IllegalStateException::class.java) { newStore().load() }
    }

    @Test
    fun P3_12_wrong_header_rejected_with_IllegalStateException() {
        val file = target()
        file.writeText("WRONG\nid-1\tSGVsbG8=")
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

    @Test
    fun P3E_06_existing_valid_NWR1_load_edit_save_reload() {
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
    fun P3E_07_NWR1_header_remains_exactly_NWR1_after_edit_save() {
        val store = newStore()
        store.save(listOf(Reminder("header-id", "before")))
        val controller = ReminderController(store) { "unused" }

        assertTrue(controller.edit("header-id", "after"))

        val text = target().readText(Charsets.UTF_8)
        assertEquals("NWR1", text.substringBefore('\n'))
    }

    @Test
    fun P3E_08_record_grammar_unchanged_after_edit_save() {
        val store = newStore()
        store.save(
            listOf(
                Reminder("grammar-a", "alpha"),
                Reminder("grammar-b", "beta"),
            ),
        )
        val controller = ReminderController(store) { "unused" }

        assertTrue(controller.edit("grammar-a", "alpha-edited"))

        val text = target().readText(Charsets.UTF_8)
        val lines = text.split("\n")
        assertEquals("NWR1", lines[0])
        assertEquals(3, lines.size)
        assertFalse(text.endsWith("\n"))

        val expectedById = mapOf(
            "grammar-a" to "alpha-edited",
            "grammar-b" to "beta",
        )

        for (i in 1..2) {
            val record = lines[i]
            assertEquals(1, record.count { it == '\t' })
            val tabIndex = record.indexOf('\t')
            val id = record.substring(0, tabIndex)
            val encoded = record.substring(tabIndex + 1)
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

    @Test
    fun P3E_10_edit_requires_no_NWR1_migration() {
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
        assertEquals("NWR1", lines[0])
        assertEquals(3, lines.size)
        assertFalse(text.endsWith("\n"))

        for (i in 1..2) {
            val record = lines[i]
            assertEquals(1, record.count { it == '\t' })
            val tabIndex = record.indexOf('\t')
            assertTrue(tabIndex > 0)
            val encoded = record.substring(tabIndex + 1)
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

    @Suppress("unused")
    private fun touchAllBranches(
        store: ReminderStore,
    ): List<Reminder> = store.load()
}