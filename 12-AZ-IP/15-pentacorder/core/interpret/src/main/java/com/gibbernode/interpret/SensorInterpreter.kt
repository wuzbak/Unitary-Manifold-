package com.gibbernode.interpret

import kotlin.math.abs
import kotlin.math.sqrt

/**
 * SensorInterpreter
 *
 * The Ψ_AI body of the Pentacorder.  Takes raw sensor readings from the
 * TricorderViewModel plus the user's active role and produces a
 * human-readable SituationReport that closes the Information Gap between
 * the Physical Manifold (Ψ_univ) and the Intent Layer (Ψ_human).
 *
 * Interpretation is *composited* — five sensors together tell a story that
 * none tells alone.  For example:
 *   barometric drop + magnetometer spike → gas pocket / structural instability
 *   high HR + low SpO₂ + low pressure → hypoxia risk at altitude
 *   vibration peak + thermal spike → machinery fault
 *
 * All thresholds are based on published standards:
 *   - Barometric: NOAA / Met Office weather thresholds
 *   - Accelerometer: ISO 10816 vibration classification
 *   - Magnetometer: WHO EMF guidelines + Earth normal ~25–65 µT
 *   - Vital signs: NHS NEWS2, WHO normal ranges
 *   - Battery thermal: Qualcomm throttle spec / Samsung S24 Ultra TDP
 *   - Heat index: Rothfusz equation (NOAA Technical Attachment SR 90-23)
 *
 * @see UserRole
 * @see SituationReport
 * @see PentadState
 */
object SensorInterpreter {

    // ── Physical constants ────────────────────────────────────────────────────

    /**
     * ISA (International Standard Atmosphere) approximation:
     * ~0.12 hPa pressure drop per metre of altitude near sea level.
     * Source: ICAO Doc 7488-CD, standard lapse rate 0.0065 K/m at ISA MSL.
     */
    private const val HPA_PER_METER_ISA = 0.12f

    /**
     * Earth's mean surface magnetic field strength used as the interpretation
     * baseline.  Actual range: ~25 µT (equatorial) to ~65 µT (polar).
     * Mid-latitude average ≈ 45 µT (IGRF-13 model).
     */
    private const val EARTH_FIELD_UT = 45f

    /**
     * Number of sensor categories assessed in [calculateConfidence].
     * Update this constant if new sensor checks are added to that function.
     */
    private const val CONFIDENCE_SENSOR_COUNT = 7

    // ── Public entry point ────────────────────────────────────────────────────

    /**
     * Interpret a snapshot of all sensor readings through the lens of [role].
     *
     * @param sensors  Full raw sensor snapshot (mirrors TricorderUiState fields).
     * @param role     Active user role — controls which aspects are emphasised.
     * @param pentad   Current Pentad state, updated with this call's results.
     * @return         A [SituationReport] with overall severity, narrative, and actions.
     */
    fun interpret(
        sensors: SensorSnapshot,
        role:    UserRole,
        pentad:  PentadState = PentadState(),
    ): SituationReport {
        val findings = mutableListOf<Finding>()

        // ── Individual sensor interpretation ──────────────────────────────────
        interpretBarometer(sensors, role, findings)
        interpretAccelerometer(sensors, role, findings)
        interpretMagnetometer(sensors, role, findings)
        interpretLight(sensors, role, findings)
        interpretGps(sensors, role, findings)
        interpretBattery(sensors, role, findings)
        interpretVitals(sensors, role, findings)
        interpretEnvironment(sensors, role, findings)

        // ── Composite multi-sensor findings ───────────────────────────────────
        interpretComposite(sensors, role, findings)

        // ── Overall severity = worst individual finding ────────────────────────
        val maxSeverity = findings.maxByOrNull { it.severity.ordinal }?.severity
            ?: Severity.OK

        // ── Narrative: lead with the most severe findings ─────────────────────
        val narrative = buildNarrative(findings, role)

        // ── Recommended actions ────────────────────────────────────────────────
        val actions = findings
            .filter { it.action != null }
            .sortedByDescending { it.severity.ordinal }
            .take(3)
            .mapNotNull { it.action }

        // ── Update Pentad Ψ_univ based on sensor quality ──────────────────────
        val okCount    = findings.count { it.severity == Severity.OK }
        val totalCount = findings.size.coerceAtLeast(1)
        val newPhiUniv = (okCount.toFloat() / totalCount).coerceIn(0f, 1f)
        val updatedPentad = pentad.copy(phiUniv = newPhiUniv)

        return SituationReport(
            severity    = maxSeverity,
            narrative   = narrative,
            actions     = actions,
            findings    = findings,
            pentad      = updatedPentad,
            confidence  = calculateConfidence(sensors),
        )
    }

