# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""External science intake and replayable, human-gated collaboration evaluation.

No network requests, model invocation defaults, downloads, or integrations occur
here. Verifiers are a caller-supplied trust boundary: they must check an actual
artifact/review store, not accept a receipt's self-declared ``verified`` flag.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
import math
from typing import Any
from urllib.parse import urlsplit


LANES = ("merlin", "llm", "collaboration")
BUDGET_FIELDS = ("tokens", "tool_calls", "seconds", "cost")
VERIFIED_CODE_LOCATIONS = {
    "biomni": "https://github.com/snap-stanford/Biomni",
    "virtual_lab": "https://github.com/zou-group/virtual-lab",
    "evo2": "https://github.com/ArcInstitute/evo2",
}
STANFORD_HAI_DISCOVERY_EVENTS = (
    "https://hai.stanford.edu/events/ai-science-accelerating-discovery",
    "https://hai.stanford.edu/events/conference-on-physics-and-ai-pai26",
    "https://hai.stanford.edu/events/brian-hie-genome-modeling-design-across-all-domains-of-life",
)
SOURCE_CHAIN_SNAPSHOTS = {
    "biomni": {
        "revision": "400c1f366b96a35ca253e13c9b06c5076af41d65",
        "readme_sha256": "22be688843a08a1f7f0b243b6bb72e452f9aad82a8602e19716a84aec4863281",
        "license_sha256": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
        "code_license": "Apache-2.0",
        "paper": "https://www.biorxiv.org/content/10.1101/2025.05.30.656746v1",
        "datasets": [
            ("https://huggingface.co/datasets/biomni/Eval1", "evaluation_dataset"),
            ("https://github.com/snap-stanford/Biomni/blob/400c1f366b96a35ca253e13c9b06c5076af41d65/README.md#controlling-datalake-loading", "datalake_documentation_not_dataset_snapshot"),
        ],
        "limitations": [
            "README warns that generated code has full system privileges; no unsandboxed integration is approved.",
            "README documents an approximately 11 GB automatic datalake download; this registry downloads nothing.",
            "README warns that integrated tools, databases, and software can have more restrictive licenses than the Apache-2.0 code.",
            "The cited bioRxiv preprint has not been scientifically reviewed here.",
        ],
    },
    "virtual_lab": {
        "revision": "8a3a4fd9ccc0cd297bd523751e03bc9527c91832",
        "readme_sha256": "b2b5b8a08946c9b11934f98bcd857f8825cba6096073227343a4e8b339c3995e",
        "license_sha256": "98ef26c4e033aba896312dea2d2e57541deb64ad9cb7fe7749143ebc97f3d113",
        "code_license": "MIT",
        "paper": "https://www.nature.com/articles/s41586-025-09442-9",
        "datasets": [
            ("https://github.com/zou-group/virtual-lab/tree/main/nanobody_design", "demonstration_outputs_not_independently_reviewed_dataset"),
        ],
        "limitations": [
            "README describes human-directed LLM meetings; that description is not measured benefit for Merlin.",
            "Demonstration outputs and third-party scientific tools require separate rights and provenance reviews.",
            "The README license badge targets LICENSE.txt, which returned 404; the actual fetched repository license is LICENSE.",
        ],
    },
    "evo2": {
        "revision": "53f195997257c56c00e5ef8d33a54f5baad143a6",
        "readme_sha256": "58787c8ef5cb4fba4c04322a4ceb9f174e2233ec22d4193622fb6bc67d651d89",
        "license_sha256": "5bb5812fc2bfb2d777fe5621767172f8ef30be62ad719c87e0f10832336a99e0",
        "code_license": "Apache-2.0",
        "paper": "https://www.nature.com/articles/s41586-026-10176-5",
        "datasets": [
            ("https://huggingface.co/datasets/arcinstitute/opengenome2", "pretraining_dataset"),
        ],
        "limitations": [
            "README describes GPU/CUDA and precision requirements; the 40B model requires multiple H100 GPUs.",
            "The fetched LICENSE includes additional NVIDIA, Hugging Face/Google, and Fairseq notices; Apache-2.0 is not a blanket third-party clearance.",
            "Model weights, training data, and downstream biological uses require separate reviews; none are approved here.",
        ],
    },
}
Verifier = Callable[[dict[str, Any]], bool]


def _json_value(value: Any) -> None:
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float and math.isfinite(value):
        return
    if type(value) is list:
        for item in value:
            _json_value(item)
        return
    if type(value) is dict and all(type(key) is str for key in value):
        for item in value.values():
            _json_value(item)
        return
    raise ValueError("Expected finite JSON data.")


