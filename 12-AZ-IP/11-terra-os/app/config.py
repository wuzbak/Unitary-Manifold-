"""
TerraOS — Configuration
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path

APP_DIR = Path(__file__).parent
TERRA_DIR = APP_DIR.parent
REPO_ROOT = TERRA_DIR.parent

@dataclass
class TerraConfig:
    db_path: Path = field(default_factory=lambda: Path(os.getenv("TERRA_DB_PATH", str(TERRA_DIR / "data" / "terra.db"))))
    knowledge_dir: Path = field(default_factory=lambda: TERRA_DIR)
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    local_llm_url: str = field(default_factory=lambda: os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate"))
    local_llm_model: str = field(default_factory=lambda: os.getenv("LOCAL_LLM_MODEL", "llama3.2:3b"))
    offline_mode: bool = field(default_factory=lambda: os.getenv("TERRA_OFFLINE", "false").lower() == "true")
    host: str = field(default_factory=lambda: os.getenv("TERRA_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("TERRA_PORT", "7862")))
    sync_url: str = field(default_factory=lambda: os.getenv("TERRA_SYNC_URL", "https://raw.githubusercontent.com/wuzbak/Private/main/terra/data/"))
    sync_interval_hours: int = field(default_factory=lambda: int(os.getenv("TERRA_SYNC_INTERVAL", "24")))
    gibberlink_secret: str = field(default_factory=lambda: os.getenv("GIBBERLINK_SECRET", ""))
    gibberlink_enabled: bool = field(default_factory=lambda: os.getenv("GIBBERLINK_ENABLED", "false").lower() == "true")
    is_android: bool = field(default_factory=lambda: os.path.exists("/data/data/com.termux") or os.getenv("TERRA_PLATFORM", "") == "android")

    def __post_init__(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

_config: TerraConfig | None = None

def get_config() -> TerraConfig:
    global _config
    if _config is None:
        env_file = TERRA_DIR / ".env"
        if env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
            except ImportError:
                pass
        _config = TerraConfig()
    return _config
