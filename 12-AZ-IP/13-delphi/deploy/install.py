"""
DelPhi — Python install helper
"""
import subprocess
import sys
from pathlib import Path

DEPLOY = Path(__file__).parent
REPO = DEPLOY.parent


def main() -> None:
    print("Installing DelPhi dependencies…")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(DEPLOY / "requirements.txt")])

    print("Seeding database…")
    sys.path.insert(0, str(REPO.parent))
    from delphi.app.db.seed import seed_database
    result = seed_database()
    print(f"Seeded: {result}")
    print("Done! Launch with: uvicorn delphi.app.main:app --host 0.0.0.0 --port 7863")


if __name__ == "__main__":
    main()