    // ── Sensor interpreters ───────────────────────────────────────────────────

    private fun interpretBarometer(s: SensorSnapshot, role: UserRole, out: MutableList<Finding>) {
        if (s.pressureHpa <= 0f) return

        val p = s.pressureHpa

        // Weather classification
        val weatherDesc = when {
            p >= 1020f -> "HIGH pressure — stable, clear conditions"
            p in 1005f..1019.9f -> "NORMAL pressure — typical surface conditions"
            p in 980f..1004.9f  -> "LOW pressure — cloudy, possible precipitation"
            p in 960f..979.9f   -> "VERY LOW — storm conditions likely"
            else                -> "EXTREME LOW (${p.toInt()} hPa) — severe weather / underground"
        }

        // Altitude estimate (barometric formula — ISA standard atmosphere)
        val altEst = if (p < 1013.25f) ((1013.25f - p) / HPA_PER_METER_ISA).toInt() else 0

        // Trend (this call only has snapshot — trend requires history; noted for future)
        val severity = when {
            p < 960f  -> Severity.CRITICAL
            p < 980f  -> Severity.WARNING
            p > 1040f -> Severity.CAUTION
            else      -> Severity.OK
        }

        val roleContext = when (role) {
            UserRole.NURSE -> when {
                p < 990f -> "Low pressure environment — consider increased respiratory effort for patients with COPD/asthma. " +
                    "Altitude ~${altEst}m: SpO₂ may read 2–4% lower than sea-level."
                else -> "Pressure ${p.toInt()} hPa — no significant clinical effect on patient."
            }
            UserRole.FIRST_RESPONDER -> when {
                p < 950f -> "⚠ EXTREME LOW: possibly underground / collapsed structure. " +
                    "CBRN check: gas pockets possible. Do NOT enter without air supply."
                p < 980f -> "Storm conditions: evacuation may be compromised. " +
                    "Structural risk elevated if pressure falling rapidly."
                else -> "Barometric: $weatherDesc"
            }
            UserRole.ENGINEER -> when {
                p < 970f -> "Sub-970 hPa: affects pneumatic systems, differential pressure sensors, " +
                    "and sealed equipment rated to standard atmosphere. Verify calibration."
                else -> "$weatherDesc — altitude ~${altEst}m above sea level"
            }
            UserRole.SCIENTIST -> "B_4 = ${p} hPa — compact dimension pressure proxy. " +
                "Δ from ISA = %.1f hPa".format(p - 1013.25f)
            UserRole.DEFAULT -> "$weatherDesc (${p.toInt()} hPa)"
        }

        out += Finding(
            sensor    = "Barometer",
            rawValue  = "%.1f hPa".format(p),
            context   = roleContext,
            severity  = severity,
            action    = if (severity >= Severity.WARNING) roleBarometerAction(p, role) else null,
        )
    }

    private fun roleBarometerAction(p: Float, role: UserRole): String = when (role) {
        UserRole.FIRST_RESPONDER -> if (p < 960f)
            "Initiate air quality check. Do not enter enclosed space without SCBA."
            else "Monitor pressure trend. Brief team on storm risk."
        UserRole.NURSE  -> "Check patient SpO₂ and respiratory rate. Document environment."
        UserRole.ENGINEER -> "Verify pneumatic / pressure-rated equipment calibration."
        else -> "Monitor barometric trend."
    }

