package com.sdam.ui

import androidx.compose.material3.ColorScheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.ui.graphics.Color

// ── SDAM brand colours ────────────────────────────────────────────────────────
val SdamGreen    = Color(0xFF00C853)
val SdamRed      = Color(0xFFFF1744)
val SdamBlue     = Color(0xFF2979FF)
val BgDark       = Color(0xFF0D1117)
val SurfaceDark  = Color(0xFF161B22)
val OnSurface    = Color(0xFFE6EDF3)
val OnSurfaceDim = Color(0xFF8B949E)

/**
 * sdamColorScheme — Material 3 dark colour scheme for the SDAM app.
 *
 * Used in [MainActivity]'s SdamTheme wrapper.
 */
fun sdamColorScheme(): ColorScheme = darkColorScheme(
    primary              = SdamGreen,
    onPrimary            = BgDark,
    primaryContainer     = Color(0xFF004D20),
    onPrimaryContainer   = SdamGreen,

    secondary            = SdamBlue,
    onSecondary          = BgDark,
    secondaryContainer   = Color(0xFF002B6B),
    onSecondaryContainer = SdamBlue,

    error                = SdamRed,
    onError              = BgDark,
    errorContainer       = Color(0xFF4D0010),
    onErrorContainer     = SdamRed,

    background           = BgDark,
    onBackground         = OnSurface,
    surface              = SurfaceDark,
    onSurface            = OnSurface,
    surfaceVariant       = Color(0xFF21262D),
    onSurfaceVariant     = OnSurfaceDim,
    outline              = Color(0xFF30363D),
)