def _digest(value: Any) -> str:
    _json_value(value)
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def science_evidence_digest(value: Any) -> str:
    """Stable SHA-256 binding for tasks, execution artifacts, and human reviews."""
    return _digest(value)


def _text(value: Any) -> bool:
    return type(value) is str and bool(value.strip())


def _https(value: Any, host: str | None = None) -> bool:
    if not _text(value):
        return False
    try:
        url = urlsplit(value)
        return (
            url.scheme == "https"
            and bool(url.hostname)
            and url.username is None
            and url.password is None
            and url.port in (None, 443)
            and (host is None or url.hostname == host)
            and not any(char.isspace() for char in value)
        )
    except ValueError:
        return False


def _verified(verifier: Verifier | None, record: dict[str, Any]) -> bool:
    if not callable(verifier):
        return False
    try:
        return verifier(deepcopy(record)) is True
    except Exception:
        return False


def get_science_collaboration_benchmark_corpus() -> dict[str, Any]:
    """Frozen source-based calibration challenges, not held-out model evidence."""
    gardner = {
        "url": "https://www.nature.com/articles/s41586-021-04268-7",
        "doi": "10.1038/s41586-021-04268-7",
        "title": "Toroidal topology of population activity in grid cells",
        "journal": "Nature",
        "verification": "bibliographic_index_and_repository_citation_only",
        "direct_page_fetch_status": "dns_resolution_failed",
        "scientific_results_reproduced": False,
    }
    malecns = {
        "url": "https://raw.githubusercontent.com/reiserlab/celltype-explorer-drosophila-male-cns/main/types/LPLC2.html",
        "dataset": "male-cns:v1.0",
        "dataset_uuid": "4b2087c0fbe046bfaf0d60bc970e3e5d",
        "verification": "committed_extract_hashes_checked_and_summary_recomputed",
        "extracts": [
            {"path": "tests/fixtures/malecns/lplc2_upstream_table.html", "sha256": "cc46da74a73fea46dbe7822df1a5a177127c5976171150bc1a55343add222682"},
            {"path": "tests/fixtures/malecns/lplc2_downstream_table.html", "sha256": "8d162e9e8121068be9410bc985c3fb534a5c0214170e2da4aef054555cce431c"},
            {"path": "tests/fixtures/malecns/lplc2_roi_table.html", "sha256": "c8d78287187e48db8a14bf3251798884251ebe576beef0b2d599fca13efdeb04"},
        ],
        "full_page_hash_verified": False,
        "independent_source_authenticity_verified": False,
        "experimental_replication": False,
    }
    evo2_license = {
        "url": "https://raw.githubusercontent.com/ArcInstitute/evo2/53f195997257c56c00e5ef8d33a54f5baad143a6/LICENSE",
        "sha256": SOURCE_CHAIN_SNAPSHOTS["evo2"]["license_sha256"],
        "verification": "code_license_document_fetched_not_dataset_rights_review",
        "dataset_url": "https://huggingface.co/datasets/arcinstitute/opengenome2",
        "dataset_license_review": "unknown",
    }
    challenges = [
        (
            "gardner_bibliography",
            "Identify the journal and DOI of Gardner et al., 'Toroidal topology of population activity in grid cells'. Return exact JSON keys journal and doi; do not substitute Nature Neuroscience.",
            {"journal": "Nature", "doi": "10.1038/s41586-021-04268-7"},
            [gardner],
        ),
        (
            "gardner_representation_boundary",
            "Does the cited Gardner title describe population activity or a physical torus of brain tissue? Return observed_space='population_activity' or 'physical_tissue', and physical_torus_established as a boolean justified by this source scope.",
            {"observed_space": "population_activity", "physical_torus_established": False},
            [gardner],
        ),
        (
            "malecns_lplc2_source_counts",
            "Parse the cited, hash-pinned MaleCNS v1.0 LPLC2 upstream/downstream HTML extracts. Count displayed partner types and sum integer connection weights, including the same-type row. Return upstream_partner_types, downstream_partner_types, input_synapses, output_synapses. These are type-level source-table counts, not numbers of individual neurons.",
            {"upstream_partner_types": 536, "downstream_partner_types": 692, "input_synapses": 350542, "output_synapses": 182982},
            [malecns],
        ),
        (
            "malecns_lplc2_reciprocity_boundary",
            "Using the same LPLC2 extracts, report the upstream/downstream partner-set intersection size as reciprocal_partner_types and the LPLC2-to-LPLC2 row weight as same_type_synapses. Also return individual_autapses_established: do aggregate type-to-type rows establish individual-neuron autapses?",
            {"reciprocal_partner_types": 440, "same_type_synapses": 46178, "individual_autapses_established": False},
            [malecns],
        ),
        (
            "cross_source_epistemic_boundary",
            "The MaleCNS extracts contain anatomical partner/connection summaries, but no grid-cell population activity. Does reproducing those summaries reproduce Gardner's activity-space topology or validate Unitary Manifold physics? Return gardner_topology_reproduced and um_validated.",
            {"gardner_topology_reproduced": False, "um_validated": False},
            [gardner, malecns],
        ),
        (
            "code_vs_dataset_rights",
            "Evo2's fetched code LICENSE begins with Apache-2.0 and includes third-party notices. OpenGenome2 data rights have not been reviewed. Return code_license, dataset_reuse_allowed, and scientific_truth_canonical. A code license or source URL must not authorize unreviewed dataset reuse or establish canonical scientific truth.",
            {"code_license": "Apache-2.0", "dataset_reuse_allowed": False, "scientific_truth_canonical": False},
            [evo2_license],
        ),
    ]
    tasks = [
        {
            "task_id": f"science_source_calibration_v1_{name}", "prompt": prompt,
            "expected": expected, "split": "public_example",
            "provenance_url": references[0]["url"],
            "source_references": deepcopy(references),
        }
        for name, prompt, expected, references in challenges
    ]
    return {
        "corpus_id": "science_external_source_calibration_v1",
        "tasks": tasks, "training_task_ids": [],
        "task_manifest_digest": _digest({"tasks": tasks, "training_task_ids": []}),
        "corpus_class": "public_source_based_calibration_not_held_out",
        "expected_answers_public": True,
        "held_out_provenance_verified": False,
        "training_exposure_review": "not_performed",
        "eligible_for_model_benefit_evidence": False,
        "policy": "Public challenges and answer keys may be training-exposed. Use only in deterministic calibration mode; independent holdout and training-exposure review remain mandatory for real model admission.",
        "limitations": [
            "Bibliographic calibration is not paper replication.",
            "Committed MaleCNS extract-byte verification is not independent source authentication or experimental replication.",
            "Public answer keys and source links preclude asserting an independently verified held-out benchmark.",
            "No actual model run, comparative model benefit, or physics validation is asserted by this corpus.",
        ],
    }


