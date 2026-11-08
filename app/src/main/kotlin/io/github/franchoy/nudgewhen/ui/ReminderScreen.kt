package io.github.franchoy.nudgewhen.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Checkbox
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TimeInput
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.material3.rememberTimePickerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import io.github.franchoy.nudgewhen.domain.Reminder
import io.github.franchoy.nudgewhen.domain.ReminderController
import java.time.LocalDate
import java.time.LocalDateTime
import java.util.UUID

/**
 * Accepted calendar-year bounds of a reminder time.
 *
 * The same bounds are accepted by the domain, by the NWR3 persistence layer and
 * by the accepted Phase-1 architecture contract. They are used here only for
 * the Material3 date-picker year range and for the picker-millis reading
 * guard.
 */
private const val MIN_REMINDER_TIME_YEAR: Int = 1

private const val MAX_REMINDER_TIME_YEAR: Int = 9999

/** The two bounded steps of the reminder-time selection flow. */
private enum class TimeSelectorStep {
    DATE,
    TIME,
}

@Composable
fun ReminderScreen(
    controller: ReminderController,
    modifier: Modifier = Modifier,
) {
    var input by remember(controller) { mutableStateOf("") }
    var reminders by remember(controller) {
        mutableStateOf(controller.reminders)
    }
    var editingId by remember(controller) { mutableStateOf<String?>(null) }
    var editBuffer by remember(controller) { mutableStateOf("") }

    // Transient reminder-time selector authority.
    //
    // `remember` semantics are used deliberately, never `rememberSaveable`: an
    // unconfirmed draft is discarded on Activity recreation, and an unconfirmed
    // selector can never reopen because the picker is mounted only while
    // `timeTargetId` is non-null. The Material3 picker states may internally
    // use saveable state, but that state is discarded together with the
    // picker when the transient parent authority resets.
    var timeTargetId by remember(controller) { mutableStateOf<String?>(null) }
    var timeStep by remember(controller) { mutableStateOf(TimeSelectorStep.DATE) }
    var selectedDate by remember(controller) { mutableStateOf<LocalDate?>(null) }
    var selectedHour by remember(controller) { mutableStateOf(0) }
    var selectedMinute by remember(controller) { mutableStateOf(0) }
    val timeErrors = remember(controller) { mutableStateMapOf<String, String>() }
    // Use a fresh, non-saveable composition key for each picker opening. Material3
    // picker states may be saveable; a new key prevents an unconsumed state entry
    // from the previous Activity from restoring an abandoned picker draft.
    var timeSelectorKey by remember(controller) { mutableStateOf(UUID.randomUUID().toString()) }

    fun openTimeSelector(reminder: Reminder) {
        val existing = reminder.time
        val now = LocalDateTime.now()
        timeErrors.remove(reminder.id)
        if (existing != null) {
            selectedDate = existing.toLocalDate()
            selectedHour = existing.hour
            selectedMinute = existing.minute
        } else {
            selectedDate = now.toLocalDate()
            selectedHour = now.hour
            selectedMinute = now.minute
        }
        timeStep = TimeSelectorStep.DATE
        timeSelectorKey = UUID.randomUUID().toString()
        timeTargetId = reminder.id
    }

    fun discardTimeDraft() {
        timeTargetId = null
        selectedDate = null
        selectedHour = 0
        selectedMinute = 0
        timeStep = TimeSelectorStep.DATE
    }

    fun cancelTimeSelector() {
        timeTargetId?.let { timeErrors.remove(it) }
        discardTimeDraft()
    }

    fun reportTimeError(message: String) {
        val targetId = timeTargetId ?: return
        timeErrors[targetId] = message
    }

    fun confirmDateSelection(date: LocalDate) {
        timeTargetId?.let { timeErrors.remove(it) }
        selectedDate = date
        timeStep = TimeSelectorStep.TIME
    }

    fun confirmTimeSelection(hour: Int, minute: Int) {
        val targetId = timeTargetId ?: return
        val date = selectedDate
        if (date == null) {
            reportTimeError("Select a date before confirming the time.")
            return
        }
        val time = try {
            ReminderTimeUi.buildReminderTime(date, hour, minute)
        } catch (e: IllegalArgumentException) {
            reportTimeError("The selected date and time are not a valid reminder time.")
            return
        }
        val accepted = try {
            controller.setTime(targetId, time)
        } catch (e: Exception) {
            reportTimeError("The reminder time could not be saved.")
            return
        }
        if (!accepted) {
            reportTimeError("The reminder time could not be saved.")
            return
        }
        reminders = controller.reminders
        timeErrors.remove(targetId)
        discardTimeDraft()
    }

    fun clearReminderTime(reminder: Reminder) {
        val accepted = try {
            controller.setTime(reminder.id, null)
        } catch (e: Exception) {
            timeErrors[reminder.id] = "The reminder time could not be cleared."
            return
        }
        if (!accepted) {
            timeErrors[reminder.id] = "The reminder time could not be cleared."
            return
        }
        reminders = controller.reminders
        timeErrors.remove(reminder.id)
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp),
    ) {
        Row(modifier = Modifier.fillMaxWidth()) {
            OutlinedTextField(
                value = input,
                onValueChange = { input = it },
                modifier = Modifier.weight(1f),
                label = { Text("New reminder") },
                singleLine = true,
            )
            Button(
                onClick = {
                    val before = reminders
                    controller.create(input)
                    val after = controller.reminders
                    if (after != before) {
                        reminders = after
                        input = ""
                    }
                },
            ) {
                Text("Add")
            }
        }

        if (reminders.isEmpty()) {
            Text("No reminders")
        } else {
            LazyColumn(modifier = Modifier.weight(1f)) {
                items(items = reminders, key = { it.id }) { reminder ->
                    Column(modifier = Modifier.fillMaxWidth()) {
                        if (editingId == reminder.id) {
                            Row(modifier = Modifier.fillMaxWidth()) {
                                Checkbox(
                                    checked = reminder.done,
                                    onCheckedChange = { newChecked ->
                                        val accepted = controller.setDone(reminder.id, newChecked)
                                        if (accepted) {
                                            reminders = controller.reminders
                                        }
                                    },
                                )
                                OutlinedTextField(
                                    value = editBuffer,
                                    onValueChange = { editBuffer = it },
                                    modifier = Modifier.weight(1f),
                                    label = { Text("Edit reminder") },
                                    singleLine = true,
                                )
                                TextButton(
                                    onClick = {
                                        val activeEditingId = reminder.id
                                        val accepted = controller.edit(activeEditingId, editBuffer)
                                        if (accepted) {
                                            reminders = controller.reminders
                                            editingId = null
                                            editBuffer = ""
                                        }
                                    },
                                ) {
                                    Text("Save")
                                }
                                TextButton(
                                    onClick = {
                                        editingId = null
                                        editBuffer = ""
                                    },
                                ) {
                                    Text("Cancel")
                                }
                            }
                        } else {
                            Row(modifier = Modifier.fillMaxWidth()) {
                                Checkbox(
                                    checked = reminder.done,
                                    onCheckedChange = { newChecked ->
                                        val accepted = controller.setDone(reminder.id, newChecked)
                                        if (accepted) {
                                            reminders = controller.reminders
                                        }
                                    },
                                )
                                Text(
                                    text = reminder.text,
                                    modifier = Modifier.weight(1f),
                                )
                                TextButton(
                                    onClick = {
                                        editBuffer = reminder.text
                                        editingId = reminder.id
                                    },
                                ) {
                                    Text("Edit")
                                }
                                TextButton(
                                    onClick = {
                                        controller.remove(reminder.id)
                                        reminders = controller.reminders
                                    },
                                ) {
                                    Text("Remove")
                                }
                            }
                        }
                        ReminderTimeControls(
                            reminder = reminder,
                            errorMessage = timeErrors[reminder.id],
                            onOpenSelector = { openTimeSelector(reminder) },
                            onClearTime = { clearReminderTime(reminder) },
                        )
                    }
                }
            }
        }
    }

    timeTargetId?.let { activeTargetId ->
        key(timeSelectorKey) {
            ReminderTimeSelector(
                step = timeStep,
                initialDate = selectedDate ?: LocalDate.now(),
                initialHour = selectedHour,
                initialMinute = selectedMinute,
                errorMessage = timeErrors[activeTargetId],
                onDateConfirmed = { date -> confirmDateSelection(date) },
                onTimeConfirmed = { hour, minute -> confirmTimeSelection(hour, minute) },
                onInvalidSelection = { message -> reportTimeError(message) },
                onBackToDate = {
                    timeErrors.remove(activeTargetId)
                    timeStep = TimeSelectorStep.DATE
                },
                onCancel = { cancelTimeSelector() },
            )
        }
    }
}

