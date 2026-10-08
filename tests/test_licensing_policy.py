# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

import json
import re

import pytest

from TOOLS.checks.check_licensing_policy import (
    DOCUMENTS,
    POLICY_ID,
    POLICY_PATH,
    REPO_ROOT,
    SOFTWARE_LOCATIONS,
    check_policy,
    check_release,
    main,
    read_object,
)


def public_release():
    return {
        "policy_id": POLICY_ID,
        "mode": "public",
        "activity": "modified_network",
        "release_id": "release-1",
        "license": "AGPL-3.0-or-later",
        "source_url": "https://example.org/source/release-1.tar.gz",
        "source_revision": "revision-1",
        "source_offer_visible": True,
        "source_access": "public-no-auth",
    }


def copy_policy(tmp_path):
    for name in SOFTWARE_LOCATIONS:
        (tmp_path / name).mkdir(parents=True, exist_ok=True)
    target = tmp_path / POLICY_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((REPO_ROOT / POLICY_PATH).read_bytes())
    for name in DOCUMENTS:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(POLICY_ID, encoding="utf-8")


def test_repository_policy():
    assert check_policy(REPO_ROOT) == []


def test_portfolio_schedule_matches_canonical_product_registry():
    registry = (REPO_ROOT / "12-AZ-IP/README.md").read_text(encoding="utf-8")
    schedule = (REPO_ROOT / "12-AZ-IP/PORTFOLIO_LICENSE_SCHEDULE.md").read_text(
        encoding="utf-8"
    )
    registry_entries = {}
    for line in registry.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 8 and re.fullmatch(r"\d{2}", cells[0]):
            folder = re.search(r"\(([^)]+)\)", cells[-1])
            assert folder is not None
            registry_entries[cells[0]] = (cells[1], f"12-AZ-IP/{folder.group(1).rstrip('/')}/")

    schedule_entries = {}
    for line in schedule.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 4 and re.fullmatch(r"\d{2}", cells[0]):
            name = cells[1].replace("**", "")
            location = re.fullmatch(r"`([^`]+)`", cells[3])
            assert location is not None
            schedule_entries[cells[0]] = (name, location.group(1))

    assert len(registry_entries) == 27
    assert schedule_entries == registry_entries
    assert {
        number: schedule_entries[number][0]
        for number in ("20", "23", "24", "25", "27")
    } == {
        "20": "PsiCat Navigator (formerly Merlin Navigator)",
        "23": "PsiCat DM Guide & Player Assistant",
        "24": "PsiCat Web Browser",
        "25": "PsiCat Braided Brain",
        "27": "PsiCat's Vite Web Workbench",
    }


@pytest.mark.parametrize("activity", ["distribution", "modified_network"])
def test_public_release(activity):
    evidence = public_release()
    evidence["activity"] = activity
    assert check_release(evidence) == ([], False)


@pytest.mark.parametrize("field", [
    "policy_id", "release_id", "mode", "activity", "license", "source_url",
    "source_revision", "source_offer_visible", "source_access",
])
def test_missing_public_evidence_fails(field):
    evidence = public_release()
    del evidence[field]
    assert check_release(evidence)[0]


@pytest.mark.parametrize("url", [
    "http://example.org/source", "https://user@example.org/source",
    "https://localhost/source", "https://127.0.0.1/source",
    "https://10.0.0.1/source", "https://[::1]/source",
    "https://example.org/source?token=private", "https://example.org/source#fragment",
    "https://example.org:bad/source", "https://example.org/\nsource",
    "https://example.local/source", "https:///source",
    "https://127.1/source", "https://0177.0.0.1/source", "https://10.1/source",
    "https://0x7f.0.0.1/source", "https://127.0.0.0x1/source",
    "https://-invalid.org/source",
    "https://localhost。localhost/source", "https://example。local/source",
    "https://１２７.０.０.１/source",
])
def test_nonpublic_or_sensitive_urls_rejected(url):
    evidence = public_release()
    evidence["source_url"] = url
    assert check_release(evidence)[0]


def test_private_use_needs_no_source_offer():
    evidence = {
        "policy_id": POLICY_ID, "mode": "public",
        "activity": "private", "release_id": "internal-1",
    }
    assert check_release(evidence) == ([], False)