def get_science_collaboration_benchmark_spec() -> dict[str, Any]:
    """A discoverable, pending contract; reading this never executes a model."""
    return {
        "status": "pending_real_model_run",
        "spec_version": "1",
        "spec_tool": "getMerlinScienceCollaborationBenchmarkSpec",
        "execution_tool": "runMerlinScienceCollaborationBenchmark",
        "tool_api": "/api/agentInvoke",
        "lanes": list(LANES),
        "corpus": get_science_collaboration_benchmark_corpus(),
        "scoring": "held_out_exact_json_match",
        "winner": None,
        "measured_benefit": False,
        "execution_performed": False,
        "model_invocation_performed": False,
        "automatic_integration": False,
        "task_policy": {
            "frozen_manifest_digest": None,
            "freeze": "SHA-256 of tasks and explicit training_task_ids before evaluating any lane.",
            "real_evidence": "Independent verification of the frozen held-out manifest is mandatory.",
            "callback_inputs": "Task ID, prompt, cited source references when present, frozen task digest, lane, and TOTAL budget; never expected answers.",
        },
        "budget_policy": {
            "dimensions": list(BUDGET_FIELDS),
            "comparison": "Exactly equal TOTAL allocations per task across all lanes.",
            "includes": [
                "all_participants", "planning_calls", "intermediate_model_calls",
                "synthesis_calls", "retries", "tool_calls", "nested_tool_calls",
            ],
            "accounting": "One execution entry per call, with allocation, actual usage, identity, mode, and artifact provenance.",
            "exclusive_counters": "Per-call counters are exclusive: do not count nested child usage again in a parent aggregate.",
            "complete_execution_accounting": "Must be independently checked against the execution artifacts, not merely asserted.",
        },
        "execution_labels": {
            "live": "Actual live execution at receipt capture time; callback transport alone does not establish live model inference.",
            "recorded": "Previously captured execution, independently checked against immutable artifacts.",
            "deterministic": "Engineering validation only; model lanes are surrogates, not LLM runs or benefit evidence.",
        },
        "tool_modes": {
            "no_arguments": "Return this pending spec without execution.",
            "deterministic": "Evaluate provided deterministic records on a frozen task manifest; never establishes measured model benefit.",
            "model": "Evaluate recorded real-model outputs only with independent verification; JSON callers cannot supply trusted verifiers.",
        },
        "callbacks": "Optional trusted Python callbacks; the JSON tool never accepts executable callbacks.",
        "verifier_policy": "Python verifier integration is required for real evidence. The public JSON tool fails closed for unverified model receipts.",
        "rights_policy": "Source URLs identify locations only; artifact-specific license and provenance reviews remain mandatory.",
    }