    private fun interpretAccelerometer(s: SensorSnapshot, role: UserRole, out: MutableList<Finding>) {
        val mag = s.accelMag
        if (mag == 0f) return

        val gravDelta = abs(mag - 9.81f)

        // Vibration frequency hint from linear acceleration magnitude
        val linMag = sqrt(
            (s.linAccX * s.linAccX + s.linAccY * s.linAccY + s.linAccZ * s.linAccZ).toDouble()
        ).toFloat()

        val severity = when {
            gravDelta > 8f  -> Severity.CRITICAL  // free-fall or severe impact
            gravDelta > 4f  -> Severity.WARNING   // significant movement / impact
            linMag > 10f    -> Severity.CAUTION   // high vibration
            else            -> Severity.OK
        }

        val roleContext = when (role) {
            UserRole.NURSE -> when {
                gravDelta > 8f -> "FALL DETECTED — device in free-fall or severe impact. Check patient for trauma."
                gravDelta > 4f -> "High acceleration event. Patient or operator may have fallen."
                linMag > 5f    -> "Vibration noted — if patient is on monitoring equipment, verify sensor contact."
                else -> "Stable — no significant motion detected."
            }
            UserRole.FIRST_RESPONDER -> when {
                gravDelta > 8f -> "⚠ IMPACT EVENT — possible structural collapse or fall. Check team safety."
                linMag > 15f   -> "High vibration ${linMag.toInt()} m/s² — possible seismic activity, heavy machinery, or explosion."
                linMag > 5f    -> "Vibration signature detected — identify source. Vehicle? Machinery? Structural stress?"
                else -> "Stable platform — no significant vibration."
            }
            UserRole.ENGINEER -> when {
                linMag > 20f -> "SEVERE vibration ${linMag.toInt()} m/s² — exceeds ISO 10816 Class C limit for rigid mounts. " +
                    "Imbalance, cavitation, or bearing failure likely."
                linMag > 10f -> "Moderate vibration ${linMag.toInt()} m/s² — ISO 10816 caution zone. " +
                    "Check rotating machinery alignment and bearing wear."
                linMag > 3f  -> "Low vibration ${linMag.toInt()} m/s² — within normal operating range for most equipment."
                else -> "No significant vibration — good platform stability."
            }
            UserRole.SCIENTIST -> "|a| = ${mag} m/s²  |Δg| = %.2f m/s²  |linAcc| = %.2f m/s²".format(gravDelta, linMag)
            UserRole.DEFAULT   -> when {
                gravDelta > 8f -> "FALL or impact detected!"
                linMag > 10f   -> "High vibration environment (${linMag.toInt()} m/s²)"
                else -> "Stable — acceleration normal (${mag.toInt()} m/s²)"
            }
        }

        out += Finding(
            sensor   = "Accelerometer",
            rawValue = "|a| = %.2f m/s²  |lin| = %.2f m/s²".format(mag, linMag),
            context  = roleContext,
            severity = severity,
            action   = if (severity >= Severity.WARNING) when (role) {
                UserRole.NURSE -> "Perform patient fall assessment. Check for injury."
                UserRole.FIRST_RESPONDER -> "Assess team safety. Look for structural damage."
                UserRole.ENGINEER -> "Shut down affected equipment. Perform vibration analysis."
                else -> "Investigate sudden acceleration event."
            } else null,
        )
    }

    private fun interpretMagnetometer(s: SensorSnapshot, role: UserRole, out: MutableList<Finding>) {
        val mag = s.magMag
        if (mag == 0f) return

        val deviation   = abs(mag - EARTH_FIELD_UT)

        val severity = when {
            mag > 200f       -> Severity.CRITICAL  // near strong electrical/industrial field
            mag > 100f       -> Severity.WARNING   // likely near power lines / heavy machinery
            deviation > 30f  -> Severity.CAUTION   // notable deviation from Earth normal
            else             -> Severity.OK
        }

        val roleContext = when (role) {
            UserRole.NURSE -> when {
                mag > 100f -> "Strong EM field detected (${mag.toInt()} µT). " +
                    "MRI / strong magnets nearby? Keep pacemaker patients away. " +
                    "Implanted devices may be affected."
                mag > 60f  -> "Elevated EM field (${mag.toInt()} µT). Verify no MRI / industrial equipment nearby."
                else -> "EM field normal (${mag.toInt()} µT) — no implant risk detected."
            }
            UserRole.FIRST_RESPONDER -> when {
                mag > 200f -> "⚠ EXTREME EM field ${mag.toInt()} µT — energised conductor, transformer, or MRI nearby. " +
                    "Risk of cardiac device interference. Keep 3m+ clearance."
                mag > 100f -> "High EM field ${mag.toInt()} µT — probable electrical infrastructure nearby. " +
                    "Check for hidden wiring. Compass unreliable — use GPS bearing."
                mag < 15f  -> "Abnormally WEAK field ${mag.toInt()} µT — possible ferromagnetic shielding " +
                    "or underground metallic structure. Compass unreliable."
                else -> "EM field normal — no electrical hazards indicated. Compass reliable."
            }
            UserRole.ENGINEER -> when {
                mag > 150f -> "Strong field ${mag.toInt()} µT — energised HV cable, transformer, or motor within ~2m. " +
                    "Check arc flash risk. Verify PPE."
                mag > 80f  -> "Elevated field ${mag.toInt()} µT — probable powered equipment nearby. " +
                    "Isolate before working on adjacent conductors."
                deviation > 25f -> "Field deviation ${deviation.toInt()} µT from Earth normal (${EARTH_FIELD_UT.toInt()} µT) — " +
                    "ferromagnetic material or AC interference present."
                else -> "Field ${mag.toInt()} µT — within Earth normal range. No electrical anomalies."
            }
            UserRole.SCIENTIST -> "H_μν = ${mag} µT  (|B| - |B_earth| = %.1f µT)".format(mag - EARTH_FIELD_UT)
            UserRole.DEFAULT   -> when {
                mag > 100f -> "High magnetic field (${mag.toInt()} µT) — electrical equipment nearby"
                mag < 15f  -> "Weak magnetic field — compass unreliable"
                else -> "Magnetic field normal (${mag.toInt()} µT)"
            }
        }

        out += Finding(
            sensor   = "Magnetometer",
            rawValue = "%.1f µT".format(mag),
            context  = roleContext,
            severity = severity,
            action   = if (severity >= Severity.WARNING) when (role) {
                UserRole.NURSE -> "Move pacemaker/implant patients away from field source immediately."
                UserRole.FIRST_RESPONDER -> "Do not approach source. Locate and isolate power supply."
                UserRole.ENGINEER -> "Verify arc flash boundary. Don insulated PPE before proceeding."
                else -> "Identify and move away from EM field source."
            } else null,
        )
    }

