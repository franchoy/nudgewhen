package io.github.franchoy.nudgewhen.ui

import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.time.format.ResolverStyle
import java.util.Locale

/**
 * Pure date/time conversion and formatting helpers for the v0.1.5 reminder-time
 * user interface.
 *
 * The helper deliberately imports nothing but `java.time`: it contains no Compose
 * and no Android framework dependency, owns no Compose state, and is therefore
 * directly testable on the JVM. It is the deterministic core that the Phase-4
 * Compose integration will call; this file does not perform that integration.
 *
 * Contract references — frozen Phase-1 architecture contract
 * `docs/releases/v0.1.5/reminder-time-architecture.md`:
 *
 *  * §8.5 — a Material3 picker's selected date is a UTC-midnight millisecond
 *    value. The calendar date is read under a UTC calendar-date convention and
 *    is never converted through the device default timezone, which would shift
 *    the selected day in zones west of UTC.
 *  * §2.1 / §2.2 — an accepted reminder time has minute precision and a
 *    calendar year in `1..9999`. Invalid input is rejected, never clamped or
 *    truncated.
 *  * §8.6 — the accepted display format is `yyyy-MM-dd HH:mm`, deliberately
 *    distinct from the persisted NWR3 literal `uuuu-MM-dd'T'HH:mm`.
 */
internal object ReminderTimeUi {

    /** Lowest accepted calendar year. */
    private const val MIN_YEAR: Int = 1

    /** Highest accepted calendar year. */
    private const val MAX_YEAR: Int = 9999

    /**
     * Deterministic, locale-independent display formatter.
     *
     * The frozen display format is `yyyy-MM-dd HH:mm`. The proleptic-year field
     * `uuuu` is used instead of the year-of-era field `yyyy` because the
     * accepted range `0001..9999` lies entirely in the Common Era, so the
     * emitted text is identical to the frozen specification, while `uuuu` has no
     * era-resolution dependency and always emits a zero-padded four-digit year.
     *
     * This formatter is display-only. It is deliberately separate from, and does
     * not reuse or modify, the NWR3 persistence formatter.
     */
    private val DISPLAY_FORMATTER: DateTimeFormatter =
        DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm")
            .withResolverStyle(ResolverStyle.STRICT)
            .withLocale(Locale.ROOT)

    /**
     * Reads the selected calendar date from a Material3 picker millisecond value.
     *
     * The value is interpreted under a UTC calendar-date convention, so the
     * selected calendar day never shifts with the device default timezone.
     *
     * @throws IllegalArgumentException if the resulting calendar year is outside
     *   the accepted range `1..9999`.
     */
    fun pickerMillisToDate(selectedDateMillis: Long): LocalDate {
        val date = Instant.ofEpochMilli(selectedDateMillis)
            .atZone(ZoneOffset.UTC)
            .toLocalDate()
        requireAcceptedYear(date.year)
        return date
    }

    /**
     * Encodes a calendar date as the UTC-midnight millisecond value that a
     * Material3 date picker uses for that date.
     *
     * @throws IllegalArgumentException if the calendar year is outside the
     *   accepted range `1..9999`.
     */
    fun dateToPickerMillis(date: LocalDate): Long {
        requireAcceptedYear(date.year)
        return date.atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli()
    }

    /**
     * Builds the timezone-free local wall-clock reminder time for a selected
     * calendar date and a selected hour and minute.
     *
     * The result carries minute precision: its second and nanosecond components
     * are always zero. Epoch milliseconds are never used as the reminder-time
     * representation.
     *
     * @throws IllegalArgumentException if the calendar year is outside the
     *   accepted range `1..9999`, if the hour is outside `0..23`, or if the
     *   minute is outside `0..59`. Invalid input is rejected, never clamped.
     */
    fun buildReminderTime(date: LocalDate, hour: Int, minute: Int): LocalDateTime {
        requireAcceptedYear(date.year)
        require(hour in 0..23) { "Reminder hour must be in 0..23: $hour" }
        require(minute in 0..59) { "Reminder minute must be in 0..59: $minute" }
        return LocalDateTime.of(date, LocalTime.of(hour, minute))
    }

    /**
     * Formats a reminder time for display using the frozen display format
     * `yyyy-MM-dd HH:mm`, for example `2026-01-01 09:30`.
     *
     * The formatting is deterministic and locale-independent.
     *
     * @throws IllegalArgumentException if the value carries a non-zero second
     *   or nanosecond component, or if its calendar year is outside the accepted
     *   range `1..9999`.
     */
    fun formatReminderTime(time: LocalDateTime): String {
        requireAcceptedYear(time.year)
        require(time.second == 0 && time.nano == 0) {
            "Reminder time must have minute precision: $time"
        }
        return DISPLAY_FORMATTER.format(time)
    }

    /**
     * Rejects a calendar year outside the accepted range `1..9999`.
     */
    private fun requireAcceptedYear(year: Int) {
        require(year in MIN_YEAR..MAX_YEAR) {
            "Reminder time year is outside the accepted bounds " +
                "$MIN_YEAR..$MAX_YEAR: $year"
        }
    }
}
