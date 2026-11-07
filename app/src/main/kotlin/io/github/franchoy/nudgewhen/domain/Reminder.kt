package io.github.franchoy.nudgewhen.domain

import java.time.LocalDateTime

data class Reminder(
    val id: String,
    val text: String,
    val done: Boolean = false,
    val time: LocalDateTime? = null,
)