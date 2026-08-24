package io.github.franchoy.nudgewhen.domain

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

    private fun validateGeneratedIdGrammar(id: String) {
        if (id.isEmpty() ||
            id.contains('\t') ||
            id.contains('\r') ||
            id.contains('\n')
        ) {
            throw IllegalArgumentException("Invalid generated id")
        }
    }
}