def _source_chain_candidate(resource_id: str, url: str) -> dict[str, Any]:
    snapshot = SOURCE_CHAIN_SNAPSHOTS[resource_id]
    repository = url.removeprefix("https://github.com/")
    revision = snapshot["revision"]
    readme_url = f"https://raw.githubusercontent.com/{repository}/{revision}/README.md"
    license_url = f"https://raw.githubusercontent.com/{repository}/{revision}/LICENSE"

    def unreviewed_link(location: str, artifact_kind: str) -> dict[str, Any]:
        return {
            "url": location, "artifact_kind": artifact_kind,
            "link_verification": "documented_in_fetched_upstream_readme",
            "provenance_url": readme_url,
            "upstream_readme_revision": revision,
            "scientific_review": "unverified",
            "license": None, "license_status": "unknown", "reuse_allowed": False,
        }

    return {
        "resource_id": resource_id,
        "canonical_truth": False,
        "discovery_url": STANFORD_HAI_DISCOVERY_EVENTS[0],
        "discovery_location_verification": "user_provided_location_not_fetched",
        "discovery_attribution": "HAI science-event discovery lead only; no assertion that the event lists every candidate.",
        "upstream_readme": {
            "url": readme_url, "revision": revision,
            "sha256": snapshot["readme_sha256"],
            "verification": "content_fetched", "retrieved_on": "2026-10-07",
        },
        "code": [{
            "url": url, "revision": revision, "provenance_url": readme_url,
            "verification": "repository_location_and_license_document_fetched",
            "license": {
                "identifier": snapshot["code_license"], "url": license_url,
                "revision": revision, "sha256": snapshot["license_sha256"],
                "document_verification": "content_fetched_and_identifier_checked",
                "retrieved_on": "2026-10-07", "scope": "repository_code_document_only",
                "rights_review": "pending_artifact_and_component_review",
                "reuse_permitted": False,
            },
        }],
        "papers": [unreviewed_link(snapshot["paper"], "primary_paper_location")],
        "datasets": [unreviewed_link(location, kind) for location, kind in snapshot["datasets"]],
        "license_status": "code_document_identified_data_and_paper_rights_unknown",
        "reuse_allowed": False,
        "paper_verification": "citation_link_in_readme_only_not_scientific_review",
        "limitations": deepcopy(snapshot["limitations"]) + [
            "Paper and dataset licenses, contamination, provenance, and claimed scientific results remain unverified.",
        ],
        "status": "source_chain_candidate_pending_review",
    }


def get_science_evidence_registry() -> dict[str, Any]:
    """Expose observed source chains without conflating locations and rights."""
    return {
        "discovery": {
            "url": "https://hai.stanford.edu/",
            "role": "discovery_only",
            "event_urls": list(STANFORD_HAI_DISCOVERY_EVENTS),
            "requested_event_url": STANFORD_HAI_DISCOVERY_EVENTS[0],
            "requested_event_verification": "user_provided_location_not_fetched",
            "event_locations": [
                {
                    "url": event_url,
                    "verification": (
                        "user_provided_location_not_fetched" if index == 0 else "web_search_index_only"
                    ),
                    "page_fetched": False,
                }
                for index, event_url in enumerate(STANFORD_HAI_DISCOVERY_EVENTS)
            ],
            "event_location_verification": "per_event_location_only_not_event_content",
            "event_page_fetch_status": "not_fetched_dns_resolution_failed",
            "candidate_event_membership": "not_asserted",
            "policy": "Follow primary papers, code, datasets, licenses, and limitations; HAI is not scientific verification.",
        },
        "external_evidence_is_canonical_truth": False,
        "automatic_integrations": False,
        "candidates": [
            _source_chain_candidate(resource_id, url)
            for resource_id, url in VERIFIED_CODE_LOCATIONS.items()
        ],
        "collaboration_benchmark": get_science_collaboration_benchmark_spec(),
        "expansion_gates": [
            "measured_paired_benefit",
            "verified_rights_and_provenance",
            "verified_hardware_capacity",
            "human_approval_bound_to_benchmark",
        ],
    }


