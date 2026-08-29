package io.github.franchoy.nudgewhen.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import io.github.franchoy.nudgewhen.domain.ReminderController

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
                    if (editingId == reminder.id) {
                        Row(modifier = Modifier.fillMaxWidth()) {
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
                }
            }
        }
    }
}
