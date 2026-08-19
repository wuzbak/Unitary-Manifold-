"""
LithosOS — Configuration
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path

APP_DIR = Path(__file__).parent
LITHIC_DIR = APP_DIR.parent
REPO_ROOT = LITHIC_DIR.parent

@dataclass
class LithosConfig:
    db_path: Path = field(default_factory=lambda: Path(os.getenv("LITHOS_DB_PATH", str(LITHIC_DIR / "data" / "lithos.db"))))
    knowledge_dir: Path = field(default_factory=lambda: LITHIC_DIR)
    mindat_api_key: str = field(default_factory=lambda: os.getenv("MINDAT_API_KEY", ""))
    inaturalist_api_token: str = field(default_factory=lambda: os.getenv("INAT_API_TOKEN", ""))
    local_model_path: Path = field(default_factory=lambda: LITHIC_DIR / "app" / "models" / "mineral_id.onnx")
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    local_llm_url: str = field(default_factory=lambda: os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate"))
    local_llm_model: str = field(default_factory=lambda: os.getenv("LOCAL_LLM_MODEL", "llama3.2:3b"))
    offline_mode: bool = field(default_factory=lambda: os.getenv("LITHOS_OFFLINE", "false").lower() == "true")
    host: str = field(default_factory=lambda: os.getenv("LITHOS_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("LITHOS_PORT", "7861")))
    sync_url: str = field(default_factory=lambda: os.getenv("LITHOS_SYNC_URL", "https://raw.githubusercontent.com/wuzbak/Private/main/lithic/data/"))
    sync_interval_hours: int = field(default_factory=lambda: int(os.getenv("LITHOS_SYNC_INTERVAL", "24")))
    gibberlink_secret: str = field(default_factory=lambda: os.getenv("GIBBERLINK_SECRET", ""))
    gibberlink_enabled: bool = field(default_factory=lambda: os.getenv("GIBBERLINK_ENABLED", "false").lower() == "true")
    is_android: bool = field(default_factory=lambda: os.path.exists("/data/data/com.termux") or os.getenv("LITHOS_PLATFORM", "") == "android")

    def __post_init__(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

_config: LithosConfig | None = None

def get_config() -> LithosConfig:
    global _config
    if _config is None:
        env_file = LITHIC_DIR / ".env"
        if env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
            except ImportError:
                pass
        _config = LithosConfig()
    return _config
