package io.github.franchoy.nudgewhen.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Test

class ReminderTest {

    @Test
    fun R_01_reminder_stores_exactly_supplied_id_and_text() {
        val reminder = Reminder(id = "id-1", text = "buy milk")
        assertEquals("id-1", reminder.id)
        assertEquals("buy milk", reminder.text)
    }

    @Test
    fun R_02_reminder_value_equality_depends_on_id_and_text() {
        val aSame = Reminder("id-1", "text")
        val bSame = Reminder("id-1", "text")
        val differentId = Reminder("id-2", "text")
        val differentText = Reminder("id-1", "different")

        assertEquals(aSame, bSame)
        assertNotEquals(aSame, differentId)
        assertNotEquals(aSame, differentText)
    }
}