    private fun interpretLight(s: SensorSnapshot, role: UserRole, out: MutableList<Finding>) {
        val lux = s.lightLux
        if (lux == 0f) return

        val desc = when {
            lux < 1f    -> "DARKNESS / night (${lux} lux)"
            lux < 50f   -> "DIM indoor (${lux.toInt()} lux)"
            lux < 500f  -> "Normal indoor (${lux.toInt()} lux)"
            lux < 2000f -> "Bright indoor / overcast outdoor (${lux.toInt()} lux)"
            lux < 10000f-> "Full daylight (${lux.toInt()} lux)"
            else        -> "DIRECT SUNLIGHT (${lux.toInt()} lux)"
        }

        // UV index estimate (rough proxy — lux to UV-I correlation at sea level)
        val uvEstimate = when {
            lux > 50000f -> "UV Index ~10+ (VERY HIGH)"
            lux > 30000f -> "UV Index ~7–9 (HIGH)"
            lux > 10000f -> "UV Index ~3–6 (MODERATE)"
            else         -> "UV Index LOW"
        }

        val severity = when {
            lux < 1f    -> Severity.CAUTION  // working in darkness
            lux > 50000f -> Severity.CAUTION // high UV
            else         -> Severity.OK
        }

        val roleContext = when (role) {
            UserRole.NURSE -> when {
                lux < 10f -> "LOW LIGHT — pupillary exam will be unreliable. Use torch. " +
                    "Document lighting conditions for patient assessment."
                lux > 50000f -> "Direct sun exposure — $uvEstimate. " +
                    "If patient outdoors: skin protection needed. Consider heat stroke risk."
                else -> "$desc — adequate for clinical assessment."
            }
            UserRole.FIRST_RESPONDER -> when {
                lux < 1f -> "DARKNESS — activate torch. 360° visual sweep required before entry. " +
                    "Night-vision / thermal recommended."
                lux < 50f -> "DIM conditions — reduced visibility. Use caution on uneven terrain."
                else -> "$desc — $uvEstimate"
            }
            UserRole.ENGINEER -> when {
                lux < 50f -> "Insufficient light for visual inspection (${lux.toInt()} lux). " +
                    "Minimum 200 lux required for mechanical work (IEC 60364)."
                else -> "$desc — $uvEstimate"
            }
            else -> "$desc — $uvEstimate"
        }

        out += Finding(
            sensor   = "Ambient Light",
            rawValue = "%.0f lux".format(lux),
            context  = roleContext,
            severity = severity,
            action   = if (lux < 50f && severity >= Severity.CAUTION)
                "Improve lighting before proceeding." else null,
        )
    }

