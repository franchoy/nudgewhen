package io.github.franchoy.nudgewhen.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertSame
import org.junit.Assert.assertThrows
import org.junit.Test
import java.time.LocalDateTime

class ReminderControllerTest {

    private class FakeReminderStore(
        initial: List<Reminder> = emptyList(),
    ) : ReminderStore {
        var saveCallCount: Int = 0
            private set
        var savedSnapshots: List<List<Reminder>> = emptyList()
            private set
        var saveCallback: ((List<Reminder>) -> Unit)? = null
        var saveException: Exception? = null

        private var loaded: List<Reminder> = initial.toList()

        override fun load(): List<Reminder> = loaded.toList()

        override fun save(reminders: List<Reminder>) {
            saveCallCount += 1
            val snapshot = reminders.toList()
            saveCallback?.invoke(snapshot)
            saveException?.let { throw it }
            savedSnapshots = savedSnapshots + listOf(snapshot)
            loaded = snapshot
        }
    }

    @Test
    fun C_01_constructor_exposes_store_load_order() {
        val initial = listOf(
            Reminder("id-3", "third"),
            Reminder("id-1", "first"),
            Reminder("id-2", "second"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "unused" }
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun C_02_valid_create_trims_text_before_creating_and_saving() {
        val store = FakeReminderStore()
        val controller = ReminderController(store) { "id-1" }
        controller.create("  hello  ")
        assertEquals(1, controller.reminders.size)
        assertEquals("hello", controller.reminders[0].text)
        assertEquals(false, controller.reminders[0].done)
        assertEquals(1, store.savedSnapshots.size)
        assertEquals("hello", store.savedSnapshots[0][0].text)
        assertEquals(false, store.savedSnapshots[0][0].done)
    }

    @Test
    fun C_03_valid_create_appends_to_end() {
        val store = FakeReminderStore(
            listOf(
                Reminder("a", "first"),
                Reminder("b", "second"),
            ),
        )
        val controller = ReminderController(store) { "c" }
        controller.create("third")
        val reminders = controller.reminders
        assertEquals(3, reminders.size)
        assertEquals("a", reminders[0].id)
        assertEquals("b", reminders[1].id)
        assertEquals("c", reminders[2].id)
    }

    @Test
    fun C_04_valid_create_invokes_idGenerator_exactly_once() {
        val store = FakeReminderStore()
        var calls = 0
        val controller = ReminderController(store) {
            calls += 1
            "id-$calls"
        }
        controller.create("hello")
        assertEquals(1, calls)
    }

    @Test
    fun C_05_empty_string_create_is_no_op() {
        val store = FakeReminderStore()
        val controller = ReminderController(store) { "id-1" }
        controller.create("")
        assertEquals(0, controller.reminders.size)
        assertEquals(0, store.saveCallCount)
    }

    @Test
    fun C_06_whitespace_only_create_is_no_op() {
        val store = FakeReminderStore()
        val controller = ReminderController(store) { "id-1" }
        controller.create("   ")
        assertEquals(0, controller.reminders.size)
        assertEquals(0, store.saveCallCount)
    }

    @Test
    fun C_07_empty_whitespace_create_does_not_invoke_idGenerator() {
        val store = FakeReminderStore()
        var calls = 0
        val controller = ReminderController(store) {
            calls += 1
            "id-$calls"
        }
        controller.create("")
        controller.create("   ")
        assertEquals(0, calls)
    }

    @Test
    fun C_08_empty_whitespace_create_does_not_save() {
        val store = FakeReminderStore()
        val controller = ReminderController(store) { "id-1" }
        controller.create("")
        controller.create("\t\n\r ")
        assertEquals(0, store.saveCallCount)
    }

    @Test
    fun C_09_generated_empty_ID_rejected_with_IllegalArgumentException() {
        val store = FakeReminderStore()
        val controller = ReminderController(store) { "" }
        assertThrows(IllegalArgumentException::class.java) {
            controller.create("hello")
        }
    }

    @Test
    fun C_10_generated_ID_containing_TAB_rejected() {
        val store = FakeReminderStore()
        val controller = ReminderController(store) { "id\tbad" }
        assertThrows(IllegalArgumentException::class.java) {
            controller.create("hello")
        }
    }

    @Test
    fun C_11_generated_ID_containing_CR_rejected() {
        val store = FakeReminderStore()
        val controller = ReminderController(store) { "id\rbad" }
        assertThrows(IllegalArgumentException::class.java) {
            controller.create("hello")
        }
    }

    @Test
    fun C_12_generated_ID_containing_LF_rejected() {
        val store = FakeReminderStore()
        val controller = ReminderController(store) { "id\nbad" }
        assertThrows(IllegalArgumentException::class.java) {
            controller.create("hello")
        }
    }

    @Test
    fun C_13_duplicate_generated_ID_rejected() {
        val store = FakeReminderStore(listOf(Reminder("dup", "existing")))
        val controller = ReminderController(store) { "dup" }
        assertThrows(IllegalArgumentException::class.java) {
            controller.create("hello")
        }
    }

    @Test
    fun C_14_invalid_or_duplicate_ID_does_not_save() {
        // A. invalid generated ID
        val storeA = FakeReminderStore()
        val controllerA = ReminderController(storeA) { "" }
        assertThrows(IllegalArgumentException::class.java) {
            controllerA.create("hello")
        }
        assertEquals(0, storeA.saveCallCount)

        // B. duplicate generated ID
        val storeB = FakeReminderStore(listOf(Reminder("dup", "existing")))
        val controllerB = ReminderController(storeB) { "dup" }
        assertThrows(IllegalArgumentException::class.java) {
            controllerB.create("hello")
        }
        assertEquals(0, storeB.saveCallCount)
    }

    @Test
    fun C_15_invalid_or_duplicate_ID_preserves_state() {
        // A. invalid generated ID
        val initialA = listOf(Reminder("a", "first"))
        val storeA = FakeReminderStore(initialA)
        val controllerA = ReminderController(storeA) { "" }
        assertThrows(IllegalArgumentException::class.java) {
            controllerA.create("hello")
        }
        assertEquals(initialA, controllerA.reminders)

        // B. duplicate generated ID
        val initialB = listOf(Reminder("dup", "existing"))
        val storeB = FakeReminderStore(initialB)
        val controllerB = ReminderController(storeB) { "dup" }
        assertThrows(IllegalArgumentException::class.java) {
            controllerB.create("hello")
        }
        assertEquals(initialB, controllerB.reminders)
    }

    @Test
    fun C_16_unknown_remove_is_no_op() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        controller.remove("nonexistent")
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun C_17_unknown_remove_does_not_save() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        controller.remove("nonexistent")
        assertEquals(0, store.saveCallCount)
    }

    @Test
    fun C_18_known_remove_removes_the_matching_reminder() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second", done = true),
            Reminder("c", "third"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        controller.remove("b")
        val reminders = controller.reminders
        assertEquals(2, reminders.size)
        assertEquals(false, reminders.any { it.id == "b" })
    }

    @Test
    fun C_19_known_remove_preserves_remaining_order() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second"),
            Reminder("c", "third"),
            Reminder("d", "fourth"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        controller.remove("b")
        val reminders = controller.reminders
        assertEquals(listOf("a", "c", "d"), reminders.map { it.id })
    }

    @Test
    fun C_20_successful_create_saves_candidate_before_exposing_new_state() {
        val store = FakeReminderStore()
        val controller = ReminderController(store) { "new-id" }
        var stateDuringSave: List<Reminder>? = null
        store.saveCallback = { _ ->
            stateDuringSave = controller.reminders.toList()
        }
        controller.create("hello")
        assertNotNull(stateDuringSave)
        assertEquals(emptyList<Reminder>(), stateDuringSave)
        assertEquals(1, controller.reminders.size)
        assertEquals("new-id", controller.reminders[0].id)
    }

    @Test
    fun C_21_successful_remove_saves_candidate_before_exposing_new_state() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        var stateDuringSave: List<Reminder>? = null
        store.saveCallback = { _ ->
            stateDuringSave = controller.reminders.toList()
        }
        controller.remove("a")
        assertNotNull(stateDuringSave)
        assertEquals(2, stateDuringSave!!.size)
        assertEquals(1, controller.reminders.size)
        assertEquals("b", controller.reminders[0].id)
    }

