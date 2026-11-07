package com.axiomzero.androidsuite

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

class LocalLibraryTest {
    @Test
    fun boundedRankingPreservesScoreNameLineAndStableTies() {
        val documents = listOf(
            EvidenceDocument("z", "alpha\nalpha beta", "z"),
            EvidenceDocument("a", "alpha beta\nalpha beta\nalpha", "first"),
            EvidenceDocument("a", "alpha beta", "second")
        )
        val all = LocalLibrary.searchDocuments(documents, "ALPHA beta", 100)
        assertEquals(listOf("first", "second", "first", "z", "first", "z"), all.map { it.sha256 })
        for (limit in 0..6) {
            assertEquals(all.take(limit), LocalLibrary.searchDocuments(documents, "ALPHA beta", limit))
        }
    }

    @Test
    fun excerptIncludesMatchingEvidenceBeyondTheLinePrefix() {
        val document = EvidenceDocument("log", "x".repeat(2000) + "MATCH" + "y".repeat(1000), "hash")
        val match = LocalLibrary.searchDocuments(listOf(document), "match", 5).single()
        assertTrue(match.excerpt.contains("MATCH"))
        assertTrue(match.excerpt.length <= 500)
    }

    @Test
    fun maximumSizedRepeatedCollectionReturnsOnlyTheBestFiveLines() {
        val document = EvidenceDocument("log", "aa\n".repeat(LocalLibrary.MAX_COLLECTION_BYTES / 3), "hash")
        val matches = LocalLibrary.searchDocuments(listOf(document), "aa", 5)
        assertEquals(listOf(1, 2, 3, 4, 5), matches.map { it.line })
    }

    @Test
    fun sharedStoreSerializesDeletionBehindPendingImportsAndInvalidatesResults() {
        val started = CountDownLatch(1)
        val release = CountDownLatch(1)
        val deleted = CountDownLatch(1)
        val events = mutableListOf<String>()
        val before = LocalStoreTasks.evidenceRevision.get()
        LocalStoreTasks.worker.execute {
            started.countDown()
            check(release.await(5, TimeUnit.SECONDS))
            events.add("import")
        }
        assertTrue(started.await(5, TimeUnit.SECONDS))
        LocalStoreTasks.evidenceRevision.incrementAndGet()
        LocalStoreTasks.worker.execute {
            events.add("delete")
            deleted.countDown()
        }
        release.countDown()
        assertTrue(deleted.await(5, TimeUnit.SECONDS))
        assertEquals(listOf("import", "delete"), events)
        assertTrue(before != LocalStoreTasks.evidenceRevision.get())
    }
}