    private fun interpretGps(s: SensorSnapshot, role: UserRole, out: MutableList<Finding>) {
        if (s.latitude == 0.0 && s.longitude == 0.0) return

        val altM  = s.altitude.toFloat()
        val accM  = s.gpsAccM
        val speed = s.gpsSpeedMs

        val altDesc = when {
            altM > 3000f -> "HIGH ALTITUDE (${altM.toInt()}m) — hypoxia risk above 2500m"
            altM > 1500f -> "Moderate altitude (${altM.toInt()}m)"
            altM < -10f  -> "BELOW SEA LEVEL (${altM.toInt()}m) — possible underground / tunnel"
            else         -> "Altitude ${altM.toInt()}m"
        }

        val severity = when {
            altM > 3000f  -> Severity.WARNING
            altM < -10f   -> Severity.CAUTION
            accM > 100f   -> Severity.CAUTION  // very poor GPS fix
            else          -> Severity.OK
        }

        val roleContext = when (role) {
            UserRole.NURSE -> when {
                altM > 2500f -> "⚠ HIGH ALTITUDE — SpO₂ normally 2–4% lower. " +
                    "Adjust NEWS2 SpO₂ thresholds. Watch for AMS symptoms: headache, nausea, ataxia."
                altM > 1500f -> "Moderate altitude (${altM.toInt()}m) — mild SpO₂ reduction expected."
                else -> "$altDesc  •  GPS acc ±${accM.toInt()}m"
            }
            UserRole.FIRST_RESPONDER -> {
                val coordStr = "%.5f, %.5f".format(s.latitude, s.longitude)
                buildString {
                    append("Position: $coordStr  $altDesc")
                    if (speed > 5f) append("  Moving: %.0f m/s (%.0f km/h)".format(speed, speed * 3.6f))
                    if (accM > 50f) append("  ⚠ Poor GPS fix (±${accM.toInt()}m) — verify position")
                    if (altM < -10f) append("  ⚠ Below ground level — underground structure")
                }
            }
            UserRole.ENGINEER -> "$altDesc  •  Accuracy ±${accM.toInt()}m  •  Speed ${speed} m/s"
            UserRole.SCIENTIST -> "λ = (%.6f, %.6f)  h = %.1fm  ±%.1fm".format(s.latitude, s.longitude, altM, accM)
            UserRole.DEFAULT -> "$altDesc  •  ±${accM.toInt()}m accuracy"
        }

        out += Finding(
            sensor   = "GPS",
            rawValue = "%.5f, %.5f  alt %.0fm".format(s.latitude, s.longitude, altM),
            context  = roleContext,
            severity = severity,
            action   = if (altM > 3000f) "Monitor SpO₂ closely. Consider oxygen supplementation." else null,
        )
    }

    private fun interpretBattery(s: SensorSnapshot, role: UserRole, out: MutableList<Finding>) {
        val pct  = s.batteryPct
        val temp = s.batteryTempC
        if (pct < 0) return

        val severity = when {
            temp > 45f -> Severity.CRITICAL  // thermal runaway risk
            temp > 40f -> Severity.WARNING
            pct <= 5   -> Severity.CRITICAL
            pct <= 15  -> Severity.WARNING
            pct <= 30  -> Severity.CAUTION
            else       -> Severity.OK
        }

        val thermalDesc = when {
            temp > 45f -> "OVERHEATING ${temp.toInt()}°C — thermal throttle active, camera/sensors degraded"
            temp > 40f -> "HIGH TEMP ${temp.toInt()}°C — reduce load, avoid direct sun"
            temp > 35f -> "WARM ${temp.toInt()}°C — normal under load"
            else       -> "Normal ${temp.toInt()}°C"
        }

        val timeEstMin = if (pct > 0 && temp < 45f) (pct * 3) else 0 // very rough: ~3 min/pct
        val timeStr    = if (timeEstMin > 60) "${timeEstMin / 60}h ${timeEstMin % 60}m est."
                         else "${timeEstMin}min est."

        val roleContext = when (role) {
            UserRole.NURSE -> when {
                pct <= 15 -> "LOW BATTERY $pct% — $timeStr until device shutdown. " +
                    "Ensure all patient data is synced / saved NOW. Connect charger."
                temp > 40f -> "$thermalDesc — some sensor accuracy may be reduced (HR, temp)."
                else -> "Battery $pct% $thermalDesc — sufficient for current session."
            }
            UserRole.FIRST_RESPONDER -> when {
                pct <= 15 -> "⚠ LOW BATTERY $pct% ($timeStr) — comms window closing. " +
                    "Transmit GPS + status NOW on RED mode before shutdown."
                temp > 45f -> "⚠ DEVICE OVERHEATING — GPS / sensors may give incorrect readings. " +
                    "Shield device from heat source. Critical data may be lost."
                else -> "Battery $pct% — $timeStr operational window. $thermalDesc"
            }
            UserRole.ENGINEER, UserRole.SCIENTIST ->
                "φ energy scalar: $pct%  T_bat=${temp}°C  $timeStr"
            UserRole.DEFAULT -> "Battery $pct% $thermalDesc"
        }

        out += Finding(
            sensor   = "Battery",
            rawValue = "$pct%  ${temp}°C",
            context  = roleContext,
            severity = severity,
            action   = when {
                pct <= 5   -> "Connect charger IMMEDIATELY. Device failure imminent."
                pct <= 15  -> "Connect charger. Transmit critical data now."
                temp > 45f -> "Remove device from heat. Stop high-load tasks."
                else       -> null
            },
        )
    }