def test_exception_never_self_authorizes(tmp_path, capsys):
    evidence = {
        "policy_id": POLICY_ID, "mode": "exception", "activity": "distribution",
        "release_id": "release-1", "agreement_reference": "reference-1",
        "approved": True, "payment_received": True,
    }
    manifest = tmp_path / "release.json"
    manifest.write_text(json.dumps(evidence), encoding="utf-8")
    assert main(["--release-manifest", str(manifest)]) == 2
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "authorized_agreement_review_required"
    assert output["exception_authorized"] is False
    assert output["legal_certification"] is False


def test_policy_cannot_disable_safeguards(tmp_path):
    copy_policy(tmp_path)
    path = tmp_path / POLICY_PATH
    policy = read_object(path)
    policy["safeguards"]["preserve_prior_grants"] = False
    path.write_text(json.dumps(policy), encoding="utf-8")
    assert check_policy(tmp_path)


def test_integer_is_not_boolean_assent(tmp_path):
    copy_policy(tmp_path)
    path = tmp_path / POLICY_PATH
    policy = read_object(path)
    policy["contract_forum"]["requires_affirmative_acceptance"] = 1
    path.write_text(json.dumps(policy), encoding="utf-8")
    assert check_policy(tmp_path)


def test_residual_guidance_cannot_become_automatic_public_fee(tmp_path):
    copy_policy(tmp_path)
    path = tmp_path / POLICY_PATH
    policy = read_object(path)
    guidance = policy["b2b_economics_guidance"]
    assert guidance["residual_reference_percent"] == "2.32"
    assert guidance["residual_period"] == "quarterly"
    guidance["not_a_public_license_fee"] = False
    path.write_text(json.dumps(policy), encoding="utf-8")
    assert check_policy(tmp_path)


def test_missing_document_fails(tmp_path):
    copy_policy(tmp_path)
    (tmp_path / "LEGAL.md").unlink()
    assert check_policy(tmp_path)


def test_missing_current_software_directory_fails(tmp_path):
    copy_policy(tmp_path)
    (tmp_path / "public-site").rmdir()
    assert check_policy(tmp_path)


def test_external_document_symlink_fails(tmp_path):
    copy_policy(tmp_path)
    external = tmp_path.parent / f"{tmp_path.name}-external"
    external.write_text(POLICY_ID, encoding="utf-8")
    path = tmp_path / "LEGAL.md"
    path.unlink()
    path.symlink_to(external)
    assert check_policy(tmp_path)


@pytest.mark.parametrize("text", ["[]", "{", '{"mode": "public", "mode": "exception"}'])
def test_bad_json_fails(tmp_path, capsys, text):
    manifest = tmp_path / "release.json"
    manifest.write_text(text, encoding="utf-8")
    assert main(["--release-manifest", str(manifest)]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "invalid_evidence"


def test_default_cli_is_read_only(capsys):
    assert main([]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["network_access_performed"] is False
    assert output["legal_certification"] is False


def test_boolean_offer_not_truthy_string():
    evidence = public_release()
    evidence["source_offer_visible"] = "true"
    assert check_release(evidence)[0]


def test_oversized_json_rejected(tmp_path):
    path = tmp_path / "large.json"
    path.write_bytes(b" " * 1_048_577)
    with pytest.raises(ValueError, match="size limit"):
        read_object(path)


def test_deeply_nested_json_fails_closed(tmp_path, capsys):
    path = tmp_path / "nested.json"
    path.write_text('{"nested":' + "[" * 2000 + "0" + "]" * 2000 + "}")
    assert main(["--release-manifest", str(path)]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "invalid_evidence"


def test_exception_missing_reference_is_invalid():
    evidence = {
        "policy_id": POLICY_ID, "mode": "exception",
        "activity": "distribution", "release_id": "release-1",
    }
    errors, review = check_release(evidence)
    assert errors
    assert review


def test_literature_release_has_provenance_and_real_local_sources():
    from TOOLS.audit.check_internal_links import LINK_RE, target_exists

    path = (
        REPO_ROOT / "7-OUTREACH" / "A Z PsiCat Literature"
        / "Releases" / "axiomzero-spc-licensing.md"
    )
    text = path.read_text(encoding="utf-8")
    for marker in (
        "# AxiomZero SPC licensing", POLICY_ID, "Original-work provenance:",
        "Local PsiCat persona", "### Gate Certification (v1)",
        "## Sources and governing instruments",
    ):
        assert marker in text
    assert "Grounded rewrite source:" not in text
    for match in LINK_RE.finditer(text):
        assert target_exists(path, match.group(1))
