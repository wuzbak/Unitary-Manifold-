# Pillar 256 Reproducibility Pack

This folder provides clone-run-compare assets for Pillar 256 execution snapshots.

## Contents

- `run_history.jsonl` — append-only snapshot ledger (one JSON row per run)
- `trend_panels.json` — long-horizon gate trend panels generated from run history
- `snapshots/<snapshot_id>/snapshot.json` — full execution snapshot payload
- `snapshots/<snapshot_id>/manifest.json` — signed run manifest for that snapshot

## Public replay commands

From repository root:

```bash
# 1) Generate new snapshot + signed manifest + update trend panels
python3 9-INFRASTRUCTURE/scripts/pillar256_replay.py snapshot

# Optional: include external observations for FST gates
python3 9-INFRASTRUCTURE/scripts/pillar256_replay.py snapshot \
  --observations-json /path/to/pillar256_observations.json

# 2) Verify a snapshot-manifest pair
python3 9-INFRASTRUCTURE/scripts/pillar256_replay.py verify \
  --snapshot 2-REPRODUCIBILITY/pillar256/snapshots/<snapshot_id>/snapshot.json \
  --manifest 2-REPRODUCIBILITY/pillar256/snapshots/<snapshot_id>/manifest.json

# 3) Compare two snapshots
python3 9-INFRASTRUCTURE/scripts/pillar256_replay.py compare \
  --left-snapshot 2-REPRODUCIBILITY/pillar256/snapshots/<left>/snapshot.json \
  --right-snapshot 2-REPRODUCIBILITY/pillar256/snapshots/<right>/snapshot.json

# 4) Rebuild trend panels from ledger
python3 9-INFRASTRUCTURE/scripts/pillar256_replay.py trend
```

## Optional HMAC signing for external groups

Set `PILLAR256_MANIFEST_HMAC_KEY` before running `snapshot` to emit
`HMAC_SHA256_V1` signatures; otherwise the script emits deterministic
`SELF_HASH_ATTESTATION_V1` signatures.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