    private fun interpretVitals(s: SensorSnapshot, role: UserRole, out: MutableList<Finding>) {
        val hr = s.heartRateBpm
        if (hr <= 0) return

        val hrClass = when {
            hr < 40  -> "BRADYCARDIA (SEVERE) — <40 bpm. Life-threatening."
            hr < 60  -> "Bradycardia — <60 bpm."
            hr in 60..100 -> "Normal — ${hr} bpm."
            hr in 101..109 -> "Mild tachycardia — ${hr} bpm."
            hr in 110..130 -> "TACHYCARDIA — ${hr} bpm."
            else -> "SEVERE TACHYCARDIA — ${hr} bpm. Urgent assessment needed."
        }

        val severity = when {
            hr < 40 || hr > 150 -> Severity.CRITICAL
            hr < 50 || hr > 130 -> Severity.WARNING
            hr < 60 || hr > 100 -> Severity.CAUTION
            else                -> Severity.OK
        }

        // NEWS2 HR score
        val news2Hr = when {
            hr <= 40  -> 3
            hr <= 50  -> 1
            hr in 51..90  -> 0
            hr in 91..110 -> 1
            hr in 111..130 -> 2
            else -> 3
        }

        val roleContext = when (role) {
            UserRole.NURSE -> buildString {
                appendLine(hrClass)
                appendLine("NEWS2 HR score: +$news2Hr")
                if (hr > 100) {
                    appendLine("Possible causes: pain, fever (check temp), dehydration, hypovolaemia, infection, anxiety.")
                    if (hr > 130) appendLine("Consider: arrhythmia, PE, sepsis. ECG if available.")
                }
                if (hr < 60) appendLine("Check medications: beta-blockers? Check for AV block.")
            }.trim()
            UserRole.FIRST_RESPONDER -> when {
                hr > 120 -> "TACHYCARDIA $hr bpm — possible SHOCK/haemorrhage. " +
                    "Check BP, pallor, capillary refill. Treat for hypovolaemia if suspected."
                hr < 50  -> "BRADYCARDIA $hr bpm — possible head injury, hypothermia, vagal response."
                else -> "$hrClass — no immediate cardiac concern."
            }
            UserRole.SCIENTIST -> "J^μ_inf = ${hr} bpm  NEWS2_HR = +$news2Hr  φ-homeostasis ${if (hr in 60..100) "STABLE" else "DEVIATED"}"
            else -> hrClass
        }

        out += Finding(
            sensor   = "Heart Rate",
            rawValue = "$hr bpm",
            context  = roleContext,
            severity = severity,
            action   = if (severity >= Severity.WARNING) when {
                hr < 40  -> "CPR assessment. Call emergency services."
                hr > 150 -> "Urgent medical assessment. Prepare AED."
                else     -> "Reassess vitals. Consider clinical cause."
            } else null,
        )
    }

