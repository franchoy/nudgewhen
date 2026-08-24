package io.github.franchoy.nudgewhen

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import io.github.franchoy.nudgewhen.data.FileReminderStore
import io.github.franchoy.nudgewhen.domain.ReminderController
import io.github.franchoy.nudgewhen.ui.ReminderScreen
import io.github.franchoy.nudgewhen.ui.theme.NudgeWhenTheme
import java.io.File
import java.util.UUID

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val reminderFile = File(filesDir, "reminders-v1.txt")
        val store = FileReminderStore(reminderFile)
        val controller = ReminderController(
            store = store,
            idGenerator = { UUID.randomUUID().toString() },
        )

        setContent {
            NudgeWhenTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background,
                ) {
                    ReminderScreen(
                        controller = controller,
                        modifier = Modifier.fillMaxSize(),
                    )
                }
            }
        }
    }
}
