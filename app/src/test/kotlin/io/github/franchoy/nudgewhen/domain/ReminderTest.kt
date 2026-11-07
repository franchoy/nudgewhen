package io.github.franchoy.nudgewhen.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNull
import org.junit.Test
import java.time.LocalDateTime

class ReminderTest {

    @Test
    fun R_01_reminder_stores_exactly_supplied_id_and_text() {
        val reminder = Reminder(id = "id-1", text = "buy milk")
        assertEquals("id-1", reminder.id)
        assertEquals("buy milk", reminder.text)
        assertEquals(false, reminder.done)
    }

    @Test
    fun R_02_reminder_value_equality_depends_on_id_text_and_done() {
        val aSame = Reminder("id-1", "text")
        val bSame = Reminder("id-1", "text")
        val differentId = Reminder("id-2", "text")
        val differentText = Reminder("id-1", "different")
        val sameIdSameTextDoneFalse = Reminder("id-1", "text", done = false)
        val sameIdSameTextDoneTrue = Reminder("id-1", "text", done = true)

        assertEquals(aSame, bSame)
        assertNotEquals(aSame, differentId)
        assertNotEquals(aSame, differentText)
        assertNotEquals(sameIdSameTextDoneFalse, sameIdSameTextDoneTrue)
    }

    @Test
    fun R_03_two_argument_construction_defaults_done_false_and_time_null() {
        val reminder = Reminder("id-1", "text")
        assertEquals(false, reminder.done)
        assertNull(reminder.time)
    }

    @Test
    fun R_04_three_argument_construction_defaults_time_null() {
        val reminder = Reminder("id-1", "text", true)
        assertEquals(true, reminder.done)
        assertNull(reminder.time)
    }

    @Test
    fun R_05_explicit_non_null_time_is_preserved() {
        val time = LocalDateTime.of(2026, 1, 1, 9, 30)
        val reminder = Reminder("id-1", "text", false, time)
        assertEquals(time, reminder.time)
        assertEquals(LocalDateTime.of(2026, 1, 1, 9, 30), reminder.time)
    }

    @Test
    fun R_06_reminders_with_different_times_are_not_equal() {
        val first = Reminder("id-1", "text", false, LocalDateTime.of(2026, 1, 1, 9, 30))
        val second = Reminder("id-1", "text", false, LocalDateTime.of(2026, 1, 1, 9, 31))
        assertNotEquals(first, second)
    }

    @Test
    fun R_07_equal_reminders_with_equal_times_have_equal_hash_codes() {
        val first = Reminder("id-1", "text", false, LocalDateTime.of(2026, 1, 1, 9, 30))
        val second = Reminder("id-1", "text", false, LocalDateTime.of(2026, 1, 1, 9, 30))
        assertEquals(first, second)
        assertEquals(first.hashCode(), second.hashCode())
    }

    @Test
    fun R_08_copy_preserves_time() {
        val time = LocalDateTime.of(2026, 1, 1, 9, 30)
        val reminder = Reminder("id-1", "text", true, time)
        val copied = reminder.copy()
        assertEquals(reminder, copied)
        assertEquals(time, copied.time)
    }

    @Test
    fun R_09_copy_with_null_time_clears_time() {
        val reminder = Reminder("id-1", "text", true, LocalDateTime.of(2026, 1, 1, 9, 30))
        val cleared = reminder.copy(time = null)
        assertNull(cleared.time)
        assertEquals("id-1", cleared.id)
        assertEquals("text", cleared.text)
        assertEquals(true, cleared.done)
    }
}