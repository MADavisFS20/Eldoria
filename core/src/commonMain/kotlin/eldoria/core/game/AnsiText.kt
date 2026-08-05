package eldoria.core.game

/**
 * Color spec locked in for the text log (see project memory): surroundings
 * and movement text are white, items are yellow, hostile beings are red,
 * passive/non-hostile NPCs are blue. `enabled = false` strips all codes for
 * terminals that don't support ANSI.
 */
object AnsiText {
    private const val RESET = "[0m"
    private const val WHITE = "[37m"
    private const val YELLOW = "[33m"
    private const val RED = "[31m"
    private const val BLUE = "[34m"
    private const val GREEN = "[32m"
    private const val CYAN = "[36m"
    private const val BOLD = "[1m"
    private const val DIM = "[2m"

    var enabled: Boolean = true

    private fun wrap(code: String, s: String): String = if (enabled) "$code$s$RESET" else s

    fun white(s: String) = wrap(WHITE, s)
    fun yellow(s: String) = wrap(YELLOW, s)
    fun red(s: String) = wrap(RED, s)
    fun blue(s: String) = wrap(BLUE, s)
    fun green(s: String) = wrap(GREEN, s)
    fun cyan(s: String) = wrap(CYAN, s)
    fun bold(s: String) = wrap(BOLD, s)
    fun dim(s: String) = wrap(DIM, s)
}
