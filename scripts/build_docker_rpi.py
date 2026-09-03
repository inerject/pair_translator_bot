from __future__ import annotations

import shutil
import subprocess
import tarfile
import tempfile
import uuid
from pathlib import Path

from common import IMAGE_NAME, load_remote_host_arg, run

from pair_translator_bot._version import __version__

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    remote_host = load_remote_host_arg()

    version_tag = f"{IMAGE_NAME}:{__version__}"
    latest_tag = f"{IMAGE_NAME}:latest"

    build_id = uuid.uuid4().hex

    remote_dir = f"/tmp/{IMAGE_NAME}-build-{build_id}"
    remote_context = f"/tmp/{IMAGE_NAME}-context-{build_id}.tar.gz"

    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        stage_dir = temp_dir / "context"
        archive_path = temp_dir / "context.tar.gz"

        stage_dir.mkdir()

        shutil.copy2(PROJECT_ROOT / "pyproject.toml", stage_dir)
        shutil.copy2(PROJECT_ROOT / "Dockerfile", stage_dir)
        shutil.copy2(PROJECT_ROOT / ".dockerignore", stage_dir)

        shutil.copytree(
            PROJECT_ROOT / "pair_translator_bot",
            stage_dir / "pair_translator_bot",
        )

        with tarfile.open(archive_path, "w:gz") as archive:
            archive.add(stage_dir, arcname=".")

        try:
            run(
                "scp",
                str(archive_path),
                f"{remote_host}:{remote_context}",
            )

            run(
                "ssh",
                remote_host,
                f"mkdir -p {remote_dir} && tar -xzf {remote_context} -C {remote_dir}",
            )

            run(
                "ssh",
                "-t",
                remote_host,
                (
                    f"sudo docker build -t {version_tag} {remote_dir} "
                    f"&& sudo docker tag {version_tag} {latest_tag}"
                ),
            )

            print()
            print(f"Built: {version_tag}")
            print(f"Tagged: {latest_tag}")

        finally:
            subprocess.run(
                [
                    "ssh",
                    remote_host,
                    f"rm -rf {remote_dir} {remote_context}",
                ],
                check=False,
            )


if __name__ == "__main__":
    main()
