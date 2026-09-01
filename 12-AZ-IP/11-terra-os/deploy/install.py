#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""TerraOS installer helpers used by tests and local setup flows."""
from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

CORE_REQUIREMENTS = [
    'fastapi>=0.100.0',
    'uvicorn[standard]>=0.22.0',
    'pydantic>=2.0.0',
    'httpx>=0.24.0',
    'pytest>=7.0.0',
    'pytest-asyncio>=0.21.0',
]


def _is_android() -> bool:
    return os.path.exists('/data/data/com.termux') or os.getenv('TERRA_PLATFORM', '') == 'android'


def _detect_platform() -> str:
    if _is_android():
        return 'android'
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    if system == 'windows':
        return 'windows'
    if system == 'linux':
        return 'linux'
    return 'unknown'


def _check_python_version() -> bool:
    return sys.version_info >= (3, 9)


def _create_directories(base_dir: Path) -> list[Path]:
    data_dir = Path(base_dir) / 'data'
    logs_dir = Path(base_dir) / 'logs'
    export_dir = Path(base_dir) / 'exports'
    for path in (data_dir, logs_dir, export_dir):
        path.mkdir(parents=True, exist_ok=True)
    return [data_dir, logs_dir, export_dir]


def _init_database(db_path: Path) -> bool:
    from terra.app.db.schema import init_db
    init_db(Path(db_path))
    return Path(db_path).exists()


def _seed_database(db_path: Path) -> bool:
    from terra.app.db.seed import seed_database
    seed_database(Path(db_path), verbose=False)
    return True


def _write_env_file(db_path: Path, env_path: Path) -> Path:
    env_path = Path(env_path)
    env_path.write_text(
        f'TERRA_DB_PATH={Path(db_path)}\nTERRA_OFFLINE=false\nTERRA_PORT=7862\n',
        encoding='utf-8',
    )
    return env_path


def run_install(db_path: Path | None = None, skip_pip: bool = False) -> dict[str, object]:
    app_root = Path(__file__).resolve().parents[1]
    target_db = Path(db_path) if db_path is not None else app_root / 'data' / 'terra.db'
    created_dirs = _create_directories(target_db.parent.parent if target_db.parent.name == 'data' else app_root)
    python_ok = _check_python_version()
    db_ok = _init_database(target_db)
    seed_ok = _seed_database(target_db) if db_ok else False
    env_path = _write_env_file(target_db, target_db.parent / '.env')
    return {
        'platform': _detect_platform(),
        'db_path': str(target_db),
        'env_path': str(env_path),
        'created_directories': [str(path) for path in created_dirs],
        'steps': {
            'python_version': python_ok,
            'skip_pip': skip_pip,
            'database_init': db_ok,
            'database_seed': seed_ok,
            'env_file': env_path.exists(),
        },
    }