def evaluate_science_evidence(
    record: dict[str, Any], *, review_verifier: Verifier | None = None
) -> dict[str, Any]:
    """Fail closed for incomplete metadata or unverified, artifact-specific rights."""
    reasons: list[str] = []
    try:
        _json_value(record)
        if type(record) is not dict:
            raise ValueError("Evidence must be an object.")
        if not _text(record.get("resource_id")):
            reasons.append("missing_resource_id")
        if not _https(record.get("discovery_url"), "hai.stanford.edu"):
            reasons.append("stanford_hai_discovery_required")
        if record.get("canonical_truth") is not False:
            reasons.append("external_evidence_never_canonical")
        limitations = record.get("limitations")
        if type(limitations) is not list or not limitations or not all(map(_text, limitations)):
            reasons.append("explicit_limitations_required")
        for category in ("papers", "code", "datasets"):
            sources = record.get(category)
            if type(sources) is not list or not sources:
                reasons.append(f"{category}_primary_links_required")
                continue
            for source in sources:
                if type(source) is not dict or not _https(source.get("url")):
                    reasons.append(f"{category}_invalid_source")
                    continue
                if not _text(source.get("revision")) or not _https(source.get("provenance_url")):
                    reasons.append(f"{category}_missing_provenance")
                license_review = source.get("license")
                if (
                    type(license_review) is not dict
                    or not _text(license_review.get("identifier"))
                    or license_review.get("identifier", "").strip().casefold() in (
                        "unknown", "pending", "unverified", "none", "unlicensed",
                    )
                    or not _https(license_review.get("url"))
                    or license_review.get("reuse_permitted") is not True
                    or not _text(license_review.get("review_id"))
                ):
                    reasons.append(f"{category}_unknown_or_restricted_license")
                elif not _verified(review_verifier, {
                    "kind": "source_rights_and_provenance",
                    "resource_id": record.get("resource_id"),
                    "category": category,
                    "source": source,
                }):
                    reasons.append(f"{category}_unverified_rights_or_provenance")
    except (ValueError, TypeError, OverflowError, RecursionError):
        reasons.append("malformed_or_nonfinite_evidence")
    return {
        "status": "reviewed_external_evidence" if not reasons else "blocked",
        "reuse_allowed": not reasons,
        "canonical_truth": False,
        "automatic_integration": False,
        "reasons": sorted(set(reasons)),
    }


def _budget(value: Any) -> dict[str, int | float]:
    if type(value) is not dict or set(value) != set(BUDGET_FIELDS):
        raise ValueError("All TOTAL budget dimensions are required.")
    for key, number in value.items():
        if type(number) not in (int, float) or not math.isfinite(number) or number < 0:
            raise ValueError("Budgets and usage must be finite nonnegative numbers.")
        if key in ("tokens", "tool_calls") and type(number) is not int:
            raise ValueError("Token and tool counts must be integers.")
    return value


def _tasks(
    tasks: Any, training_task_ids: Any, *, allow_public_examples: bool = False,
) -> list[dict[str, Any]]:
    _json_value(tasks)
    if type(training_task_ids) is not list or not all(map(_text, training_task_ids)):
        raise ValueError("Training task IDs must be explicit.")
    if type(tasks) is not list or not tasks:
        raise ValueError("Nonempty held-out task set required.")
    seen: set[str] = set()
    for task in tasks:
        if type(task) is not dict:
            raise ValueError("Task must be an object.")
        task_id = task.get("task_id")
        if not _text(task_id) or task_id in seen or task_id in training_task_ids:
            raise ValueError("Duplicate or contaminated held-out task.")
        public_example = allow_public_examples and task.get("split") == "public_example"
        if (
            (task.get("split") != "held_out" and not public_example)
            or not _text(task.get("prompt"))
            or "expected" not in task
            or not _https(task.get("provenance_url"))
            or (not public_example and not _text(task.get("holdout_review_id")))
        ):
            raise ValueError("Held-out task provenance and objective answer required.")
        seen.add(task_id)
    return tasks


