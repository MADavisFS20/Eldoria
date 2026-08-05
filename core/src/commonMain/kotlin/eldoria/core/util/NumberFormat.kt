package eldoria.core.util

import kotlin.math.abs
import kotlin.math.round

/**
 * "%.1f".format(this) equivalent -- String.format is JVM-only (backed by
 * java.util.Formatter), unavailable on Kotlin/Wasm or Kotlin/JS, so QA
 * reports and any other one-decimal display formatting go through this
 * instead.
 */
fun Double.formatOneDecimal(): String {
    val negative = this < 0
    val scaled = round(abs(this) * 10).toLong()
    val whole = scaled / 10
    val frac = scaled % 10
    val sign = if (negative && (whole != 0L || frac != 0L)) "-" else ""
    return "$sign$whole.$frac"
}
