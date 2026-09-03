from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from dotenv import dotenv_values

IMAGE_NAME = "ru-uk-bot"
DOCKER_HUB_NAMESPACE = "inerject"


def load_remote_host_arg() -> str:
    env_file = parse_env_file_arg()
    return load_remote_host(env_file)


def parse_env_file_arg() -> Path:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env-file",
        type=Path,
        required=True,
    )
    return parser.parse_args().env_file


def load_remote_host(env_file: Path) -> str:
    env = dotenv_values(env_file)

    remote_host = env.get("DOCKER_REMOTE_HOST")
    if not remote_host:
        raise RuntimeError(f"DOCKER_REMOTE_HOST is not set in {env_file}")

    return remote_host


def run(*args: str) -> None:
    subprocess.run(args, check=True)
