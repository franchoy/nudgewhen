package io.github.franchoy.nudgewhen.ui

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertThrows
import org.junit.Test
import java.time.DateTimeException
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.util.Locale
import java.util.TimeZone

/**
 * Deterministic JVM proof for the v0.1.5 Phase-4B1 pure time helper.
 *
 * Every test is independent of the machine on which it runs: the JVM default
 * timezone and the JVM default format locale are restored in a `finally` block
 * whenever a test changes them.
 */
class ReminderTimeUiTest {

    /** 2026-01-01T00:00:00Z expressed in milliseconds since the epoch. */
    private val utcMidnight2026Millis = 1_767_225_600_000L

    /** 0001-01-01T00:00:00Z expressed in milliseconds since the epoch. */
    private val utcMidnightYear1Millis = -62_135_596_800_000L

    /** 9999-12-31T00:00:00Z expressed in milliseconds since the epoch. */
    private val utcMidnightYear9999Millis = 253_402_214_400_000L

    @Test
    fun P4B1_01_picker_millis_reads_utc_calendar_date() {
        assertEquals(
            LocalDate.of(2026, 1, 1),
            ReminderTimeUi.pickerMillisToDate(utcMidnight2026Millis),
        )
    }

    @Test
    fun P4B1_02_picker_millis_reads_utc_calendar_date_of_a_non_midnight_instant() {
        val twoThirtyUtcMillis = utcMidnight2026Millis + (2 * 60 + 30) * 60_000L

        assertEquals(
            LocalDate.of(2026, 1, 1),
            ReminderTimeUi.pickerMillisToDate(twoThirtyUtcMillis),
        )
    }

    @Test
    fun P4B1_03_picker_conversion_is_independent_of_the_default_timezone() {
        val zones = listOf("UTC", "America/Los_Angeles", "Asia/Tokyo")

        zones.forEach { zoneId ->
            withDefaultTimeZone(zoneId) {
                assertEquals(
                    LocalDate.of(2026, 1, 1),
                    ReminderTimeUi.pickerMillisToDate(utcMidnight2026Millis),
                )
                assertEquals(
                    utcMidnight2026Millis,
                    ReminderTimeUi.dateToPickerMillis(LocalDate.of(2026, 1, 1)),
                )
            }
        }
    }

    @Test
    fun P4B1_04_date_to_picker_millis_encodes_utc_midnight() {
        assertEquals(
            utcMidnight2026Millis,
            ReminderTimeUi.dateToPickerMillis(LocalDate.of(2026, 1, 1)),
        )
        assertEquals(
            utcMidnightYear1Millis,
            ReminderTimeUi.dateToPickerMillis(LocalDate.of(1, 1, 1)),
        )
        assertEquals(
            utcMidnightYear9999Millis,
            ReminderTimeUi.dateToPickerMillis(LocalDate.of(9999, 12, 31)),
        )
    }

    @Test
    fun P4B1_05_date_picker_round_trip_preserves_the_selected_date() {
        val dates = listOf(
            LocalDate.of(2026, 1, 1),
            LocalDate.of(2024, 2, 29),
            LocalDate.of(2026, 12, 31),
            LocalDate.of(1, 1, 1),
            LocalDate.of(9999, 12, 31),
        )

        dates.forEach { date ->
            assertEquals(
                date,
                ReminderTimeUi.pickerMillisToDate(ReminderTimeUi.dateToPickerMillis(date)),
            )
        }
    }

