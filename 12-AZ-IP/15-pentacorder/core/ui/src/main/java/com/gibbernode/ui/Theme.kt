package com.gibbernode.ui

import androidx.compose.material3.ColorScheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.ui.graphics.Color

// ── Pentacorder brand colours ──────────────────────────────────────────────────
val GibberGreen  = Color(0xFF00C853)
val GibberRed    = Color(0xFFFF1744)
val GibberBlue   = Color(0xFF2979FF)
val GibberAmber  = Color(0xFFFFAB00)
val BgDark       = Color(0xFF0D1117)
val SurfaceDark  = Color(0xFF161B22)
val OnSurface    = Color(0xFFE6EDF3)
val OnSurfaceDim = Color(0xFF8B949E)

/**
 * gibberColorScheme
 *
 * Material 3 dark color scheme seeded from Pentacorder's brand palette.
 * Used in [MainActivity]'s GibberNodeTheme wrapper.
 */
fun gibberColorScheme(): ColorScheme = darkColorScheme(
    primary              = GibberGreen,
    onPrimary            = BgDark,
    primaryContainer     = Color(0xFF004D20),
    onPrimaryContainer   = GibberGreen,

    secondary            = GibberBlue,
    onSecondary          = BgDark,
    secondaryContainer   = Color(0xFF002B6B),
    onSecondaryContainer = GibberBlue,

    tertiary             = GibberAmber,
    onTertiary           = BgDark,
    tertiaryContainer    = Color(0xFF4D3200),
    onTertiaryContainer  = GibberAmber,

    error                = GibberRed,
    onError              = BgDark,
    errorContainer       = Color(0xFF4D0010),
    onErrorContainer     = GibberRed,

    background           = BgDark,
    onBackground         = OnSurface,
    surface              = SurfaceDark,
    onSurface            = OnSurface,
    surfaceVariant       = Color(0xFF21262D),
    onSurfaceVariant     = OnSurfaceDim,
    outline              = Color(0xFF30363D),
)
