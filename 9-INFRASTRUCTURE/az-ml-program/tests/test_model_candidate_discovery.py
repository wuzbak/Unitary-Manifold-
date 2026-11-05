# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Offline metadata eligibility checks; fixtures do not establish real artifacts."""

from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from src.infrastructure import model_candidate_discovery as discovery


def fixture():
    return {
        "id": "HuggingFaceTB/SmolLM3-fixture", "sha": "a" * 40,
        "private": False, "gated": False, "cardData": {"license": "apache-2.0"},
        "siblings": [{"rfilename": "fixture.gguf",
                      "lfs": {"sha256": "b" * 64, "size": 1_500_000_000}}],
    }


def encoded(value):
    return json.dumps(value).encode("utf-8")


class DiscoveryTests(unittest.TestCase):
    def run_metadata(self, metadata):
        return discovery.discover(lambda url: encoded([metadata]))

    def test_all_eligible_artifacts_are_reported_without_selection(self):
        metadata = fixture()
        metadata["siblings"].append({"rfilename": "sub/second.GGUF",
                                     "lfs": {"sha256": "c" * 64, "size": 1_000_000}})
        metadata["siblings"].append({"rfilename": "README.md"})
        calls = []

        def transport(url):
            calls.append(url)
            return encoded([metadata])

        report = discovery.discover(transport)
        self.assertTrue(report["complete"])
        self.assertEqual(len(report["eligibleArtifacts"]), 2)
        self.assertEqual(calls, [discovery.QUERY_URL])
        self.assertIn("not artifact-byte verification", report["boundary"])

    def test_missing_list_fields_fetch_canonical_metadata(self):
        metadata = fixture()
        canonical = f"https://huggingface.co/api/models/{metadata['id']}?blobs=true"
        responses = {discovery.QUERY_URL: [{"id": metadata["id"]}], canonical: metadata}
        calls = []

        def transport(url):
            calls.append(url)
            return encoded(responses[url])

        report = discovery.discover(transport)
        self.assertTrue(report["complete"])
        self.assertEqual(calls, [discovery.QUERY_URL, canonical])
        self.assertEqual(report["eligibleArtifacts"][0]["source"], canonical)

    def test_missing_canonical_provenance_is_unknown(self):
        for field in ("sha", "private", "gated", "cardData", "siblings"):
            with self.subTest(field=field):
                metadata = fixture()
                del metadata[field]
                report = discovery.discover(
                    lambda url: encoded([metadata] if url == discovery.QUERY_URL else metadata))
                self.assertFalse(report["complete"])
                self.assertEqual(report["eligibleArtifacts"], [])
                self.assertEqual(report["repositories"][0]["status"], "unknown")
                self.assertTrue(report["repositories"][0]["reasons"])

    def test_ineligible_metadata_has_reasons(self):
        for field, value in (("private", True), ("gated", "manual"),
                             ("cardData", {"license": "mit"})):
            with self.subTest(field=field):
                metadata = fixture()
                metadata[field] = value
                report = self.run_metadata(metadata)
                self.assertEqual(report["eligibleArtifacts"], [])
                self.assertEqual(report["repositories"][0]["status"], "ineligible")
                self.assertTrue(report["repositories"][0]["reasons"])

    def test_size_boundaries_and_types(self):
        for size, status in ((999_999, "ineligible"), (1_000_000, "eligible"),
                             (1_600_000_000, "eligible"), (1_600_000_001, "ineligible"),
                             (True, "unknown"), ("1500000", "unknown"), (None, "unknown")):
            with self.subTest(size=size):
                metadata = fixture()
                metadata["siblings"][0]["lfs"]["size"] = size
                report = self.run_metadata(metadata)
                artifact = report["repositories"][0]["artifacts"][0]
                self.assertEqual(artifact["status"], status)
                self.assertEqual(bool(report["eligibleArtifacts"]), status == "eligible")

    def test_bad_sha_path_and_revision_are_unknown(self):
        for field, value in (("sha256", "Z" * 64), ("sha256", "b" * 63),
                             ("rfilename", "../fixture.gguf"),
                             ("rfilename", "/fixture.gguf"),
                             ("rfilename", "sub\\fixture.gguf"),
                             ("rfilename", "https://evil/fixture.gguf"),
                             ("rfilename", "a%2fb.gguf"), ("sha", "a" * 39)):
            with self.subTest(field=field, value=value):
                metadata = fixture()
                if field == "sha":
                    metadata[field] = value
                elif field == "rfilename":
                    metadata["siblings"][0][field] = value
                else:
                    metadata["siblings"][0]["lfs"][field] = value
                self.assertEqual(self.run_metadata(metadata)["eligibleArtifacts"], [])

    def test_missing_lfs_is_unknown_not_defaulted(self):
        metadata = fixture()
        del metadata["siblings"][0]["lfs"]
        report = discovery.discover(
            lambda url: encoded([metadata] if url == discovery.QUERY_URL else metadata))
        self.assertFalse(report["complete"])
        self.assertIn("provenance", report["repositories"][0]["artifacts"][0]["reasons"][0])

    def test_known_exclusion_does_not_hide_unknown_provenance(self):
        metadata = fixture()
        metadata["private"] = True
        metadata["sha"] = None
        report = self.run_metadata(metadata)
        self.assertFalse(report["complete"])
        self.assertEqual(report["repositories"][0]["status"], "unknown")
        self.assertEqual(report["repositories"][0]["artifacts"][0]["status"], "unknown")
        self.assertEqual(report["eligibleArtifacts"], [])

    def test_untrusted_or_duplicate_repository_never_qualifies(self):
        for repository in ("unsloth/SmolLM3-fixture", "HuggingFaceTB/../SmolLM3",
                           "huggingfacetb/SmolLM3-fixture", "HuggingFaceTB/Other"):
            with self.subTest(repository=repository):
                metadata = fixture()
                metadata["id"] = repository
                calls = []
                report = discovery.discover(
                    lambda url: calls.append(url) or encoded([metadata]))
                self.assertFalse(report["complete"])
                self.assertEqual(report["eligibleArtifacts"], [])
                self.assertEqual(calls, [discovery.QUERY_URL])
        metadata = fixture()
        report = discovery.discover(lambda url: encoded([metadata, metadata]))
        self.assertEqual(report["eligibleArtifacts"], [])

    def test_canonical_identity_mismatch_is_unknown(self):
        metadata = fixture()
        other = deepcopy(metadata)
        other["id"] = "HuggingFaceTB/SmolLM3-other"
        report = discovery.discover(
            lambda url: encoded([{"id": metadata["id"]}]
                                if url == discovery.QUERY_URL else other))
        self.assertFalse(report["complete"])
        self.assertEqual(report["eligibleArtifacts"], [])

    def test_malformed_and_duplicate_inventory_fail_closed(self):
        for addition in (None, {"rfilename": 123}, deepcopy(fixture()["siblings"][0])):
            metadata = fixture()
            metadata["siblings"].append(addition)
            report = discovery.discover(
                lambda url: encoded([metadata] if url == discovery.QUERY_URL else metadata))
            self.assertFalse(report["complete"])
            self.assertEqual(report["eligibleArtifacts"], [])

    def test_no_gguf_and_empty_query_are_valid_negative_discovery(self):
        metadata = fixture()
        metadata["siblings"] = [{"rfilename": "model.safetensors"}]
        report = self.run_metadata(metadata)
        self.assertTrue(report["complete"])
        self.assertEqual(report["repositories"][0]["status"], "ineligible")
        self.assertTrue(discovery.discover(lambda url: b"[]")["complete"])

    def test_strict_json_and_response_byte_cap(self):
        for raw in (b'[{"id":1,"id":2}]', b"[NaN]", b"[Infinity]", b"[1e999]", b"\xff", b"{}",
                    b"[", b" " * (discovery.MAX_RESPONSE_BYTES + 1), "[]"):
            with self.subTest(raw=str(raw)[:40]):
                report = discovery.discover(lambda url: raw)
                self.assertFalse(report["complete"])
                self.assertTrue(report["errors"])
                self.assertEqual(report["eligibleArtifacts"], [])

    def test_transport_failure_is_reported(self):
        report = discovery.discover(MagicMock(side_effect=OSError("DNS unavailable")))
        self.assertFalse(report["complete"])
        self.assertIn("DNS unavailable", report["errors"][0])
        self.assertEqual(report["eligibleArtifacts"], [])

    def test_partial_failure_retains_verified_artifacts_but_is_incomplete(self):
        metadata = fixture()
        report = discovery.discover(
            lambda url: encoded([metadata, {"id": "HuggingFaceTB/SmolLM3-other"}])
            if url == discovery.QUERY_URL else (_ for _ in ()).throw(OSError("offline")))
        self.assertFalse(report["complete"])
        self.assertEqual(len(report["eligibleArtifacts"]), 1)

    def test_result_limit_and_global_byte_and_time_caps(self):
        listing = [dict(fixture(), id=f"HuggingFaceTB/SmolLM3-{index}")
                   for index in range(100)]
        report = discovery.discover(lambda url: encoded(listing))
        self.assertFalse(report["complete"])
        self.assertIn("100-result", report["errors"][0])
        with patch.object(discovery, "MAX_TOTAL_BYTES", 10):
            report = self.run_metadata(fixture())
            self.assertFalse(report["complete"])
            self.assertEqual(report["eligibleArtifacts"], [])
        with patch.object(discovery.time, "monotonic", side_effect=[0, 181]):
            transport = MagicMock()
            report = discovery.discover(transport)
            transport.assert_not_called()
            self.assertFalse(report["complete"])

    def test_url_restrictions_and_redirect_rejection(self):
        for url in ("http://huggingface.co/api/models", "https://huggingface.co.evil/api/models",
                    "https://huggingface.co:443/api/models", "https://user@huggingface.co/api/models",
                    "https://huggingface.co/api/models/x?blobs=true",
                    "https://huggingface.co/HuggingFaceTB/SmolLM3/resolve/main/model.gguf",
                    discovery.QUERY_URL + "#fragment"):
            with self.subTest(url=url), self.assertRaises(discovery.DiscoveryError):
                discovery.fetch_metadata(url)
        with self.assertRaises(discovery.DiscoveryError):
            discovery._NoRedirects().redirect_request(None, None, 302, "", {}, "https://evil")

    def test_http_transport_timeout_cap_and_no_proxy(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.status = 200
        response.geturl.return_value = discovery.QUERY_URL
        response.read.return_value = b"[]"
        opener = MagicMock()
        opener.open.return_value = response
        with patch.object(discovery, "build_opener", return_value=opener) as build:
            self.assertEqual(discovery.fetch_metadata(discovery.QUERY_URL), b"[]")
        self.assertEqual(opener.open.call_args.kwargs["timeout"], 15)
        response.read.assert_called_once_with(discovery.MAX_RESPONSE_BYTES + 1)
        self.assertEqual(build.call_args.args[0].proxies, {})
        self.assertIsInstance(build.call_args.args[1], discovery._NoRedirects)
        for status, url, raw in ((302, discovery.QUERY_URL, b"[]"),
                                 (200, "https://evil", b"[]"),
                                 (200, discovery.QUERY_URL,
                                  b" " * (discovery.MAX_RESPONSE_BYTES + 1))):
            response.status, response.read.return_value = status, raw
            response.geturl.return_value = url
            with patch.object(discovery, "build_opener", return_value=opener):
                with self.assertRaises(discovery.DiscoveryError):
                    discovery.fetch_metadata(discovery.QUERY_URL)

    def test_cli_stdout_error_report_and_write_failure(self):
        for transport, expected in ((lambda url: b"[]", 0),
                                     (MagicMock(side_effect=OSError("offline")), 1)):
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                self.assertEqual(discovery.main([], transport=transport), expected)
                self.assertIsInstance(json.loads(stdout.getvalue()), dict)
        destination = MagicMock()
        with patch.object(Path, "open", return_value=destination) as opened:
            self.assertEqual(discovery.main(["--output", "report.json"],
                                            transport=lambda url: b"[]"), 0)
            opened.assert_called_once_with("x", encoding="utf-8")
            text = destination.__enter__.return_value.write.call_args.args[0]
            self.assertTrue(json.loads(text)["complete"])
        with patch.object(Path, "open", side_effect=FileExistsError("exists")), \
                patch("sys.stderr", new_callable=StringIO) as stderr:
            self.assertEqual(discovery.main(["--output", "report.json"],
                                            transport=lambda url: b"[]"), 2)
            self.assertIn("Cannot write", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
