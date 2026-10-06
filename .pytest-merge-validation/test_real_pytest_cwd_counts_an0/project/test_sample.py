from pathlib import Path
import pytest
def test_cwd(): assert Path.cwd() == Path('/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/.pytest-merge-validation/test_real_pytest_cwd_counts_an0/project')
@pytest.mark.skip(reason='explicit skip')
def test_skip(): pass
