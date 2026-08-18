from __future__ import annotations

from src.core.pillar710_sprint_bb_regression_cert import (
    NEXT_PILLAR_SLOT,
    SPRINT_BB_PILLARS,
    sprint_bb_regression_cert,
)


def test_sprint_bb_pillars():
    assert SPRINT_BB_PILLARS == ['705', '706', '707', '708', '709', '710']


def test_next_pillar_slot():
    assert NEXT_PILLAR_SLOT == 711


def test_regression_returns_dict():
    assert isinstance(sprint_bb_regression_cert(), dict)


def test_regression_status():
    cert = sprint_bb_regression_cert()
    assert cert['status'] == 'SPRINT_BB_REGRESSION_PASSED'


def test_regression_all_passed():
    cert = sprint_bb_regression_cert()
    assert cert['all_passed'] is True


def test_regression_has_expected_checks():
    cert = sprint_bb_regression_cert()
    assert len(cert['pillar_checks']) == 5


def test_regression_each_check_passes():
    cert = sprint_bb_regression_cert()
    for check in cert['pillar_checks']:
        assert check['passed'] is True


def test_regression_checks_statuses():
    cert = sprint_bb_regression_cert()
    expected = {
        '705': 'ARCHITECTURE_LIMIT_CERTIFIED',
        '706': 'ARCHITECTURE_LIMIT_CERTIFIED',
        '707': 'IRREDUCIBLE_AT_5D',
        '708': 'NATURAL',
        '709': 'KK_HIGGS_INVISIBLE_AT_LHC',
    }
    for check in cert['pillar_checks']:
        assert check['actual_status'] == expected[check['pillar']]


def test_regression_summary_mentions_survey():
    cert = sprint_bb_regression_cert()
    assert 'survey' in cert['summary'].lower()