    private fun interpretEnvironment(s: SensorSnapshot, role: UserRole, out: MutableList<Finding>) {
        val temp     = s.ambientTempC
        val humidity = s.humidityPct
        if (temp == 0f && humidity == 0f) return

        val tempDesc = when {
            temp > 40f  -> "EXTREME HEAT ${temp.toInt()}°C — heat stroke risk"
            temp > 35f  -> "HOT ${temp.toInt()}°C — heat exhaustion risk"
            temp > 28f  -> "Warm ${temp.toInt()}°C"
            temp in 18f..28f -> "Comfortable ${temp.toInt()}°C"
            temp in 10f..17.9f -> "Cool ${temp.toInt()}°C"
            temp in 0f..9.9f   -> "COLD ${temp.toInt()}°C — hypothermia risk for vulnerable"
            temp < 0f   -> "FREEZING ${temp.toInt()}°C — hypothermia risk"
            else -> "${temp.toInt()}°C"
        }

        val humDesc = when {
            humidity > 80f -> "HIGH humidity ${humidity.toInt()}% — heat stress amplified, mould risk"
            humidity < 20f -> "LOW humidity ${humidity.toInt()}% — respiratory irritation, static risk"
            else           -> "Humidity ${humidity.toInt()}%"
        }

        val heatIndex = computeHeatIndex(temp, humidity)
        val severity = when {
            temp > 40f || heatIndex > 41f -> Severity.WARNING
            temp < 0f                     -> Severity.WARNING
            temp > 35f                    -> Severity.CAUTION
            else                          -> Severity.OK
        }

        val roleContext = when (role) {
            UserRole.NURSE -> buildString {
                appendLine("$tempDesc  •  $humDesc")
                if (temp > 35f) appendLine("Patient risk: heat exhaustion / stroke. Cool patient. Oral hydration if conscious.")
                if (temp < 5f)  appendLine("Patient risk: hypothermia. Warm patient, monitor core temp.")
                if (humidity > 80f && temp > 28f)
                    appendLine("High heat-humidity index: effective temp ~${heatIndex.toInt()}°C — fans alone insufficient.")
            }.trim()
            UserRole.FIRST_RESPONDER -> buildString {
                appendLine("$tempDesc  •  $humDesc")
                if (temp > 35f) appendLine("Team risk: heat exhaustion after ~30min exertion. Rotate crews. Hydrate.")
                if (temp < 5f)  appendLine("Hypothermia risk: PPE must include insulation for victims.")
                if (heatIndex > 40f) appendLine("Heat index ${heatIndex.toInt()}°C — limit to 20min exertion cycles.")
            }.trim()
            else -> "$tempDesc  •  $humDesc"
        }

        out += Finding(
            sensor   = "Environment",
            rawValue = "${temp.toInt()}°C  ${humidity.toInt()}%",
            context  = roleContext,
            severity = severity,
            action   = when {
                temp > 40f -> "Remove people from heat. Emergency cooling. Call medical."
                temp < 0f  -> "Insulate victims. Warm fluids if available. Monitor core temp."
                else -> null
            },
        )
    }

    // ── Composite multi-sensor analysis ──────────────────────────────────────

