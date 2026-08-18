package com.sdam.di

import android.content.Context
import com.sdam.audio.AudioEngine
import com.sdam.audio.CalibrationStore
import com.sdam.audio.NoiseFloorCalibrator
import com.sdam.security.AcousticAuth
import com.sdam.security.PayloadCipher
import com.sdam.security.SdamKeyManager
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * AppModule
 *
 * Hilt singleton providers for all SDAM cross-cutting dependencies.
 */
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideAudioEngine(): AudioEngine = AudioEngine()

    @Provides
    @Singleton
    fun provideNoiseFloorCalibrator(): NoiseFloorCalibrator = NoiseFloorCalibrator()

    @Provides
    @Singleton
    fun provideCalibrationStore(
        @ApplicationContext context: Context,
    ): CalibrationStore = CalibrationStore(context)

    @Provides
    @Singleton
    fun provideSdamKeyManager(): SdamKeyManager = SdamKeyManager().also {
        it.ensureKeyExists()  // provisions HMAC + AES-256-GCM keys on first launch
    }

    @Provides
    @Singleton
    fun provideAcousticAuth(keyManager: SdamKeyManager): AcousticAuth =
        AcousticAuth(keyManager)

    @Provides
    @Singleton
    fun providePayloadCipher(keyManager: SdamKeyManager): PayloadCipher =
        PayloadCipher(keyManager)
}