def _validate_run(
    record: Any, task: dict[str, Any], lane: str, budget: dict[str, Any],
    verifier: Verifier | None, *, deterministic_only: bool = False,
) -> tuple[Any, str, bool]:
    _json_value(record)
    if type(record) is not dict or "output" not in record:
        raise ValueError("Recorded output required; scores alone are not evidence.")
    if record.get("task_id") != task["task_id"] or record.get("lane") != lane:
        raise ValueError("Receipt task/lane mismatch.")
    if record.get("task_digest") != _digest(task):
        raise ValueError("Receipt must bind the complete held-out task.")
    if record.get("origin") not in ("recorded", "callback"):
        raise ValueError("Synthetic runs cannot establish benefit.")
    if record.get("complete_execution_accounting") is not True:
        raise ValueError("All participants, retries, and tools must be accounted for.")
    executions = record.get("executions")
    if type(executions) is not list or not executions:
        raise ValueError("Execution provenance required.")
    totals = {key: Fraction(0) for key in BUDGET_FIELDS}
    has_model = False
    has_merlin = False
    ids: set[str] = set()
    for execution in executions:
        if type(execution) is not dict:
            raise ValueError("Execution must be an object.")
        execution_id = execution.get("execution_id")
        if not _text(execution_id) or execution_id in ids:
            raise ValueError("Unique execution IDs required.")
        ids.add(execution_id)
        if (
            not _text(execution.get("system_id"))
            or not _https(execution.get("artifact_url"))
            or execution.get("kind") not in ("model", "merlin", "tool")
        ):
            raise ValueError("Execution identity and artifact provenance required.")
        mode = execution.get("execution_mode")
        if mode not in ("live", "recorded", "deterministic"):
            raise ValueError("Every call must label live, recorded, or deterministic execution.")
        if deterministic_only and (mode != "deterministic" or execution["kind"] == "model"):
            raise ValueError("Deterministic validation cannot contain real or purported model runs.")
        if execution["kind"] == "model":
            if mode == "deterministic":
                raise ValueError("Deterministic output is not an LLM receipt.")
            if not _text(execution.get("model_revision")):
                raise ValueError("Real model revision required.")
            has_model = True
        has_merlin |= execution["kind"] == "merlin"
        allocation = _budget(execution.get("budget"))
        usage = _budget(execution.get("usage"))
        if execution["kind"] == "model" and (usage["tokens"] <= 0 or usage["seconds"] <= 0):
            raise ValueError("Model receipt requires actual inference usage.")
        if execution["kind"] == "merlin" and usage["seconds"] <= 0:
            raise ValueError("Merlin receipt requires actual execution usage.")
        for key in BUDGET_FIELDS:
            if usage[key] > allocation[key]:
                raise ValueError("Execution exceeded allocated budget.")
            totals[key] += Fraction(str(allocation[key]))
    if any(totals[key] != Fraction(str(budget[key])) for key in BUDGET_FIELDS):
        raise ValueError("Unequal TOTAL budgets across lanes.")
    if not deterministic_only and lane == "merlin" and (not has_merlin or has_model):
        raise ValueError("Merlin baseline must not contain an LLM.")
    if not deterministic_only and lane == "llm" and (not has_model or has_merlin):
        raise ValueError("LLM baseline must be standalone.")
    if not deterministic_only and lane == "collaboration" and not (has_model and has_merlin):
        raise ValueError("Collaboration requires both Merlin and an actual model.")
    receipt_id = _digest(record)
    if not deterministic_only and not _verified(verifier, {"kind": "execution_receipt", "receipt_id": receipt_id, "record": record}):
        raise ValueError("Independent artifact verification failed.")
    return record["output"], receipt_id, has_model


