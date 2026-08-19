package com.gibbernode.di

import android.content.Context
import androidx.room.Room
import com.gibbernode.audio.AudioEngine
import com.gibbernode.audio.NoiseFloorCalibrator
import com.gibbernode.gibberwave.CalibrationStore
import com.gibbernode.gibberwave.GibberDatabase
import com.gibbernode.gibberwave.IntentEngine
import com.gibbernode.gibberwave.OllamaConfig
import com.gibbernode.gibberwave.RelayRouter
import com.gibbernode.security.AcousticAuth
import com.gibbernode.security.GibberKeyManager
import com.gibbernode.security.PayloadCipher
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * AppModule
 *
 * Hilt singleton providers for all cross-cutting dependencies.
 * Scoped to [SingletonComponent] — one instance per application process.
 */
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    // ── Audio ─────────────────────────────────────────────────────────────────

    @Provides
    @Singleton
    fun provideAudioEngine(): AudioEngine = AudioEngine()

    @Provides
    @Singleton
    fun provideNoiseFloorCalibrator(): NoiseFloorCalibrator = NoiseFloorCalibrator()

    // ── Security ──────────────────────────────────────────────────────────────

    @Provides
    @Singleton
    fun provideGibberKeyManager(): GibberKeyManager = GibberKeyManager().also {
        it.ensureKeyExists()  // provisions both HMAC and AES-256-GCM keys on first launch
    }

    @Provides
    @Singleton
    fun provideAcousticAuth(keyManager: GibberKeyManager): AcousticAuth =
        AcousticAuth(keyManager)

    @Provides
    @Singleton
    fun providePayloadCipher(keyManager: GibberKeyManager): PayloadCipher =
        PayloadCipher(keyManager)

    // ── Relay ─────────────────────────────────────────────────────────────────

    @Provides
    @Singleton
    fun provideRelayRouter(): RelayRouter = RelayRouter()

    // ── Ollama / Intent Engine ────────────────────────────────────────────────

    @Provides
    @Singleton
    fun provideOllamaConfig(): OllamaConfig = OllamaConfig()

    @Provides
    @Singleton
    fun provideIntentEngine(config: OllamaConfig): IntentEngine = IntentEngine(config)

    // ── Room database ─────────────────────────────────────────────────────────

    @Provides
    @Singleton
    fun provideGibberDatabase(
        @ApplicationContext context: Context,
    ): GibberDatabase = Room.databaseBuilder(
        context,
        GibberDatabase::class.java,
        "gibbernode.db",
    ).fallbackToDestructiveMigration().build()

    @Provides
    @Singleton
    fun provideAuditLogDao(db: GibberDatabase) = db.auditLogDao()

    // ── Calibration ───────────────────────────────────────────────────────────

    @Provides
    @Singleton
    fun provideCalibrationStore(
        @ApplicationContext context: Context,
    ): CalibrationStore = CalibrationStore(context)
}
