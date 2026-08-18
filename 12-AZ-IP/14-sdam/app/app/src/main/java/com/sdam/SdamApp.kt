package com.sdam

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * SdamApp
 *
 * Hilt application class for the Software-Defined Acoustic Modem.
 * No WorkManager needed — SDAM uses a bound Foreground Service for background
 * mic capture instead of periodic background workers.
 */
@HiltAndroidApp
class SdamApp : Application()
