package io.github.franchoy.nudgewhen.domain

import java.time.LocalDateTime

class ReminderController(
    private val store: ReminderStore,
    private val idGenerator: () -> String,
) {
    private var state: List<Reminder> = store.load().toList()

    val reminders: List<Reminder>
        get() = state

    fun create(text: String) {
        val normalizedText = text.trim()
        if (normalizedText.isEmpty()) return

        val generatedId = idGenerator()
        validateGeneratedIdGrammar(generatedId)
        if (state.any { it.id == generatedId }) {
            throw IllegalArgumentException("Duplicate reminder id: $generatedId")
        }

        val candidate: List<Reminder> = state + Reminder(generatedId, normalizedText)
        store.save(candidate)
        state = candidate
    }

    fun remove(id: String) {
        val index = state.indexOfFirst { it.id == id }
        if (index < 0) return

        val mutableCandidate = state.toMutableList()
        mutableCandidate.removeAt(index)
        val candidate: List<Reminder> = mutableCandidate
        store.save(candidate)
        state = candidate
    }

    fun edit(id: String, text: String): Boolean {
        val index = state.indexOfFirst { it.id == id }
        if (index < 0) return false

        val normalizedText = text.trim()
        if (normalizedText.isEmpty()) return false

        if (state[index].text == normalizedText) return true

        val mutableCandidate = state.toMutableList()
        mutableCandidate[index] = state[index].copy(
            text = normalizedText,
        )
        val candidate: List<Reminder> = mutableCandidate
        store.save(candidate)
        state = candidate
        return true
    }

    fun setDone(id: String, done: Boolean): Boolean {
        val index = state.indexOfFirst { it.id == id }
        if (index < 0) return false

        if (state[index].done == done) return true

        val mutableCandidate = state.toMutableList()
        mutableCandidate[index] = state[index].copy(done = done)
        val candidate: List<Reminder> = mutableCandidate
        store.save(candidate)
        state = candidate
        return true
    }

    /**
     * Sets, replaces, or clears the optional local wall-clock time of the
     * reminder identified by [id].
     *
     * The operation order is fixed:
     *
     *  1. the reminder is looked up by its exact id;
     *  2. a missing id returns `false` immediately, without validating the
     *     supplied value and without saving;
     *  3. a non-null supplied value is validated;
     *  4. an unchanged value returns `true` without saving;
     *  5. otherwise the complete candidate list is derived, saved exactly
     *     once, and only published after the save returns successfully.
     *
     * The reminder id, text, done state, list index, neighbors, and overall
     * ordering are preserved. [idGenerator] is never invoked. A failing save
     * propagates its exception and leaves the in-memory state unchanged.
     */
    fun setTime(id: String, time: LocalDateTime?): Boolean {
        val index = state.indexOfFirst { it.id == id }
        if (index < 0) return false

        validateReminderTime(time)

        if (state[index].time == time) return true

        val mutableCandidate = state.toMutableList()
        mutableCandidate[index] = state[index].copy(time = time)
        val candidate: List<Reminder> = mutableCandidate
        store.save(candidate)
        state = candidate
        return true
    }

    private fun validateReminderTime(time: LocalDateTime?) {
        if (time == null) return

        if (time.second != 0 || time.nano != 0) {
            throw IllegalArgumentException(
                "Reminder time must have minute precision: $time",
            )
        }

        if (time.year < MIN_REMINDER_TIME_YEAR || time.year > MAX_REMINDER_TIME_YEAR) {
            throw IllegalArgumentException(
                "Reminder time year is outside the accepted bounds " +
                    "$MIN_REMINDER_TIME_YEAR..$MAX_REMINDER_TIME_YEAR: $time",
            )
        }
    }

    private fun validateGeneratedIdGrammar(id: String) {
        if (id.isEmpty() ||
            id.contains('\t') ||
            id.contains('\r') ||
            id.contains('\n')
        ) {
            throw IllegalArgumentException("Invalid generated id")
        }
    }

    private companion object {
        const val MIN_REMINDER_TIME_YEAR: Int = 1
        const val MAX_REMINDER_TIME_YEAR: Int = 9999
    }
}