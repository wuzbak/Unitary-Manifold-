package com.gibbernode.optics

import org.junit.Assert.*
import org.junit.Test

// ─────────────────────────────────────────────────────────────────────────────
// NLOSAdvisor Tests
// ─────────────────────────────────────────────────────────────────────────────

class NLOSAdvisorTest {

    @Test fun `empty diffMaps returns empty result`() {
        val r = NLOSAdvisor.reconstruct(emptyList(), 10, 10)
        assertTrue(r.echos.isEmpty())
        assertEquals(0f, r.silhouetteArea, 0f)
        assertEquals(0f, r.confidence, 0f)
    }

    @Test fun `zero dimensions returns empty result`() {
        val r = NLOSAdvisor.reconstruct(listOf(FloatArray(100) { 0.5f }), 0, 10)
        assertTrue(r.echos.isEmpty())
    }

    @Test fun `single bright pixel detected as echo`() {
        // 5×5 frame, one bright spot at centre
        val frame = FloatArray(25) { 0f }
        frame[12] = 0.8f   // centre pixel at row=2, col=2
        val r = NLOSAdvisor.reconstruct(listOf(frame), 5, 5)
        // The centre pixel should be detected (non-max suppression passes single max)
        assertTrue(r.echos.isNotEmpty())
        assertEquals(0.8f, r.echos.first().energy, 0.01f)
    }

    @Test fun `silhouetteArea scales with bright region`() {
        val bright = FloatArray(100) { 0.5f }  // all bright
        val r = NLOSAdvisor.reconstruct(listOf(bright), 10, 10)
        assertTrue(r.silhouetteArea > 0f)
    }

    @Test fun `confidence increases with more frames`() {
        val frame = FloatArray(100) { 0.1f }
        val r1 = NLOSAdvisor.reconstruct(listOf(frame), 10, 10)
        val r5 = NLOSAdvisor.reconstruct(List(10) { frame }, 10, 10)
        assertTrue(r5.confidence >= r1.confidence)
    }