    @Test
    fun P4B1_06_date_to_picker_millis_rejects_years_outside_the_accepted_bounds() {
        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.dateToPickerMillis(LocalDate.of(0, 1, 1))
        }
        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.dateToPickerMillis(LocalDate.of(10000, 1, 1))
        }
    }

    @Test
    fun P4B1_07_picker_millis_rejects_years_outside_the_accepted_bounds() {
        val year0Millis = LocalDate.of(0, 1, 1)
            .atStartOfDay(ZoneOffset.UTC)
            .toInstant()
            .toEpochMilli()
        val year10000Millis = LocalDate.of(10000, 1, 1)
            .atStartOfDay(ZoneOffset.UTC)
            .toInstant()
            .toEpochMilli()

        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.pickerMillisToDate(year0Millis)
        }
        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.pickerMillisToDate(year10000Millis)
        }
    }

    @Test
    fun P4B1_08_build_reminder_time_has_minute_precision() {
        val reminderTime = ReminderTimeUi.buildReminderTime(
            LocalDate.of(2026, 1, 1),
            9,
            30,
        )

        assertEquals(LocalDateTime.of(2026, 1, 1, 9, 30), reminderTime)
        assertEquals(9, reminderTime.hour)
        assertEquals(30, reminderTime.minute)
        assertEquals(0, reminderTime.second)
        assertEquals(0, reminderTime.nano)
    }

    @Test
    fun P4B1_09_build_reminder_time_rejects_an_invalid_hour() {
        val date = LocalDate.of(2026, 1, 1)

        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.buildReminderTime(date, -1, 30)
        }
        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.buildReminderTime(date, 24, 30)
        }
    }

    @Test
    fun P4B1_10_build_reminder_time_rejects_an_invalid_minute() {
        val date = LocalDate.of(2026, 1, 1)

        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.buildReminderTime(date, 9, -1)
        }
        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.buildReminderTime(date, 9, 60)
        }
    }

    @Test
    fun P4B1_11_build_reminder_time_accepts_the_year_boundaries() {
        assertEquals(
            LocalDateTime.of(1, 1, 1, 0, 0),
            ReminderTimeUi.buildReminderTime(LocalDate.of(1, 1, 1), 0, 0),
        )
        assertEquals(
            LocalDateTime.of(9999, 12, 31, 23, 59),
            ReminderTimeUi.buildReminderTime(LocalDate.of(9999, 12, 31), 23, 59),
        )
    }

    @Test
    fun P4B1_12_build_reminder_time_rejects_years_outside_the_accepted_bounds() {
        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.buildReminderTime(LocalDate.of(0, 1, 1), 9, 30)
        }
        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.buildReminderTime(LocalDate.of(10000, 1, 1), 9, 30)
        }
    }

    @Test
    fun P4B1_13_leap_day_is_handled_correctly() {
        val leapDay = LocalDate.of(2024, 2, 29)

        assertEquals(
            leapDay,
            ReminderTimeUi.pickerMillisToDate(ReminderTimeUi.dateToPickerMillis(leapDay)),
        )

        val reminderTime = ReminderTimeUi.buildReminderTime(leapDay, 9, 30)

        assertEquals(LocalDateTime.of(2024, 2, 29, 9, 30), reminderTime)
        assertEquals("2024-02-29 09:30", ReminderTimeUi.formatReminderTime(reminderTime))
        assertThrows(DateTimeException::class.java) { LocalDate.of(2026, 2, 29) }
    }

    @Test
    fun P4B1_14_format_reminder_time_matches_the_frozen_display_format() {
        assertEquals(
            "2026-01-01 09:30",
            ReminderTimeUi.formatReminderTime(LocalDateTime.of(2026, 1, 1, 9, 30)),
        )
    }

    @Test
    fun P4B1_15_format_reminder_time_zero_pads_every_field() {
        assertEquals(
            "2026-01-02 03:04",
            ReminderTimeUi.formatReminderTime(LocalDateTime.of(2026, 1, 2, 3, 4)),
        )
        assertEquals(
            "0001-01-01 00:00",
            ReminderTimeUi.formatReminderTime(LocalDateTime.of(1, 1, 1, 0, 0)),
        )
        assertEquals(
            "9999-12-31 23:59",
            ReminderTimeUi.formatReminderTime(LocalDateTime.of(9999, 12, 31, 23, 59)),
        )
    }

    @Test
    fun P4B1_16_format_reminder_time_rejects_values_without_minute_precision() {
        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.formatReminderTime(LocalDateTime.of(2026, 1, 1, 9, 30, 1))
        }
        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.formatReminderTime(LocalDateTime.of(2026, 1, 1, 9, 30, 0, 1))
        }
    }

    @Test
    fun P4B1_17_format_reminder_time_rejects_years_outside_the_accepted_bounds() {
        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.formatReminderTime(LocalDateTime.of(0, 1, 1, 0, 0))
        }
        assertThrows(IllegalArgumentException::class.java) {
            ReminderTimeUi.formatReminderTime(LocalDateTime.of(10000, 1, 1, 0, 0))
        }
    }

    @Test
    fun P4B1_18_format_reminder_time_is_locale_independent() {
        val locales = listOf(
            Locale.US,
            Locale.GERMANY,
            Locale.FRANCE,
            Locale.JAPAN,
            Locale.forLanguageTag("ar-EG"),
        )

        locales.forEach { locale ->
            withDefaultFormatLocale(locale) {
                assertEquals(
                    "2026-01-01 09:30",
                    ReminderTimeUi.formatReminderTime(LocalDateTime.of(2026, 1, 1, 9, 30)),
                )
            }
        }
    }

    @Test
    fun P4B1_19_format_reminder_time_is_timezone_independent() {
        val zones = listOf("UTC", "America/Los_Angeles", "Asia/Tokyo")

        zones.forEach { zoneId ->
            withDefaultTimeZone(zoneId) {
                assertEquals(
                    "2026-01-01 09:30",
                    ReminderTimeUi.formatReminderTime(LocalDateTime.of(2026, 1, 1, 9, 30)),
                )
            }
        }
    }

    @Test
    fun P4B1_20_display_format_is_distinct_from_the_persisted_literal() {
        val display = ReminderTimeUi.formatReminderTime(LocalDateTime.of(2026, 1, 1, 9, 30))
        val persistedLiteral = "2026-01-01T09:30"

        assertEquals("2026-01-01 09:30", display)
        assertNotEquals(persistedLiteral, display)
        assertEquals(persistedLiteral.replace('T', ' '), display)
        assertEquals(' ', display[10])
        assertEquals('T', persistedLiteral[10])
        assertEquals(persistedLiteral.length, display.length)
    }

    /**
     * Runs [block] with the JVM default timezone temporarily set to [zoneId] and
     * restores the previous value afterwards, also when [block] throws.
     */
    private fun <T> withDefaultTimeZone(zoneId: String, block: () -> T): T {
        val previous = TimeZone.getDefault()
        try {
            TimeZone.setDefault(TimeZone.getTimeZone(zoneId))
            return block()
        } finally {
            TimeZone.setDefault(previous)
        }
    }

    /**
     * Runs [block] with the JVM default format locale temporarily set to
     * [locale] and restores the previous value afterwards, also when [block]
     * throws.
     */
    private fun <T> withDefaultFormatLocale(locale: Locale, block: () -> T): T {
        val previous = Locale.getDefault(Locale.Category.FORMAT)
        try {
            Locale.setDefault(Locale.Category.FORMAT, locale)
            return block()
        } finally {
            Locale.setDefault(Locale.Category.FORMAT, previous)
        }
    }
}