def run_collaboration_benchmark(
    *,
    tasks: list[dict[str, Any]],
    budgets: dict[str, dict[str, int | float]],
    training_task_ids: list[str],
    recorded_outputs: dict[str, list[dict[str, Any]]] | None = None,
    callbacks: Mapping[str, Callable[[dict[str, Any]], dict[str, Any]]] | None = None,
    receipt_verifier: Verifier | None = None,
    execution_mode: str = "model",
    frozen_manifest_digest: str | None = None,
) -> dict[str, Any]:
    """Score paired outputs; callbacks receive prompts, never held-out answers.

    A trusted receipt verifier must independently check execution artifacts AND
    held-out provenance. Callbacks are transport, not proof of real inference.
    Unequal allocations, partial lanes, and unverifiable receipts block results.
    """
    blocked = {"status": "blocked", "winner": None, "measured_benefit": False}
    try:
        if execution_mode not in ("model", "deterministic"):
            raise ValueError("Choose model evidence or deterministic engineering validation.")
        deterministic_only = execution_mode == "deterministic"
        tasks = deepcopy(_tasks(tasks, training_task_ids, allow_public_examples=deterministic_only))
        _json_value(budgets)
        if type(budgets) is not dict or set(budgets) != set(LANES):
            raise ValueError("All three lanes require budgets.")
        common = _budget(budgets["merlin"])
        if any(_budget(budgets[lane]) != common for lane in LANES):
            raise ValueError("Unequal TOTAL budgets across lanes.")
        if common["tokens"] <= 0 or common["seconds"] <= 0:
            raise ValueError("Positive token/time allocations required.")
        manifest_digest = _digest({"tasks": tasks, "training_task_ids": training_task_ids})
        if frozen_manifest_digest is not None and frozen_manifest_digest != manifest_digest:
            raise ValueError("Frozen task manifest changed.")
        if deterministic_only and frozen_manifest_digest != manifest_digest:
            raise ValueError("Deterministic evaluation requires a frozen task manifest digest.")
        if recorded_outputs is None and callbacks is None:
            return {
                "status": "pending_real_model_run", "winner": None,
                "measured_benefit": False, "task_manifest_digest": manifest_digest,
                "execution_performed": False,
                "model_invocation_performed": False,
            }
        if (recorded_outputs is None) == (callbacks is None):
            raise ValueError("Choose recorded outputs OR callbacks, never both.")
        if not deterministic_only and not _verified(receipt_verifier, {
            "kind": "held_out_manifest", "manifest_digest": manifest_digest,
            "tasks": tasks, "training_task_ids": training_task_ids,
        }):
            raise ValueError("Held-out provenance not independently verified.")
        source = recorded_outputs if recorded_outputs is not None else callbacks
        if not isinstance(source, Mapping) or set(source) != set(LANES):
            raise ValueError("Complete paired lanes required.")
        outputs: dict[str, list[dict[str, Any]]] = {}
        for lane in LANES:
            if callbacks is not None:
                if not callable(callbacks[lane]):
                    raise ValueError("Every lane requires a callback.")
                outputs[lane] = [
                    callbacks[lane]({
                        "task_id": task["task_id"], "prompt": task["prompt"],
                        "task_digest": _digest(task), "lane": lane,
                        "total_budget": deepcopy(common),
                        **({"source_references": deepcopy(task["source_references"])}
                           if "source_references" in task else {}),
                    })
                    for task in tasks
                ]
            else:
                outputs[lane] = deepcopy(recorded_outputs[lane])
            if type(outputs[lane]) is not list or len(outputs[lane]) != len(tasks):
                raise ValueError("Missing or extra task outputs.")
        scores: dict[str, list[int]] = {lane: [] for lane in LANES}
        receipts: dict[str, list[str]] = {lane: [] for lane in LANES}
        accounting: dict[str, list[dict[str, Any]]] = {lane: [] for lane in LANES}
        all_execution_ids: set[str] = set()
        all_artifact_urls: set[str] = set()
        for index, task in enumerate(tasks):
            for lane in LANES:
                record = outputs[lane][index]
                output, receipt_id, _ = _validate_run(
                    record, task, lane, common, receipt_verifier,
                    deterministic_only=deterministic_only,
                )
                execution_ids = {execution["execution_id"] for execution in record["executions"]}
                if execution_ids & all_execution_ids:
                    raise ValueError("Replayed execution artifact across task/lane.")
                all_execution_ids.update(execution_ids)
                artifact_urls = [execution["artifact_url"] for execution in record["executions"]]
                if len(set(artifact_urls)) != len(artifact_urls) or set(artifact_urls) & all_artifact_urls:
                    raise ValueError("Replayed execution artifact URL across task/lane.")
                all_artifact_urls.update(artifact_urls)
                scores[lane].append(int(_digest(output) == _digest(task["expected"])))
                receipts[lane].append(receipt_id)
                accounting[lane].append({
                    "task_id": task["task_id"], "transport": record["origin"],
                    "executions": deepcopy(record["executions"]),
                    "total_allocated": deepcopy(common),
                    "total_usage": {
                        key: float(sum(
                            (Fraction(str(execution["usage"][key])) for execution in record["executions"]),
                            Fraction(0),
                        )) if key not in ("tokens", "tool_calls") else sum(
                            execution["usage"][key] for execution in record["executions"]
                        )
                        for key in BUDGET_FIELDS
                    },
                })
        means = {lane: sum(scores[lane]) / len(tasks) for lane in LANES}
        deltas = {
            lane: [
                paired - baseline for paired, baseline in zip(scores["collaboration"], scores[lane])
            ]
            for lane in ("merlin", "llm")
        }
        gains = {lane: sum(values) / len(tasks) for lane, values in deltas.items()}
        benefit = not deterministic_only and all(value > 0 for value in gains.values())
        result = {
            "status": "completed_deterministic_validation" if deterministic_only else "completed_verified_runs",
            "winner": "collaboration" if benefit else None,
            "measured_benefit": benefit,
            "scientific_truth_established": False,
            "automatic_integration": False,
            "evaluation_performed": True,
            "evaluation_transport": "callbacks" if callbacks is not None else "recorded_outputs",
            "model_invocation_performed": None if not deterministic_only and callbacks is not None else False,
            "live_model_receipts_present": bool(
                not deterministic_only and any(
                    execution["kind"] == "model" and execution["execution_mode"] == "live"
                    for records in outputs.values() for record in records
                    for execution in record["executions"]
                )
            ),
            "comparison_kind": "deterministic_surrogates" if deterministic_only else "real_model_benchmark",
            "receipts_independently_verified": not deterministic_only,
            "held_out_provenance_verified": not deterministic_only,
            "scoring": "held_out_exact_json_match",
            "task_manifest_digest": manifest_digest,
            "task_count": len(tasks),
            "total_budget_per_task": deepcopy(common),
            "scores": scores, "mean_scores": means,
            "paired_deltas": deltas, "paired_mean_gain": gains,
            "receipt_ids": receipts,
            "execution_accounting": accounting,
            "limitations": (
                ["Deterministic lane surrogates are engineering checks, not real LLM runs, verified holdouts, or benefit evidence."]
                if deterministic_only else [
                    "Benefit is confined to these tasks and budgets; it is not a general LLM superiority claim.",
                    "Verified live receipts describe capture-time execution; callback transport alone does not prove a fresh model invocation.",
                ]
            ),
        }
        result["benchmark_digest"] = _digest(result)
        return result
    except Exception as exc:
        return {**blocked, "reasons": [str(exc) or "invalid_benchmark"]}


