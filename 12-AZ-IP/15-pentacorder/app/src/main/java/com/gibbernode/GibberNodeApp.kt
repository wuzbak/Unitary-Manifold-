package com.gibbernode

import android.app.Application
import androidx.work.Configuration
import dagger.hilt.android.HiltAndroidApp
import javax.inject.Inject

/**
 * PentacorderApp
 *
 * Application class.  Hilt annotation generates the component that provides
 * dependency injection to all Activities, Services, ViewModels, and Workers.
 *
 * WorkManager is initialised with the Hilt-backed WorkerFactory so that
 * [SentinelWorker] can receive injected dependencies.
 */
@HiltAndroidApp
class PentacorderApp : Application(), Configuration.Provider {

    @Inject lateinit var workerFactory: androidx.hilt.work.HiltWorkerFactory

    override val workManagerConfiguration: Configuration
        get() = Configuration.Builder()
            .setWorkerFactory(workerFactory)
            .setMinimumLoggingLevel(android.util.Log.INFO)
            .build()
}