    private fun interpretComposite(s: SensorSnapshot, role: UserRole, out: MutableList<Finding>) {
        val pressure = s.pressureHpa
        val magMag   = s.magMag
        val linMag   = sqrt(
            (s.linAccX * s.linAccX + s.linAccY * s.linAccY + s.linAccZ * s.linAccZ).toDouble()
        ).toFloat()

        // Pattern: low pressure + high EM → structural gas pocket / buried cable
        if (pressure in 1f..960f && magMag > 80f && role == UserRole.FIRST_RESPONDER) {
            out += Finding(
                sensor   = "⚠ COMPOSITE",
                rawValue = "P=${pressure.toInt()} hPa  B=${magMag.toInt()} µT",
                context  = "LOW PRESSURE + HIGH EM FIELD detected simultaneously. " +
                    "Pattern: possible buried energised cable + structural void, or underground utility fault. " +
                    "Do NOT excavate. Call utility emergency services.",
                severity = Severity.CRITICAL,
                action   = "Stop work. Call utility emergency line. Keep 5m+ clearance.",
            )
        }

        // Pattern: tachycardia + high altitude → acute mountain sickness
        val hr  = s.heartRateBpm
        val alt = s.altitude.toFloat()
        if (hr > 100 && alt > 2500f && (role == UserRole.NURSE || role == UserRole.FIRST_RESPONDER)) {
            out += Finding(
                sensor   = "⚠ COMPOSITE",
                rawValue = "HR=${hr} bpm  alt=${alt.toInt()}m",
                context  = "TACHYCARDIA + HIGH ALTITUDE — Acute Mountain Sickness (AMS) pattern. " +
                    "Symptoms: headache, nausea, dizziness. DESCEND if any two present.",
                severity = Severity.WARNING,
                action   = "Descend to lower altitude. O₂ supplement if available. Do NOT ascend further.",
            )
        }

        // Pattern: high vibration + high temperature → machinery fault
        val batTemp = s.batteryTempC
        if (linMag > 15f && batTemp > 45f && role == UserRole.ENGINEER) {
            out += Finding(
                sensor   = "⚠ COMPOSITE",
                rawValue = "|lin|=${linMag.toInt()} m/s²  T=${batTemp.toInt()}°C",
                context  = "HIGH VIBRATION + THERMAL SPIKE — machinery fault pattern. " +
                    "Likely: bearing failure, imbalance causing frictional heat. " +
                    "Immediate shutdown recommended.",
                severity = Severity.CRITICAL,
                action   = "Emergency stop affected machinery. Lock out / tag out. Inspect bearings.",
            )
        }
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private fun buildNarrative(findings: List<Finding>, role: UserRole): String {
        val critical = findings.filter { it.severity == Severity.CRITICAL }
        val warnings = findings.filter { it.severity == Severity.WARNING }
        val cautions = findings.filter { it.severity == Severity.CAUTION }

        return buildString {
            if (critical.isNotEmpty()) {
                appendLine("🚨 CRITICAL: ${critical.joinToString("  |  ") { it.sensor }}")
                critical.forEach { appendLine("  • ${it.context}") }
            }
            if (warnings.isNotEmpty()) {
                appendLine("⚠ WARNING: ${warnings.joinToString("  |  ") { it.sensor }}")
                warnings.forEach { appendLine("  • ${it.context}") }
            }
            if (cautions.isNotEmpty()) {
                appendLine("ℹ CAUTION: ${cautions.joinToString("  |  ") { it.sensor }}")
            }
            if (critical.isEmpty() && warnings.isEmpty() && cautions.isEmpty()) {
                appendLine("✅ All sensors nominal. No active alerts for ${role.displayName} role.")
            }
        }.trim()
    }

    /**
     * Heat Index (apparent temperature) using the Rothfusz regression equation.
     * Source: NOAA Technical Attachment SR 90-23 (1990).
     * Formula is valid for T > 27°C (80°F) and relative humidity > 40%.
     * Below 27°C, the heat index approximates ambient temperature.
     *
     * Input:  tempC in °C,  humidityPct as 0–100.
     * Output: apparent temperature in °C.
     */
    private fun computeHeatIndex(tempC: Float, humidityPct: Float): Float {
        if (tempC < 27f) return tempC
        val t  = tempC * 9f / 5f + 32f  // convert to °F for Rothfusz formula
        val h  = humidityPct
        // Rothfusz polynomial (NOAA SR 90-23):
        val hi = (-42.379f +
            2.04901523f   * t +
            10.14333127f  * h +
            -0.22475541f  * t * h +
            -0.00683783f  * t * t +
            -0.05481717f  * h * h +
            0.00122874f   * t * t * h +
            0.00085282f   * t * h * h +
            -0.00000199f  * t * t * h * h)
        return (hi - 32f) * 5f / 9f  // convert result back to °C
    }

    private fun calculateConfidence(s: SensorSnapshot): Float {
        // CONFIDENCE_SENSOR_COUNT must match the number of checks below (7).
        var present = 0
        if (s.pressureHpa > 0)                        present++
        if (s.accelMag > 0)                            present++
        if (s.magMag > 0)                              present++
        if (s.lightLux > 0)                            present++
        if (s.latitude != 0.0 || s.longitude != 0.0)  present++
        if (s.batteryPct >= 0)                         present++
        if (s.heartRateBpm > 0)                        present++
        return present.toFloat() / CONFIDENCE_SENSOR_COUNT
    }
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * SensorSnapshot — a pure data mirror of TricorderUiState without the
 * Android-framework dependency, so SensorInterpreter can be unit-tested
 * without the Android SDK.
 */
data class SensorSnapshot(
    val accelX: Float        = 0f,
    val accelY: Float        = 0f,
    val accelZ: Float        = 0f,
    val accelMag: Float      = 0f,
    val linAccX: Float       = 0f,
    val linAccY: Float       = 0f,
    val linAccZ: Float       = 0f,
    val magMag: Float        = 0f,
    val pressureHpa: Float   = 0f,
    val ambientTempC: Float  = 0f,
    val humidityPct: Float   = 0f,
    val lightLux: Float      = 0f,
    val latitude: Double     = 0.0,
    val longitude: Double    = 0.0,
    val altitude: Double     = 0.0,
    val gpsAccM: Float       = 0f,
    val gpsSpeedMs: Float    = 0f,
    val batteryPct: Int      = -1,
    val batteryTempC: Float  = 0f,
    val heartRateBpm: Int    = 0,
)

// ─────────────────────────────────────────────────────────────────────────────

/**
 * SituationReport — the output of [SensorInterpreter.interpret].
 *
 * Carries the overall severity, a role-appropriate narrative, a short list of
 * recommended actions, all individual findings, and the updated Pentad state.
 */
data class SituationReport(
    val severity:   Severity,
    val narrative:  String,
    val actions:    List<String>,
    val findings:   List<Finding>,
    val pentad:     PentadState,
    /** Fraction of sensors that returned valid data — maps to β·C trust field. */
    val confidence: Float,
)

data class Finding(
    val sensor:   String,
    val rawValue: String,
    val context:  String,
    val severity: Severity,
    val action:   String?,
)

enum class Severity { OK, CAUTION, WARNING, CRITICAL }
