package com.gibbernode.gibberwave

/**
 * RelayRule
 *
 * A single rule in the relay routing table.
 * Kotlin port of RelayRule dataclass in Gibberlink/scripts/upb_hub.py.
 *
 * @param sourceProtocol  Source to match.  "*" = any protocol.
 * @param intentTag       Intent to match.  "*" = any intent.
 * @param targetMode      Operational mode to broadcast on when rule fires.
 */
data class RelayRule(
    val sourceProtocol: String,   // SourceProtocol.name or "*"
    val intentTag: String,        // IntentTag.name or "*"
    val targetMode: OperationalMode,
)

/**
 * RelayRouter
 *
 * Evaluates [RelayRule] tables against incoming CommonTokens and determines
 * which (if any) mode to re-broadcast them on.
 *
 * Matching is first-match-wins, with wildcards supported.
 * Port of UniversalProtocolBridge._relay() in upb_hub.py.
 */
class RelayRouter(private val rules: List<RelayRule> = DEFAULT_RELAY_RULES) {

    /**
     * Find the first matching rule for [token].
     *
     * @return  [OperationalMode] to broadcast on, or null if no rule matches.
     */
    fun match(token: CommonToken): OperationalMode? {
        val sourceName = token.source.name
        val intentName = token.intent.name
        return rules.firstOrNull { rule ->
            (rule.sourceProtocol == "*" || rule.sourceProtocol.equals(sourceName, ignoreCase = true)) &&
            (rule.intentTag      == "*" || rule.intentTag.equals(intentName, ignoreCase = true))
        }?.targetMode
    }

    companion object {
        /**
         * Default relay rules — mirror DEFAULT_RELAY_RULES in upb_hub.py.
         *
         * Priority (first match wins):
         *   SDR/ALERT     → RED  (emergency from radio scanner)
         *   BLE/ALERT     → RED  (accessory critical alert)
         *   USB/ALERT     → RED  (external sensor critical)
         *   SYSTEM/ALERT  → RED  (sentinel watchdog anomaly)
         *   CSI/ALERT     → RED  (RF spatial intrusion)
         *   *  /RELAY     → GREEN (explicit passthrough relay)
         */
        val DEFAULT_RELAY_RULES: List<RelayRule> = listOf(
            RelayRule("SDR",    "ALERT", OperationalMode.RED),
            RelayRule("BLE",    "ALERT", OperationalMode.RED),
            RelayRule("USB",    "ALERT", OperationalMode.RED),
            RelayRule("SYSTEM", "ALERT", OperationalMode.RED),
            RelayRule("CSI",    "ALERT", OperationalMode.RED),
            RelayRule("ENERGY", "ALERT", OperationalMode.RED),
            RelayRule("*",      "RELAY", OperationalMode.GREEN),
        )
    }
}
