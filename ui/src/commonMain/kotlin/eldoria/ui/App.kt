package eldoria.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier

/**
 * Phase 3 toolchain checkpoint: a trivial screen to prove Compose
 * Multiplatform actually builds and runs on both the jvm() desktop target
 * and the wasmJs browser target in this environment (a much heavier
 * dependency than anything used through Phase 0-2) before any real game
 * screens get built on top of it. Replaced with the real character
 * creation/exploration/combat/inventory/dialogue screens once this is
 * confirmed working.
 */
@Composable
fun App() {
    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize()) {
            Column(
                modifier = Modifier.fillMaxSize(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
            ) {
                Text("Eldoria", style = MaterialTheme.typography.displayMedium)
                Text("Compose Multiplatform toolchain check -- Phase 3 in progress.")
            }
        }
    }
}
