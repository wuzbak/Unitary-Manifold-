package com.axiomzero.androidsuite

import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

@RunWith(AndroidJUnit4::class)
class LocalModelRuntimeOwnershipTest {
    @Test
    fun concurrentNativeCancelAndCloseNeverUseFreedSession() {
        repeat(100) {
            val runtime = LocalModelRuntime()
            runtime.installCancellationProbeForTest()
            val start = CountDownLatch(1)
            val finished = CountDownLatch(2)
            val failure = AtomicReference<Throwable?>()

            Thread {
                try {
                    check(start.await(5, TimeUnit.SECONDS))
                    repeat(200) { runtime.cancelGeneration() }
                } catch (error: Throwable) {
                    failure.compareAndSet(null, error)
                } finally {
                    finished.countDown()
                }
            }.start()
            Thread {
                try {
                    check(start.await(5, TimeUnit.SECONDS))
                    runtime.close()
                } catch (error: Throwable) {
                    failure.compareAndSet(null, error)
                } finally {
                    finished.countDown()
                }
            }.start()

            start.countDown()
            assertTrue("Native cancel/close race did not finish", finished.await(10, TimeUnit.SECONDS))
            failure.get()?.let { throw AssertionError("Native cancel/close race failed", it) }
            assertFalse("Closed runtime still owns a native session", runtime.isLoaded)
            runtime.close()
        }
    }
}