/**
 * The compact reminder-time control row, rendered beneath the ordinary reminder
 * controls of both the ordinary and the text-editing reminder row.
 */
@Composable
private fun ReminderTimeControls(
    reminder: Reminder,
    errorMessage: String?,
    onOpenSelector: () -> Unit,
    onClearTime: () -> Unit,
) {
    val time = reminder.time
    Column(modifier = Modifier.fillMaxWidth()) {
        Row(modifier = Modifier.fillMaxWidth()) {
            if (time != null) {
                Text(
                    text = ReminderTimeUi.formatReminderTime(time),
                    modifier = Modifier.weight(1f),
                )
            }
            TextButton(onClick = onOpenSelector) {
                Text(if (time == null) "Set time" else "Change time")
            }
            if (time != null) {
                TextButton(onClick = onClearTime) {
                    Text("Clear time")
                }
            }
        }
        if (errorMessage != null) {
            Text(
                text = errorMessage,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}

/**
 * The bounded two-step reminder-time selector.
 *
 * Step 1 selects a calendar date with a Material3 date picker. The selected
 * picker value is read as a UTC calendar date through
 * [ReminderTimeUi.pickerMillisToDate] and is never converted through the device
 * default timezone. Step 1 never calls the controller.
 *
 * Step 2 selects the hour and minute with a compact Material3 time input in
 * 24-hour mode. The chosen calendar date is retained in the transient parent
 * state. Only an explicit confirmation commits a value, and only an accepted
 * controller result refreshes the displayed reminder state.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ReminderTimeSelector(
    step: TimeSelectorStep,
    initialDate: LocalDate,
    initialHour: Int,
    initialMinute: Int,
    errorMessage: String?,
    onDateConfirmed: (LocalDate) -> Unit,
    onTimeConfirmed: (Int, Int) -> Unit,
    onInvalidSelection: (String) -> Unit,
    onBackToDate: () -> Unit,
    onCancel: () -> Unit,
) {
    val datePickerState = rememberDatePickerState(
        initialSelectedDateMillis = ReminderTimeUi.dateToPickerMillis(initialDate),
        yearRange = MIN_REMINDER_TIME_YEAR..MAX_REMINDER_TIME_YEAR,
    )
    val timePickerState = rememberTimePickerState(
        initialHour = initialHour,
        initialMinute = initialMinute,
        is24Hour = true,
    )

    when (step) {
        TimeSelectorStep.DATE -> {
            DatePickerDialog(
                onDismissRequest = onCancel,
                confirmButton = {
                    TextButton(
                        onClick = {
                            val selectedMillis = datePickerState.selectedDateMillis
                            if (selectedMillis == null) {
                                onInvalidSelection("Select a date before continuing.")
                            } else {
                                val date = try {
                                    ReminderTimeUi.pickerMillisToDate(selectedMillis)
                                } catch (e: IllegalArgumentException) {
                                    null
                                }
                                if (date == null) {
                                    onInvalidSelection(
                                        "The selected date is outside the supported year range.",
                                    )
                                } else {
                                    onDateConfirmed(date)
                                }
                            }
                        },
                    ) {
                        Text("Next")
                    }
                },
                dismissButton = {
                    TextButton(onClick = onCancel) {
                        Text("Cancel")
                    }
                },
            ) {
                DatePicker(
                    state = datePickerState,
                    title = {
                        Text(
                            text = errorMessage ?: "Select date",
                            color = if (errorMessage == null) {
                                MaterialTheme.colorScheme.onSurfaceVariant
                            } else {
                                MaterialTheme.colorScheme.error
                            },
                            style = MaterialTheme.typography.bodySmall,
                            modifier = Modifier.padding(horizontal = 24.dp, vertical = 16.dp),
                        )
                    },
                )
            }
        }
        TimeSelectorStep.TIME -> {
            AlertDialog(
                onDismissRequest = onCancel,
                confirmButton = {
                    TextButton(
                        onClick = {
                            // The resolved Material3 `TimePickerState` exposes a
                            // non-null hour and minute, so the selection is
                            // always complete when the confirmation is pressed.
                            onTimeConfirmed(
                                timePickerState.hour,
                                timePickerState.minute,
                            )
                        },
                    ) {
                        Text("Confirm")
                    }
                },
                dismissButton = {
                    Row {
                        TextButton(onClick = onBackToDate) {
                            Text("Back")
                        }
                        TextButton(onClick = onCancel) {
                            Text("Cancel")
                        }
                    }
                },
                title = {
                    Text("Reminder time")
                },
                text = {
                    Column {
                        TimeInput(state = timePickerState)
                        if (errorMessage != null) {
                            Text(
                                text = errorMessage,
                                color = MaterialTheme.colorScheme.error,
                                style = MaterialTheme.typography.bodySmall,
                                modifier = Modifier.padding(top = 8.dp),
                            )
                        }
                    }
                },
            )
        }
    }
}
