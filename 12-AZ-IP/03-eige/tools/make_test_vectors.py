# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Generate the published EIGE test vectors deterministically.

Usage (from the product directory)::

    python tools/make_test_vectors.py            # (re)write test_vectors/
    python tools/make_test_vectors.py --check    # exit 1 if test_vectors/ is stale

Vectors let independent implementers check their own verifier against EIGE:

* ``merkle.json``   — RFC 6962 roots, inclusion and consistency proofs over the
  Certificate Transparency reference leaves.
* ``ed25519.json``  — RFC 8032 §7.1 test 1 plus an EIGE signed tree head with
  its exact signing message (context separation).
* ``sampling.json`` — audit draws for a public seed and manifest.
* ``bundle/``       — a complete synthetic publication bundle (development keys)
  that ``python -m eige.verify bundle test_vectors/bundle`` accepts.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys
import tempfile
from typing import Dict

PRODUCT = pathlib.Path(__file__).resolve().parent.parent
if str(PRODUCT) not in sys.path:
    sys.path.insert(0, str(PRODUCT))

from eige.audit.sampling import draw_sample, sample_record  # noqa: E402
from eige.crypto import merkle  # noqa: E402
from eige.crypto.signing import DevelopmentSigner, key_id_for, signing_message  # noqa: E402
from eige.ledger.log import MerkleLog  # noqa: E402
from eige.model.election import parse_manifest  # noqa: E402
from eige.pipeline import _seed32, build_synthetic_bundle  # noqa: E402

OUT = PRODUCT / "test_vectors"

CT_LEAVES = [
    b"",
    b"\x00",
    b"\x10",
    b"\x20\x21",
    b"\x30\x31",
    b"\x40\x41\x42\x43",
    b"\x50\x51\x52\x53\x54\x55\x56\x57",
    b"\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f",
]

RFC8032_TEST1 = {
    "secret_key": "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
    "public_key": "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
    "message": "",
    "signature": (
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
        "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
    ),
}


def _dump(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def merkle_vectors() -> dict:
    hashes = [merkle.leaf_hash(x) for x in CT_LEAVES]
    roots = {str(n): merkle.root_from_leaf_hashes(hashes[:n]).hex() for n in range(0, len(hashes) + 1)}
    inclusion = []
    for size in (1, 5, 8):
        for index in range(size):
            inclusion.append({
                "tree_size": size,
                "leaf_index": index,
                "leaf_hash": hashes[index].hex(),
                "proof": [p.hex() for p in merkle.inclusion_proof(hashes[:size], index)],
                "root": roots[str(size)],
            })
    consistency = []
    for old in range(1, 8):
        consistency.append({
            "old_size": old,
            "new_size": 8,
            "old_root": roots[str(old)],
            "new_root": roots["8"],
            "proof": [p.hex() for p in merkle.consistency_proof(hashes, old)],
        })
    return {
        "format": "eige.test_vectors.merkle.v1",
        "spec": "RFC 6962 section 2.1 (leaf prefix 0x00, node prefix 0x01, SHA-256)",
        "leaves_hex": [x.hex() for x in CT_LEAVES],
        "leaf_hashes": [h.hex() for h in hashes],
        "roots": roots,
        "inclusion": inclusion,
        "consistency": consistency,
    }


def signing_vectors() -> dict:
    signer = DevelopmentSigner(_seed32("test-vector-log"))
    log = MerkleLog("TV-COUNTY")
    log.append({"type": "cvr", "cvr": {"id": "TV-1", "batch_id": "B00", "ballot_style": "1", "selections": {}}})
    head = log.sign_head(signer, timestamp=1_793_700_000)
    return {
        "format": "eige.test_vectors.ed25519.v1",
        "rfc8032_test1": RFC8032_TEST1,
        "eige_signed_tree_head": {
            "public_key": signer.public_key_raw.hex(),
            "key_id": key_id_for(signer.public_key_raw),
            "context": "sth",
            "signed_payload": head.signed_payload(),
            "signing_message_hex": signing_message("sth", head.signed_payload()).hex(),
            "head": head.as_dict(),
        },
    }


def sampling_vectors() -> dict:
    manifest = parse_manifest({"jurisdiction": "TV-COUNTY", "batches": [
        {"batch_id": "B00", "ballot_count": 120, "container_id": "BOX-00", "tabulator_id": "TAB-1"},
        {"batch_id": "B01", "ballot_count": 80, "container_id": "BOX-01", "tabulator_id": "TAB-1"},
    ]})
    seed = "31415926535897932384"
    draws = draw_sample(seed, manifest, 12)
    return {
        "format": "eige.test_vectors.sampling.v1",
        "rule": "position_i = 1 + (int(SHA-256(f'{seed},{i}')) mod N), i = 1..n",
        "record": sample_record(seed, manifest, draws),
    }


def generate(directory: pathlib.Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "merkle.json").write_text(_dump(merkle_vectors()), encoding="utf-8")
    (directory / "ed25519.json").write_text(_dump(signing_vectors()), encoding="utf-8")
    (directory / "sampling.json").write_text(_dump(sampling_vectors()), encoding="utf-8")
    build_synthetic_bundle(directory / "bundle", n_batches=2, per_batch=60)


def _snapshot(directory: pathlib.Path) -> Dict[str, bytes]:
    return {str(p.relative_to(directory)): p.read_bytes() for p in sorted(directory.rglob("*")) if p.is_file()}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Generate EIGE test vectors")
    parser.add_argument("--check", action="store_true", help="fail if committed vectors differ")
    args = parser.parse_args(argv)
    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            fresh = pathlib.Path(tmp) / "test_vectors"
            generate(fresh)
            if not OUT.exists() or _snapshot(fresh) != _snapshot(OUT):
                print("test_vectors/ is stale; run python tools/make_test_vectors.py", file=sys.stderr)
                return 1
        return 0
    if OUT.exists():
        shutil.rmtree(OUT)
    generate(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
