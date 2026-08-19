package com.gibbernode.gibberwave

import androidx.room.ColumnInfo
import androidx.room.Dao
import androidx.room.Database
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.RoomDatabase
import kotlinx.coroutines.flow.Flow

// ─────────────────────────────────────────────────────────────────────────────
// Entity
// ─────────────────────────────────────────────────────────────────────────────

/**
 * AuditLogEntity
 *
 * Room-persisted record of every CommonToken that passed through the UPB Hub.
 * Maps directly to a CommonToken; stored as flat columns for efficient SQLite
 * search and fast RecyclerView rendering.
 */
@Entity(tableName = "audit_log")
data class AuditLogEntity(
    @PrimaryKey val id: String,                      // CommonToken UUID
    @ColumnInfo(name = "timestamp") val timestamp: Long,
    @ColumnInfo(name = "source") val source: String, // SourceProtocol.name
    @ColumnInfo(name = "intent") val intent: String, // IntentTag.name
    @ColumnInfo(name = "payload") val payload: String,
    @ColumnInfo(name = "confidence") val confidence: Float,
) {
    companion object {
        fun fromToken(token: CommonToken) = AuditLogEntity(
            id         = token.id,
            timestamp  = token.timestamp,
            source     = token.source.name,
            intent     = token.intent.name,
            payload    = token.payload,
            confidence = token.confidence,
        )
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// DAO
// ─────────────────────────────────────────────────────────────────────────────

@Dao
interface AuditLogDao {

    /** Insert a single entry; silently skip if the same UUID already exists. */
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insert(entry: AuditLogEntity)

    /** Live Flow of all entries ordered by time descending — UI subscribes here. */
    @Query("SELECT * FROM audit_log ORDER BY timestamp DESC")
    fun allEntries(): Flow<List<AuditLogEntity>>

    /**
     * Full-text search across payload column.
     * SQLite LIKE is case-insensitive for ASCII characters.
     */
    @Query("SELECT * FROM audit_log WHERE payload LIKE '%' || :query || '%' ORDER BY timestamp DESC LIMIT 200")
    fun search(query: String): Flow<List<AuditLogEntity>>

    /** Entries filtered by source protocol. */
    @Query("SELECT * FROM audit_log WHERE source = :source ORDER BY timestamp DESC LIMIT 200")
    fun bySource(source: String): Flow<List<AuditLogEntity>>

    /** Entries filtered by intent. */
    @Query("SELECT * FROM audit_log WHERE intent = :intent ORDER BY timestamp DESC LIMIT 200")
    fun byIntent(intent: String): Flow<List<AuditLogEntity>>

    /** Total entry count — displayed in the Audit tab header. */
    @Query("SELECT COUNT(*) FROM audit_log")
    fun count(): Flow<Int>

    /** Delete all entries (user-facing "Clear Log" action). */
    @Query("DELETE FROM audit_log")
    suspend fun clear()

    /** Delete entries older than [cutoffTimestamp]. */
    @Query("DELETE FROM audit_log WHERE timestamp < :cutoffTimestamp")
    suspend fun deleteOlderThan(cutoffTimestamp: Long)
}

// ─────────────────────────────────────────────────────────────────────────────
// Database
// ─────────────────────────────────────────────────────────────────────────────

@Database(
    entities = [AuditLogEntity::class],
    version = 1,
    exportSchema = false,
)
abstract class GibberDatabase : RoomDatabase() {
    abstract fun auditLogDao(): AuditLogDao
}