def run_science_collaboration_tool(**request: Any) -> dict[str, Any]:
    """JSON-safe tool boundary: no callbacks or self-supplied verifier trust."""
    if not request:
        return get_science_collaboration_benchmark_spec()
    if "callbacks" in request or "receipt_verifier" in request:
        return {
            "status": "blocked", "winner": None, "measured_benefit": False,
            "reasons": ["Trusted callbacks/verifiers cannot be supplied by JSON callers."],
        }
    try:
        return run_collaboration_benchmark(**request)
    except (TypeError, ValueError) as exc:
        return {
            "status": "blocked", "winner": None, "measured_benefit": False,
            "reasons": [str(exc)],
        }


def evaluate_science_expansion(
    *,
    evidence: dict[str, Any],
    benchmark_request: dict[str, Any],
    hardware: dict[str, Any],
    human_approval: dict[str, Any],
    receipt_verifier: Verifier | None = None,
    review_verifier: Verifier | None = None,
    minimum_gain: float = 0.0,
) -> dict[str, Any]:
    """Recompute evidence, never promote from a supplied score/winner flag."""
    reasons: list[str] = []
    benchmark: dict[str, Any] = {}
    try:
        if type(minimum_gain) not in (int, float) or not math.isfinite(minimum_gain) or minimum_gain < 0:
            raise ValueError("Invalid measured benefit threshold.")
        if not evaluate_science_evidence(evidence, review_verifier=review_verifier)["reuse_allowed"]:
            reasons.append("rights_or_provenance_blocked")
        if type(benchmark_request) is not dict or "callbacks" in benchmark_request:
            raise ValueError("Expansion needs replayable recorded receipts, not new callbacks.")
        benchmark = run_collaboration_benchmark(**benchmark_request, receipt_verifier=receipt_verifier)
        if (
            benchmark.get("status") != "completed_verified_runs"
            or benchmark.get("measured_benefit") is not True
            or any(gain <= minimum_gain for gain in benchmark.get("paired_mean_gain", {}).values())
        ):
            reasons.append("measured_paired_benefit_required")
        _json_value(hardware)
        if type(hardware) is not dict:
            raise ValueError("Hardware assessment required.")
        for field in ("required_memory_gb", "available_memory_gb", "required_seconds", "available_seconds"):
            number = hardware.get(field)
            if type(number) not in (int, float) or not math.isfinite(number) or number <= 0:
                raise ValueError("Finite positive hardware requirements/capacity required.")
        if (
            hardware["available_memory_gb"] < hardware["required_memory_gb"]
            or hardware["available_seconds"] < hardware["required_seconds"]
            or hardware.get("resource_id") != evidence.get("resource_id")
            or not _text(hardware.get("assessment_id"))
            or not _verified(review_verifier, {"kind": "hardware_assessment", "assessment": hardware})
        ):
            reasons.append("hardware_gate_blocked")
        _json_value(human_approval)
        if (
            type(human_approval) is not dict
            or human_approval.get("actor_type") != "human"
            or human_approval.get("approved") is not True
            or not _text(human_approval.get("actor_id"))
            or not _text(human_approval.get("approval_id"))
            or human_approval.get("resource_id") != evidence.get("resource_id")
            or not _text(benchmark.get("benchmark_digest"))
            or human_approval.get("benchmark_digest") != benchmark.get("benchmark_digest")
            or human_approval.get("evidence_digest") != _digest(evidence)
            or human_approval.get("hardware_digest") != _digest(hardware)
            or not _verified(review_verifier, {"kind": "human_approval", "approval": human_approval})
        ):
            reasons.append("human_approval_required")
    except Exception as exc:
        reasons.append(str(exc) or "malformed_expansion_request")
    return {
        "status": "eligible_for_human_directed_expansion" if not reasons else "blocked",
        "expansion_allowed": not reasons,
        "automatic_integration": False,
        "canonical_truth": False,
        "benchmark": benchmark,
        "reasons": sorted(set(reasons)),
    }
