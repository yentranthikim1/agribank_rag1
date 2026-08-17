"""Prepare the Buoi 6 runtime without creating a Python environment."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
EXPECTED_PYTHON = ROOT.parent / "buoi_05" / ".venv" / "Scripts" / "python.exe"
ENV_FILE = ROOT / ".env"
REQUIRED_ENV = {
    "GEMINI_API_KEY": "",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DB": "rag_db",
    "POSTGRES_USER": "postgres",
    "POSTGRES_PASSWORD": "",
}
PACKAGES = {
    "streamlit": "streamlit",
    "google-genai": "google.genai",
    "chromadb": "chromadb",
    "psycopg": "psycopg",
    "python-dotenv": "dotenv",
}


def ensure_env_file() -> None:
    if not ENV_FILE.exists():
        example = ROOT / ".env.example"
        ENV_FILE.write_text(example.read_text(encoding="utf-8") if example.exists() else "", encoding="utf-8")

    existing = ENV_FILE.read_text(encoding="utf-8").splitlines()
    names = {line.split("=", 1)[0].strip() for line in existing if "=" in line and not line.lstrip().startswith("#")}
    missing = [f"{name}={value}" for name, value in REQUIRED_ENV.items() if name not in names]
    if missing:
        suffix = "\n" if existing and existing[-1] else ""
        ENV_FILE.write_text(ENV_FILE.read_text(encoding="utf-8") + suffix + "\n".join(missing) + "\n", encoding="utf-8")


def check_interpreter() -> bool:
    if Path(sys.executable).resolve() != EXPECTED_PYTHON.resolve():
        print(f"FAIL Python interpreter: expected {EXPECTED_PYTHON}")
        print(f"FAIL Python interpreter: using {sys.executable}")
        print("User action: create or restore RAG/rag_foundation/buoi_05/.venv, then run this script with its Scripts/python.exe.")
        return False
    print(f"PASS Python interpreter: {sys.executable}")
    return True


def install_and_check_packages() -> bool:
    missing = [package for package, module in PACKAGES.items() if importlib.util.find_spec(module) is None]
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        result = subprocess.run([sys.executable, "-m", "pip", "install", *missing], check=False)
        if result.returncode != 0:
            print("FAIL package installation")
            return False

    passed = True
    for package, module in PACKAGES.items():
        try:
            __import__(module)
            print(f"PASS import {package}")
        except Exception:
            print(f"FAIL import {package}")
            passed = False
    return passed


def setup_chroma() -> None:
    server_url = os.getenv("CHROMA_SERVER_URL", "http://localhost:8000/api/v2/heartbeat")
    try:
        with urlopen(server_url, timeout=2):
            print(f"PASS ChromaDB: Server ({server_url.rsplit('/', 1)[0]})")
            return
    except (OSError, URLError, ValueError):
        pass

    import chromadb

    storage = ROOT / "storage" / "chroma"
    storage.mkdir(parents=True, exist_ok=True)
    chromadb.PersistentClient(path=str(storage))
    print(f"PASS ChromaDB: Embedded Local ({storage})")


def setup_postgres() -> None:
    from dotenv import dotenv_values
    import psycopg

    values = dotenv_values(ENV_FILE)
    password = values.get("POSTGRES_PASSWORD") or None
    settings = {
        "host": values.get("POSTGRES_HOST", "localhost"),
        "port": values.get("POSTGRES_PORT", "5432"),
        "user": values.get("POSTGRES_USER", "postgres"),
        "password": password,
    }
    if not password:
        print("FAIL PostgreSQL: POSTGRES_PASSWORD is empty")
        print("User action: install PostgreSQL from https://www.postgresql.org/download/ if needed.")
        print("User action: start PostgreSQL, remember the postgres password, enter it in .env, then rerun this script.")
        return

    try:
        with psycopg.connect(dbname="postgres", **settings, autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (values.get("POSTGRES_DB", "rag_db"),))
                exists = cursor.fetchone() is not None
                if not exists:
                    cursor.execute('CREATE DATABASE "rag_db"')
        print("PASS PostgreSQL: server reachable")
        with psycopg.connect(dbname="rag_db", **settings):
            pass
        print("PASS PostgreSQL database: rag_db")
    except Exception:
        print("FAIL PostgreSQL: cannot connect or create database rag_db")
        print("User action: install PostgreSQL from https://www.postgresql.org/download/ if needed, start it, then verify POSTGRES_PASSWORD in .env.")


def main() -> int:
    ensure_env_file()
    if not check_interpreter():
        return 1
    if not install_and_check_packages():
        return 1
    try:
        setup_chroma()
    except Exception:
        print("FAIL ChromaDB: embedded client could not be initialized")
    setup_postgres()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())