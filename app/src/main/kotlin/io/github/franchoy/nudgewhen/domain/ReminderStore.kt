package io.github.franchoy.nudgewhen.domain

interface ReminderStore {
    fun load(): List<Reminder>
    fun save(reminders: List<Reminder>)
}