    @Test
    fun C_22_create_save_failure_propagates() {
        val store = FakeReminderStore()
        val controller = ReminderController(store) { "new-id" }
        val original = IllegalStateException("save failure")
        store.saveException = original
        val thrown = assertThrows(IllegalStateException::class.java) {
            controller.create("hello")
        }
        assertSame(original, thrown)
    }

    @Test
    fun C_23_create_save_failure_preserves_previous_state() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "new-id" }
        store.saveException = IllegalStateException("save failure")
        assertThrows(IllegalStateException::class.java) {
            controller.create("hello")
        }
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun C_24_remove_save_failure_propagates() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val original = IllegalStateException("save failure")
        store.saveException = original
        val thrown = assertThrows(IllegalStateException::class.java) {
            controller.remove("a")
        }
        assertSame(original, thrown)
    }

    @Test
    fun C_25_remove_save_failure_preserves_previous_state() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        store.saveException = IllegalStateException("save failure")
        assertThrows(IllegalStateException::class.java) {
            controller.remove("a")
        }
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun E_01_changed_valid_edit_returns_true() {
        val initial = listOf(Reminder("a", "old text"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.edit("a", "new text")
        assertEquals(true, result)
    }

    @Test
    fun E_02_changed_edit_changes_only_target_text() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second", done = false),
            Reminder("c", "third"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        controller.edit("b", "second-edited")
        val reminders = controller.reminders
        assertEquals("first", reminders[0].text)
        assertEquals("second-edited", reminders[1].text)
        assertEquals("third", reminders[2].text)
        assertEquals(false, reminders[1].done)
    }

    @Test
    fun E_03_changed_edit_preserves_target_id() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val beforeId = controller.reminders[1].id
        controller.edit("b", "second-edited")
        val reminders = controller.reminders
        assertEquals(beforeId, reminders[1].id)
        assertEquals("b", reminders[1].id)
    }

    @Test
    fun E_04_changed_edit_preserves_target_index() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second"),
            Reminder("c", "third"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        controller.edit("b", "second-edited")
        val reminders = controller.reminders
        assertEquals("a", reminders[0].id)
        assertEquals("b", reminders[1].id)
        assertEquals("c", reminders[2].id)
    }

    @Test
    fun E_05_changed_edit_preserves_neighbors_and_order() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second"),
            Reminder("c", "third"),
            Reminder("d", "fourth"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        controller.edit("b", "second-edited")
        val reminders = controller.reminders
        assertEquals(listOf("a", "b", "c", "d"), reminders.map { it.id })
        assertEquals("first", reminders[0].text)
        assertEquals("second-edited", reminders[1].text)
        assertEquals("third", reminders[2].text)
        assertEquals("fourth", reminders[3].text)
    }

    @Test
    fun E_06_changed_edit_trims_input() {
        val initial = listOf(Reminder("a", "old text"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        controller.edit("a", "   new text   ")
        val reminders = controller.reminders
        assertEquals("new text", reminders[0].text)
        assertEquals(1, store.savedSnapshots.size)
        assertEquals("new text", store.savedSnapshots[0][0].text)
    }

    @Test
    fun E_07_empty_edit_returns_false_no_save() {
        val initial = listOf(Reminder("a", "existing"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.edit("a", "")
        assertEquals(false, result)
        assertEquals(0, store.saveCallCount)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun E_08_whitespace_only_edit_returns_false_no_save() {
        val initial = listOf(Reminder("a", "existing"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.edit("a", " \t\n ")
        assertEquals(false, result)
        assertEquals(0, store.saveCallCount)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun E_09_missing_id_edit_returns_false_no_save() {
        val initial = listOf(Reminder("a", "existing"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.edit("nonexistent", "new text")
        assertEquals(false, result)
        assertEquals(0, store.saveCallCount)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun E_10_exact_identical_edit_returns_true_no_save() {
        val initial = listOf(Reminder("a", "hello"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.edit("a", "hello")
        assertEquals(true, result)
        assertEquals(0, store.saveCallCount)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun E_11_normalized_identical_edit_returns_true_no_save() {
        val initial = listOf(Reminder("a", "hello"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.edit("a", "  hello  ")
        assertEquals(true, result)
        assertEquals(0, store.saveCallCount)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun E_12_changed_edit_saves_exactly_once_with_complete_candidate() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second"),
            Reminder("c", "third"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        controller.edit("b", "second-edited")
        val expected = listOf(
            Reminder("a", "first"),
            Reminder("b", "second-edited"),
            Reminder("c", "third"),
        )
        assertEquals(1, store.saveCallCount)
        assertEquals(1, store.savedSnapshots.size)
        assertEquals(expected, store.savedSnapshots[0])
    }

    @Test
    fun E_13_edit_does_not_invoke_idGenerator() {
        val initial = listOf(Reminder("a", "existing"))
        val store = FakeReminderStore(initial)
        var calls = 0
        val controller = ReminderController(store) {
            calls += 1
            "new-id-$calls"
        }
        // changed valid edit
        controller.edit("a", "changed")
        // missing id
        controller.edit("nonexistent", "anything")
        // invalid blank edit
        controller.edit("a", "   ")
        // identical edit
        controller.edit("a", "changed")
        assertEquals(0, calls)
    }

    @Test
    fun E_14_old_state_observable_during_save() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second"),
            Reminder("c", "third"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        var stateDuringSave: List<Reminder>? = null
        store.saveCallback = { _ ->
            stateDuringSave = controller.reminders.toList()
        }
        controller.edit("b", "second-edited")
        assertNotNull(stateDuringSave)
        assertEquals(initial, stateDuringSave!!)
        val reminders = controller.reminders
        assertEquals("second-edited", reminders[1].text)
    }

    @Test
    fun E_15_edit_save_failure_propagates() {
        val initial = listOf(Reminder("a", "existing"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val original = IllegalStateException("save failure")
        store.saveException = original
        val thrown = assertThrows(IllegalStateException::class.java) {
            controller.edit("a", "new text")
        }
        assertSame(original, thrown)
    }

    @Test
    fun E_16_edit_save_failure_preserves_state() {
        val initial = listOf(Reminder("a", "existing"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        store.saveException = IllegalStateException("save failure")
        assertThrows(IllegalStateException::class.java) {
            controller.edit("a", "new text")
        }
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun E_17_unicode_edit_text_supported() {
        val initial = listOf(Reminder("a", "old text"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val unicodeText = "caf\u00E9 \uD83D\uDE0A \u4E2D\u6587"
        val result = controller.edit("a", unicodeText)
        assertEquals(true, result)
        assertEquals(unicodeText, controller.reminders[0].text)
        assertEquals(1, store.savedSnapshots.size)
        assertEquals(unicodeText, store.savedSnapshots[0][0].text)
    }

    @Test
    fun D_01_setDone_false_to_true_changes_target_only() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second"),
            Reminder("c", "third"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.setDone("b", true)
        assertEquals(true, result)
        val reminders = controller.reminders
        assertEquals(true, reminders[1].done)
        assertEquals("b", reminders[1].id)
        assertEquals("second", reminders[1].text)
        assertEquals("first", reminders[0].text)
        assertEquals("third", reminders[2].text)
        val expected = listOf(
            Reminder("a", "first", done = false),
            Reminder("b", "second", done = true),
            Reminder("c", "third", done = false),
        )
        assertEquals(expected, reminders)
        assertEquals(1, store.saveCallCount)
        assertEquals(1, store.savedSnapshots.size)
        assertEquals(expected, store.savedSnapshots[0])
    }

    @Test
    fun D_02_setDone_true_to_false_changes_target_only() {
        val initial = listOf(Reminder("a", "existing", done = true))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.setDone("a", false)
        assertEquals(true, result)
        assertEquals(false, controller.reminders[0].done)
    }

    @Test
    fun D_03_setDone_same_state_returns_true_no_save() {
        val initial = listOf(Reminder("a", "existing", done = false))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.setDone("a", false)
        assertEquals(true, result)
        assertEquals(0, store.saveCallCount)
        assertEquals(0, store.savedSnapshots.size)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun D_04_setDone_missing_id_returns_false_no_save() {
        val initial = listOf(Reminder("a", "existing"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.setDone("nonexistent", true)
        assertEquals(false, result)
        assertEquals(0, store.saveCallCount)
        assertEquals(0, store.savedSnapshots.size)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun D_05_setDone_never_invokes_idGenerator() {
        val initial = listOf(
            Reminder("a", "first", done = false),
            Reminder("b", "second", done = true),
        )
        val store = FakeReminderStore(initial)
        var idCalls = 0
        val controller = ReminderController(store) {
            idCalls += 1
            "unused-$idCalls"
        }
        controller.setDone("a", true)          // changed-state
        controller.setDone("b", false)         // changed-state
        controller.setDone("a", true)          // same-state
        controller.setDone("nonexistent", true) // missing-id
        assertEquals(0, idCalls)
    }

    @Test
    fun D_06_setDone_old_state_observable_during_save() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second"),
            Reminder("c", "third"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        var stateDuringSave: List<Reminder>? = null
        store.saveCallback = { _ ->
            stateDuringSave = controller.reminders.toList()
        }
        val result = controller.setDone("b", true)
        assertEquals(true, result)
        assertNotNull(stateDuringSave)
        assertEquals(initial, stateDuringSave!!)
        assertEquals(true, controller.reminders[1].done)
    }

    @Test
    fun D_07_setDone_save_failure_propagates_and_preserves_state() {
        val initial = listOf(Reminder("a", "existing"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val original = IllegalStateException("save failure")
        store.saveException = original
        val thrown = assertThrows(IllegalStateException::class.java) {
            controller.setDone("a", true)
        }
        assertSame(original, thrown)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun D_08_edit_then_setDone_preserves_edited_text_and_done_state() {
        val initial = listOf(Reminder("a", "old text"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val editResult = controller.edit("a", "new text")
        assertEquals(true, editResult)
        val setDoneResult = controller.setDone("a", true)
        assertEquals(true, setDoneResult)
        assertEquals("new text", controller.reminders[0].text)
        assertEquals(true, controller.reminders[0].done)
    }

    @Test
    fun D_09_setDone_then_edit_preserves_done_state() {
        val initial = listOf(Reminder("a", "old text"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val setDoneResult = controller.setDone("a", true)
        assertEquals(true, setDoneResult)
        val editResult = controller.edit("a", "new text")
        assertEquals(true, editResult)
        assertEquals("new text", controller.reminders[0].text)
        assertEquals(true, controller.reminders[0].done)
    }

    @Test
    fun T_01_setTime_sets_a_valid_time_on_the_target_reminder() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val time = LocalDateTime.of(2026, 1, 1, 9, 30)
        val result = controller.setTime("b", time)
        assertEquals(true, result)
        assertEquals(time, controller.reminders[1].time)
        assertNull(controller.reminders[0].time)
    }

    @Test
    fun T_02_setTime_replaces_an_existing_time() {
        val initial = listOf(
            Reminder("a", "first", time = LocalDateTime.of(2026, 1, 1, 9, 30)),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val replacement = LocalDateTime.of(2026, 6, 15, 18, 45)
        val result = controller.setTime("a", replacement)
        assertEquals(true, result)
        assertEquals(replacement, controller.reminders[0].time)
        assertEquals(1, store.saveCallCount)
    }

    @Test
    fun T_03_setTime_clears_a_non_null_time() {
        val initial = listOf(
            Reminder("a", "first", time = LocalDateTime.of(2026, 1, 1, 9, 30)),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.setTime("a", null)
        assertEquals(true, result)
        assertNull(controller.reminders[0].time)
        assertEquals(1, store.saveCallCount)
    }

    @Test
    fun T_04_setTime_clearing_an_already_null_time_returns_true_without_saving() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.setTime("a", null)
        assertEquals(true, result)
        assertEquals(0, store.saveCallCount)
        assertEquals(0, store.savedSnapshots.size)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun T_05_setTime_unchanged_valid_time_returns_true_without_saving() {
        val initial = listOf(
            Reminder("a", "first", time = LocalDateTime.of(2026, 1, 1, 9, 30)),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.setTime("a", LocalDateTime.of(2026, 1, 1, 9, 30))
        assertEquals(true, result)
        assertEquals(0, store.saveCallCount)
        assertEquals(0, store.savedSnapshots.size)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun T_06_setTime_missing_id_returns_false_without_saving() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.setTime("nonexistent", LocalDateTime.of(2026, 1, 1, 9, 30))
        assertEquals(false, result)
        assertEquals(0, store.saveCallCount)
        assertEquals(0, store.savedSnapshots.size)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun T_07_setTime_missing_id_with_invalid_time_returns_false_without_validation() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val result = controller.setTime("nonexistent", LocalDateTime.of(2026, 1, 1, 9, 30, 30))
        assertEquals(false, result)
        assertEquals(0, store.saveCallCount)
        assertEquals(0, store.savedSnapshots.size)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun T_08_setTime_invalid_non_null_time_throws_IllegalArgumentException() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        assertThrows(IllegalArgumentException::class.java) {
            controller.setTime("a", LocalDateTime.of(2026, 1, 1, 9, 30, 30))
        }
        assertEquals(0, store.saveCallCount)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun T_09_setTime_rejects_a_non_zero_second() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        assertThrows(IllegalArgumentException::class.java) {
            controller.setTime("a", LocalDateTime.of(2026, 1, 1, 9, 30, 1))
        }
        assertEquals(0, store.saveCallCount)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun T_10_setTime_rejects_a_non_zero_nanosecond() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        assertThrows(IllegalArgumentException::class.java) {
            controller.setTime("a", LocalDateTime.of(2026, 1, 1, 9, 30, 0, 1))
        }
        assertEquals(0, store.saveCallCount)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun T_11_setTime_rejects_year_zero() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        assertThrows(IllegalArgumentException::class.java) {
            controller.setTime("a", LocalDateTime.of(0, 1, 1, 0, 0))
        }
        assertEquals(0, store.saveCallCount)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun T_12_setTime_rejects_year_10000() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        assertThrows(IllegalArgumentException::class.java) {
            controller.setTime("a", LocalDateTime.of(10000, 1, 1, 0, 0))
        }
        assertEquals(0, store.saveCallCount)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun T_13_setTime_accepts_year_one_and_year_9999() {
        val store = FakeReminderStore(listOf(Reminder("a", "first")))
        val controller = ReminderController(store) { "x" }
        val yearOne = LocalDateTime.of(1, 1, 1, 0, 0)
        assertEquals(true, controller.setTime("a", yearOne))
        assertEquals(yearOne, controller.reminders[0].time)
        val yearNineThousandNineHundredNinetyNine = LocalDateTime.of(9999, 12, 31, 23, 59)
        assertEquals(true, controller.setTime("a", yearNineThousandNineHundredNinetyNine))
        assertEquals(yearNineThousandNineHundredNinetyNine, controller.reminders[0].time)
        assertEquals(2, store.saveCallCount)
    }

    @Test
    fun T_14_setTime_rejects_an_invalid_supplied_time_equal_to_an_invalid_stored_time() {
        val invalid = LocalDateTime.of(2026, 1, 1, 9, 30, 30)
        val initial = listOf(Reminder("a", "first", time = invalid))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        assertThrows(IllegalArgumentException::class.java) {
            controller.setTime("a", invalid)
        }
        assertEquals(0, store.saveCallCount)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun T_15_setTime_effective_change_saves_exactly_once_with_the_complete_candidate() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second"),
            Reminder("c", "third"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val time = LocalDateTime.of(2026, 1, 1, 9, 30)
        controller.setTime("b", time)
        val expected = listOf(
            Reminder("a", "first"),
            Reminder("b", "second", time = time),
            Reminder("c", "third"),
        )
        assertEquals(1, store.saveCallCount)
        assertEquals(1, store.savedSnapshots.size)
        assertEquals(expected, store.savedSnapshots[0])
        assertEquals(expected, controller.reminders)
    }

    @Test
    fun T_16_setTime_old_state_is_observable_during_the_save_callback() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second"),
            Reminder("c", "third"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        var stateDuringSave: List<Reminder>? = null
        store.saveCallback = { _ ->
            stateDuringSave = controller.reminders.toList()
        }
        val result = controller.setTime("b", LocalDateTime.of(2026, 1, 1, 9, 30))
        assertEquals(true, result)
        assertNotNull(stateDuringSave)
        assertEquals(initial, stateDuringSave!!)
        assertEquals(LocalDateTime.of(2026, 1, 1, 9, 30), controller.reminders[1].time)
    }

    @Test
    fun T_17_setTime_save_failure_propagates_the_same_exception_and_preserves_state() {
        val initial = listOf(Reminder("a", "existing"))
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val original = IllegalStateException("save failure")
        store.saveException = original
        val thrown = assertThrows(IllegalStateException::class.java) {
            controller.setTime("a", LocalDateTime.of(2026, 1, 1, 9, 30))
        }
        assertSame(original, thrown)
        assertEquals(initial, controller.reminders)
    }

    @Test
    fun T_18_setTime_never_invokes_idGenerator() {
        val initial = listOf(Reminder("a", "first"))
        val store = FakeReminderStore(initial)
        var idCalls = 0
        val controller = ReminderController(store) {
            idCalls += 1
            "unused-$idCalls"
        }
        controller.setTime("a", LocalDateTime.of(2026, 1, 1, 9, 30))          // effective change
        controller.setTime("a", LocalDateTime.of(2026, 1, 1, 9, 30))          // unchanged
        controller.setTime("a", null)                                         // effective clear
        controller.setTime("nonexistent", LocalDateTime.of(2026, 1, 1, 9, 30)) // missing id
        assertEquals(0, idCalls)
    }

    @Test
    fun T_19_setTime_preserves_id_text_done_size_index_and_neighbors() {
        val initial = listOf(
            Reminder("a", "first"),
            Reminder("b", "second", done = true),
            Reminder("c", "third"),
            Reminder("d", "fourth"),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "x" }
        val time = LocalDateTime.of(2026, 1, 1, 9, 30)
        val result = controller.setTime("b", time)
        assertEquals(true, result)
        val reminders = controller.reminders
        assertEquals(4, reminders.size)
        assertEquals(listOf("a", "b", "c", "d"), reminders.map { it.id })
        assertEquals("b", reminders[1].id)
        assertEquals("second", reminders[1].text)
        assertEquals(true, reminders[1].done)
        assertEquals(time, reminders[1].time)
        assertEquals("first", reminders[0].text)
        assertEquals("third", reminders[2].text)
        assertEquals("fourth", reminders[3].text)
        assertNull(reminders[0].time)
        assertNull(reminders[2].time)
        assertNull(reminders[3].time)
    }

    @Test
    fun T_20_setTime_composes_with_create_remove_edit_and_setDone() {
        val initial = listOf(
            Reminder("a", "first", time = LocalDateTime.of(2026, 1, 1, 9, 30)),
        )
        val store = FakeReminderStore(initial)
        val controller = ReminderController(store) { "new-id" }
        val time = LocalDateTime.of(2026, 1, 1, 9, 30)

        // create: a newly created reminder carries no time
        controller.create("second")
        assertEquals(2, controller.reminders.size)
        assertNull(controller.reminders[1].time)

        // edit preserves an existing time
        assertEquals(true, controller.edit("a", "first-edited"))
        assertEquals(time, controller.reminders[0].time)

        // setDone preserves an existing time
        assertEquals(true, controller.setDone("a", true))
        assertEquals(time, controller.reminders[0].time)
        assertEquals(true, controller.reminders[0].done)

        // setTime preserves the text and the done state
        val replacement = LocalDateTime.of(2026, 2, 2, 8, 15)
        assertEquals(true, controller.setTime("a", replacement))
        assertEquals(replacement, controller.reminders[0].time)
        assertEquals("first-edited", controller.reminders[0].text)
        assertEquals(true, controller.reminders[0].done)

        // remove removes the reminder that carried the time
        controller.remove("a")
        assertEquals(1, controller.reminders.size)
        assertEquals("new-id", controller.reminders[0].id)
    }
}