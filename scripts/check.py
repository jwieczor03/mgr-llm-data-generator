"""Uruchom kontrole z katalogu głównego bez instalowania zależności."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICES = ("application-api", "generation-service", "validation-service")


def run(command, cwd=ROOT, env=None):
    print(f"\n> {' '.join(map(str, command))} ({cwd.relative_to(ROOT)})", flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def main():
    if sys.argv[1:] == ["integration"]:
        env = os.environ.copy()
        env.update(RUN_DATABASE_TESTS="1", RUN_COMPOSE_TESTS="1")
        run(["docker", "info"], env=env)
        run(["uv", "run", "--locked", "--no-sync", "pytest", "tests/test_database.py"], ROOT / "services/application-api", env)
        run(["uv", "run", "--locked", "--no-sync", "pytest", "-c", "pyproject.toml", "../../tests/integration/test_compose.py"], ROOT / "services/application-api", env)
    elif not sys.argv[1:]:
        # Check all Python sources and tests using the shared root configuration.
        run(["uv", "run", "--locked", "--no-sync", "ruff", "check", "../../services", "../../tests", "../../scripts"], ROOT / "services/application-api")
        for service in SERVICES:
            env = os.environ.copy()
            env.pop("RUN_DATABASE_TESTS", None)
            env.pop("RUN_COMPOSE_TESTS", None)
            run(["uv", "run", "--locked", "--no-sync", "pytest"], ROOT / "services" / service, env)
        for script in ("typecheck", "test", "build"):
            run(["npm", "run", script], ROOT / "apps/web")
    else:
        raise SystemExit("Użycie: python scripts/check.py [integration]")


if __name__ == "__main__":
    try:
        main()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"Kontrola nie powiodła się: {exc}", file=sys.stderr)
        sys.exit(1)