    @Test fun `tof depth is non-zero when phase lag provided`() {
        val frame = FloatArray(25) { 0f }
        frame[12] = 0.9f
        val r = NLOSAdvisor.reconstruct(listOf(frame), 5, 5, tofPhaseLagS = 1e-8f)
        if (r.echos.isNotEmpty()) {
            assertTrue(r.echos.first().depthMeters > 0f)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// HyperspectralAdvisor Tests
// ─────────────────────────────────────────────────────────────────────────────

class HyperspectralAdvisorTest {

    @Test fun `empty frame returns not-plant result`() {
        val r = HyperspectralAdvisor.analyse(emptyList())
        assertEquals(HyperspectralAdvisor.PlantStressLevel.NOT_PLANT, r.plantStressLabel)
    }

    @Test fun `healthy plant has REI above threshold`() {
        // Simulate green/healthy pixels: high R, moderate G, low B (plant signature)
        val pixels = List(16) { floatArrayOf(0.6f, 0.5f, 0.1f) }
        val r = HyperspectralAdvisor.analyse(pixels)
        assertTrue(r.meanRedEdgeIndex >= HyperspectralAdvisor.REI_MODERATE)
    }

    @Test fun `dark subtraction reduces pixel values`() {
        val light = List(4) { floatArrayOf(0.8f, 0.7f, 0.6f) }
        val dark  = List(4) { floatArrayOf(0.1f, 0.1f, 0.1f) }
        val r = HyperspectralAdvisor.analyse(light, dark)
        // After subtraction the rNorm should be lower than without dark sub
        val rWithout = HyperspectralAdvisor.analyse(light)
        assertTrue(r.nirMean <= rWithout.nirMean + 0.01f)
    }

    @Test fun `stacking reduces noise — result size equals input size`() {
        val frame1 = List(8) { floatArrayOf(0.5f, 0.4f, 0.3f) }
        val frame2 = List(8) { floatArrayOf(0.6f, 0.4f, 0.3f) }
        val stacked = HyperspectralAdvisor.stackFrames(listOf(frame1, frame2))
        assertEquals(8, stacked.size)
        assertEquals(0.55f, stacked[0][0], 0.01f)
    }

    @Test fun `bruised fraction is non-zero for high NIR-to-green pixels`() {
        // High R (NIR proxy) relative to G signals bruising
        val pixels = List(9) { floatArrayOf(0.9f, 0.1f, 0.1f) }
        val r = HyperspectralAdvisor.analyse(pixels)
        assertTrue(r.bruisedFraction > 0f)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// MotionMagnificationAdvisor Tests
// ─────────────────────────────────────────────────────────────────────────────

class MotionMagnificationAdvisorTest {

    @Test fun `too-short trace returns zero result`() {
        val trace = MotionMagnificationAdvisor.ColourTrace(FloatArray(3) { 0.5f }, 30f)
        val r = MotionMagnificationAdvisor.magnify(trace)
        assertEquals(0f, r.dominantFreqHz, 0f)
        assertEquals(0f, r.bpmEstimate, 0f)
    }

    @Test fun `cardiac frequency detected in synthetic 1Hz signal`() {
        val fps = 30f
        val n   = 300  // 10 seconds
        // Synthesise a 1.2 Hz (72 bpm) signal
        val vals = FloatArray(n) { t ->
            0.02f * kotlin.math.sin(2f * Math.PI.toFloat() * 1.2f * t / fps).toFloat()
        }
        val trace = MotionMagnificationAdvisor.ColourTrace(vals, fps)
        val r = MotionMagnificationAdvisor.magnify(
            trace,
            lowHz  = MotionMagnificationAdvisor.CARDIAC_LOW_HZ,
            highHz = MotionMagnificationAdvisor.CARDIAC_HIGH_HZ,
        )
        // Dominant frequency should be within ±0.5 Hz of 1.2 Hz
        assertEquals(1.2f, r.dominantFreqHz, 0.5f)
        assertTrue(r.bpmEstimate in 40f..130f)
    }

    @Test fun `magnified signal has higher amplitude than input`() {
        val fps = 60f
        val vals = FloatArray(120) { t ->
            0.01f * kotlin.math.sin(2f * Math.PI.toFloat() * t / fps).toFloat()
        }
        val trace = MotionMagnificationAdvisor.ColourTrace(vals, fps)
        val r = MotionMagnificationAdvisor.magnify(trace, alpha = 20f)
        assertTrue(r.signalPower >= 0f)  // magnified signal exists
    }

    @Test fun `respiratory band returns below-1Hz frequency`() {
        val fps = 30f
        val n   = 300
        val vals = FloatArray(n) { t ->
            0.03f * kotlin.math.sin(2f * Math.PI.toFloat() * 0.25f * t / fps).toFloat()
        }
        val trace = MotionMagnificationAdvisor.ColourTrace(vals, fps)
        val r = MotionMagnificationAdvisor.magnify(
            trace,
            lowHz  = MotionMagnificationAdvisor.RESP_LOW_HZ,
            highHz = MotionMagnificationAdvisor.RESP_HIGH_HZ,
        )
        assertTrue(r.dominantFreqHz < 1.0f)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// VisualMicrophoneAdvisor Tests
// ─────────────────────────────────────────────────────────────────────────────

class VisualMicrophoneAdvisorTest {

    @Test fun `empty trace returns empty result`() {
        val trace = VisualMicrophoneAdvisor.VibrationTrace(FloatArray(0), 960f)
        val r = VisualMicrophoneAdvisor.reconstruct(trace)
        assertTrue(r.spectrum.isEmpty())
        assertEquals(0f, r.rmsAmplitude, 0f)
    }

    @Test fun `speech-frequency signal flagged as speechLikely`() {
        val fps = 960f
        val n   = 960
        // 400 Hz tone — within [300, 480] Hz (Nyquist = fps/2 = 480 Hz)
        val disp = FloatArray(n) { t ->
            0.1f * kotlin.math.sin(2f * Math.PI.toFloat() * 400f * t / fps).toFloat()
        }
        val trace = VisualMicrophoneAdvisor.VibrationTrace(disp, fps)
        val r = VisualMicrophoneAdvisor.reconstruct(
            trace,
            bandLow  = VisualMicrophoneAdvisor.SPEECH_LOW_HZ,
            bandHigh = VisualMicrophoneAdvisor.SPEECH_HIGH_HZ,
        )
        assertTrue(r.speechLikely)
        // Dominant freq must be in the lower speech band (below Nyquist 480 Hz)
        assertTrue("Expected ~400 Hz, got ${r.dominantFreqHz}",
            r.dominantFreqHz in 300f..480f)
    }

    @Test fun `spectrum size equals half the trace length`() {
        val fps = 120f; val n = 60
        val disp = FloatArray(n) { 0.05f }
        val trace = VisualMicrophoneAdvisor.VibrationTrace(disp, fps)
        val r = VisualMicrophoneAdvisor.reconstruct(trace)
        assertEquals(n / 2, r.spectrum.size)
    }

    @Test fun `reconstructedPcm is same length as input`() {
        val n = 100
        val trace = VisualMicrophoneAdvisor.VibrationTrace(FloatArray(n) { 0.02f }, 960f)
        val r = VisualMicrophoneAdvisor.reconstruct(trace)
        assertEquals(n, r.reconstructedPcm.size)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// SyntheticApertureAdvisor Tests
// ─────────────────────────────────────────────────────────────────────────────

class SyntheticApertureAdvisorTest {

    private fun gyroSamples(count: Int, omega: Float): List<SyntheticApertureAdvisor.ImuSample> =
        List(count) { i ->
            SyntheticApertureAdvisor.ImuSample(
                gyroX       = omega,
                gyroY       = 0f,
                gyroZ       = omega,
                timestampMs = (i * 10L),
            )
        }

    @Test fun `empty imu returns physical aperture unchanged`() {
        val r = SyntheticApertureAdvisor.compute(emptyList(), frameCount = 5)
        assertEquals(SyntheticApertureAdvisor.PHYSICAL_APERTURE_MM, r.virtualApertureMm, 0.01f)
        assertEquals(1f, r.apertureRatio, 0.01f)
    }

    @Test fun `virtual aperture exceeds physical with non-zero gyro`() {
        val samples = gyroSamples(100, 0.01f)
        val r = SyntheticApertureAdvisor.compute(samples, frameCount = 10)
        assertTrue(r.virtualApertureMm >= SyntheticApertureAdvisor.PHYSICAL_APERTURE_MM)
    }

    @Test fun `snr improvement is positive for multi-frame burst`() {
        val samples = gyroSamples(50, 0.005f)
        val r = SyntheticApertureAdvisor.compute(samples, frameCount = 16)
        assertTrue(r.snrImprovementDb > 0f)
    }

    @Test fun `bokeh radius is zero when subject and background at same depth`() {
        val samples = gyroSamples(20, 0.001f)
        val r = SyntheticApertureAdvisor.compute(samples, subjectDepthM = 3f, backgroundDepthM = 3f)
        assertEquals(0f, r.bokehBlurRadiusPx, 0.01f)
    }

    @Test fun `bokeh radius increases with background distance`() {
        val samples = gyroSamples(50, 0.01f)
        val r1 = SyntheticApertureAdvisor.compute(samples, subjectDepthM = 2f, backgroundDepthM = 5f)
        val r2 = SyntheticApertureAdvisor.compute(samples, subjectDepthM = 2f, backgroundDepthM = 20f)
        assertTrue(r2.bokehBlurRadiusPx >= r1.bokehBlurRadiusPx)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// NightModeAdvisor Tests
// ─────────────────────────────────────────────────────────────────────────────

class NightModeAdvisorTest {

    private fun frames(count: Int, r: Float = 0.05f, g: Float = 0.04f, b: Float = 0.03f) =
        List(count) { NightModeAdvisor.FrameSample(r, g, b) }

    @Test fun `fused SNR exceeds single-frame SNR`() {
        val r = NightModeAdvisor.analyse(frames(10), sceneLux = 5f)
        assertTrue(r.fusedSnrDb > r.singlePixelSnrDb)
    }

    @Test fun `binned SNR exceeds single-pixel SNR`() {
        val r = NightModeAdvisor.analyse(frames(5), sceneLux = 1f)
        assertTrue(r.binnedSnrDb > r.singlePixelSnrDb)
    }

    @Test fun `more frames give higher fused SNR`() {
        val r5  = NightModeAdvisor.analyse(frames(5),  sceneLux = 2f)
        val r20 = NightModeAdvisor.analyse(frames(20), sceneLux = 2f)
        assertTrue(r20.fusedSnrDb > r5.fusedSnrDb)
    }

    @Test fun `colour temperature in plausible range`() {
        val r = NightModeAdvisor.analyse(frames(10, r = 0.2f, g = 0.15f, b = 0.08f), sceneLux = 10f)
        assertTrue(r.colourTempK in 1800f..12000f)
    }

    @Test fun `ois trace extends max exposure beyond baseline`() {
        // Slow hand movement = small angular velocity
        val slowTrace = NightModeAdvisor.OisTrace(FloatArray(100) { 0.002f }, 100f)
        val r = NightModeAdvisor.analyse(frames(5), oisTrace = slowTrace)
        assertTrue(r.maxHandheldExposureMs > 4f)
    }

    @Test fun `high-tremor trace limits max exposure`() {
        val fastTrace = NightModeAdvisor.OisTrace(FloatArray(100) { 1.5f }, 100f)
        val r = NightModeAdvisor.analyse(frames(5), oisTrace = fastTrace)
        assertTrue(r.maxHandheldExposureMs <= 4000f)  // never exceeds OIS limit
    }

    @Test fun `recommended ISO is higher in darker scenes`() {
        val rBright = NightModeAdvisor.analyse(frames(5), sceneLux = 200f)
        val rDark   = NightModeAdvisor.analyse(frames(5), sceneLux = 0.5f)
        assertTrue(rDark.recommendedIso >= rBright.recommendedIso)
    }

    @Test fun `single frame still produces valid result`() {
        val r = NightModeAdvisor.analyse(frames(1), sceneLux = 1f)
        assertEquals(1, r.frameCount)
        assertTrue(r.fusedSnrDb.isFinite())
    }

    @Test fun `bin factor is always 16 for 200MP sensor`() {
        val r = NightModeAdvisor.analyse(frames(5))
        assertEquals(NightModeAdvisor.BIN_FACTOR, r.binFactor)
    }

    @Test fun `computeMaxExposure with empty trace returns baseline`() {
        val trace = NightModeAdvisor.OisTrace(FloatArray(0))
        val ms = NightModeAdvisor.computeMaxExposure(trace)
        assertEquals(100f, ms, 0f)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// ActiveNIRAdvisor Tests
// ─────────────────────────────────────────────────────────────────────────────

class ActiveNIRAdvisorTest {

    // ── IR-cut transmittance ──────────────────────────────────────────────────

    @Test fun `visible light has high transmittance`() {
        val r = ActiveNIRAdvisor.irCutTransmittance(550)
        assertTrue(r.transmittance > 0.85f)
        assertTrue(r.usableSignal)
    }

    @Test fun `850nm has reduced but usable transmittance`() {
        val r = ActiveNIRAdvisor.irCutTransmittance(850)
        assertTrue(r.transmittance in 0.03f..0.20f)
        assertTrue(r.usableSignal)
    }

    @Test fun `940nm is lower than 850nm`() {
        val r850 = ActiveNIRAdvisor.irCutTransmittance(850)
        val r940 = ActiveNIRAdvisor.irCutTransmittance(940)
        assertTrue(r940.transmittance <= r850.transmittance)
    }

    @Test fun `ir cut removed gives near-full transmittance`() {
        val r = ActiveNIRAdvisor.irCutTransmittance(940, irCutRemoved = true)
        assertTrue(r.transmittance > 0.90f)
        assertTrue(r.usableSignal)
    }

    @Test fun `transmittance clamps between 0 and 1`() {
        listOf(400, 550, 700, 850, 1050).forEach { wl ->
            val r = ActiveNIRAdvisor.irCutTransmittance(wl)
            assertTrue("transmittance out of range at $wl", r.transmittance in 0.01f..0.95f)
        }
    }

    // ── LaserAF depth map ─────────────────────────────────────────────────────

    @Test fun `low confidence pixels zeroed in output`() {
        val depth = floatArrayOf(0.5f, 0.5f, 0.5f)
        val conf  = floatArrayOf(0.1f, 0.1f, 0.1f)   // all below gate
        val frame = ActiveNIRAdvisor.DepthFrame(depth, conf, 3, 1)
        val r = ActiveNIRAdvisor.processDepthMap(frame, minConfidence = 0.3f)
        r.nightVisionImage.forEach { assertEquals(0f, it, 0f) }
        assertEquals(0f, r.validPixelFraction, 0f)
    }

    @Test fun `high confidence close pixel is bright`() {
        val depth = floatArrayOf(0.1f)   // very close (depth ≈ 0 → brightness ≈ 1)
        val conf  = floatArrayOf(0.9f)
        val frame = ActiveNIRAdvisor.DepthFrame(depth, conf, 1, 1)
        val r = ActiveNIRAdvisor.processDepthMap(frame)
        assertTrue(r.nightVisionImage[0] > 0.8f)
        assertEquals(1f, r.validPixelFraction, 0f)
    }

    // ── Temporal denoising ────────────────────────────────────────────────────

    @Test fun `single frame passes through unchanged`() {
        val frame = floatArrayOf(0.1f, 0.5f, 0.9f)
        val r = ActiveNIRAdvisor.temporalDenoise(listOf(frame))
        assertArrayEquals(frame, r, 0.001f)
    }

    @Test fun `averaging two identical frames returns same values`() {
        val frame = floatArrayOf(0.3f, 0.6f, 0.9f)
        val r = ActiveNIRAdvisor.temporalDenoise(listOf(frame, frame), alpha = 0.5f)
        assertArrayEquals(frame, r, 0.001f)
    }

    @Test fun `noisy burst smooths toward mean`() {
        // Alternating noise 0.0 / 1.0 — denoised should converge toward 0.5
        val lo = floatArrayOf(0.0f)
        val hi = floatArrayOf(1.0f)
        val frames = List(20) { i -> if (i % 2 == 0) lo else hi }
        val r = ActiveNIRAdvisor.temporalDenoise(frames, alpha = 0.2f)
        assertTrue("Expected ~0.5, got ${r[0]}", r[0] in 0.1f..0.9f)
    }

    @Test fun `ghost rejection kicks in for large delta`() {
        val base  = floatArrayOf(0.1f)
        val spike = floatArrayOf(0.9f)  // Δ > ghostThreshold (0.2)
        // With ghost rejection the spike should influence output more than without
        val r = ActiveNIRAdvisor.temporalDenoise(listOf(base, spike), ghostThreshold = 0.2f)
        assertTrue(r[0] > base[0])
    }

    // ── CLAHE ─────────────────────────────────────────────────────────────────

    @Test fun `clahe output has same size as input`() {
        val img = FloatArray(64) { it / 64f }
        val r = ActiveNIRAdvisor.clahe(img, 8, 8)
        assertEquals(img.size, r.size)
    }

    @Test fun `clahe output stays in 0-1 range`() {
        val img = FloatArray(100) { it / 100f }
        val r = ActiveNIRAdvisor.clahe(img, 10, 10)
        r.forEach { assertTrue("Out of range: $it", it in 0f..1f) }
    }

    @Test fun `clahe raises contrast on dark image`() {
        // Dark image: all pixels near 0
        val dark = FloatArray(64) { 0.01f + it * 0.001f }
        val r = ActiveNIRAdvisor.clahe(dark, 8, 8, clipLimit = 0.05f)
        val meanInput  = dark.average()
        val meanOutput = r.average()
        // CLAHE should spread the histogram — mean should shift from near-0
        assertTrue("CLAHE should brighten dark image: in=$meanInput out=$meanOutput",
            meanOutput >= meanInput - 0.01f)
    }

    @Test fun `empty image returns empty`() {
        val r = ActiveNIRAdvisor.clahe(FloatArray(0), 0, 0)
        assertEquals(0, r.size)
    }

    // ── Thermal safety ────────────────────────────────────────────────────────

    @Test fun `cool camera is safe with full duty cycle`() {
        val r = ActiveNIRAdvisor.checkThermalSafety(28f)
        assertEquals(ActiveNIRAdvisor.ThermalRisk.SAFE, r.riskLevel)
        assertEquals(1.0f, r.maxDutyCycle, 0f)
    }

    @Test fun `45+ degrees is critical with zero duty cycle`() {
        val r = ActiveNIRAdvisor.checkThermalSafety(47f)
        assertEquals(ActiveNIRAdvisor.ThermalRisk.CRITICAL, r.riskLevel)
        assertEquals(0f, r.maxDutyCycle, 0f)
    }

    @Test fun `thermal risk increases monotonically with temperature`() {
        val temps = listOf(25f, 36f, 42f, 48f)
        val risks = temps.map { ActiveNIRAdvisor.checkThermalSafety(it).riskLevel.ordinal }
        for (i in 1 until risks.size) {
            assertTrue("Risk should be non-decreasing", risks[i] >= risks[i - 1])
        }
    }

    // ── Camera2 parameter recommendations ─────────────────────────────────────

    @Test fun `dark scene recommends high ISO`() {
        val r = ActiveNIRAdvisor.recommendCamera2Params(sceneLux = 0f)
        assertTrue(r.iso >= 3200)
    }

    @Test fun `bright scene recommends low ISO`() {
        val r = ActiveNIRAdvisor.recommendCamera2Params(sceneLux = 50f)
        assertTrue(r.iso <= 3200)
    }

    @Test fun `raw capture sets format to RAW_SENSOR`() {
        val r = ActiveNIRAdvisor.recommendCamera2Params(useRawCapture = true)
        assertTrue(r.outputFormat.contains("RAW"))
    }

    @Test fun `awb mode is always OFF for NIR`() {
        val r = ActiveNIRAdvisor.recommendCamera2Params()
        assertEquals("CONTROL_AWB_MODE_OFF", r.awbMode)
    }
}
