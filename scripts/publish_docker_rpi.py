from __future__ import annotations

from common import (
    DOCKER_HUB_NAMESPACE,
    IMAGE_NAME,
    load_remote_host_arg,
    run,
)

from ru_uk_bot._version import __version__

DOCKER_HUB_IMAGE = f"{DOCKER_HUB_NAMESPACE}/{IMAGE_NAME}"


def main() -> None:
    remote_host = load_remote_host_arg()

    source_tag = f"{IMAGE_NAME}:{__version__}"
    version_tag = f"{DOCKER_HUB_IMAGE}:{__version__}"
    latest_tag = f"{DOCKER_HUB_IMAGE}:latest"

    run(
        "ssh",
        "-t",
        remote_host,
        (
            f"sudo docker image inspect {source_tag} >/dev/null "
            f"&& sudo docker tag {source_tag} {version_tag} "
            f"&& sudo docker tag {source_tag} {latest_tag} "
            f"&& sudo docker push {version_tag} "
            f"&& sudo docker push {latest_tag}"
        ),
    )

    print()
    print(f"Published: {version_tag}")
    print(f"Published: {latest_tag}")


if __name__ == "__main__":
    main()
