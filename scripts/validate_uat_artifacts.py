"""Validate Buyer NP UAT Postman artifacts against FastAPI OpenAPI examples."""

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app
from generate_postman import COLLECTION, ENDPOINTS, ENVIRONMENT, PAYLOADS


REQUIRED_ENV_KEYS = {
    "base_url",
    "domain",
    "version",
    "transaction_id",
    "message_id",
    "bap_id",
    "bap_uri",
}


def flatten_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flat: list[dict[str, Any]] = []
    for item in items:
        if "item" in item:
            flat.extend(flatten_items(item["item"]))
        else:
            flat.append(item)
    return flat


def postman_path(raw_url: str) -> str:
    return raw_url.replace("{{base_url}}", "")


def openapi_first_example(path: str) -> dict[str, Any]:
    operation = app.openapi()["paths"][path]["post"]
    content = operation["requestBody"]["content"]["application/json"]
    examples = content.get("examples") or {}
    if not examples:
        raise AssertionError(f"No OpenAPI examples found for {path}")
    first = next(iter(examples.values()))
    return first["value"]


def main() -> None:
    collection = json.loads(COLLECTION.read_text(encoding="utf-8"))
    environment = json.loads(ENVIRONMENT.read_text(encoding="utf-8"))

    items = flatten_items(collection["item"])
    post_requests = {
        postman_path(item["request"]["url"]): item
        for item in items
        if item["request"]["method"] == "POST"
    }

    expected_by_path = {endpoint["path"]: endpoint for endpoint in ENDPOINTS}
    missing = sorted(set(expected_by_path) - set(post_requests))
    extra = sorted(set(post_requests) - set(expected_by_path))
    if missing or extra:
        raise AssertionError(f"Postman path mismatch | missing={missing} extra={extra}")

    for path, endpoint in expected_by_path.items():
        postman_body = json.loads(post_requests[path]["request"]["body"]["raw"])
        payload_file = PAYLOADS / endpoint["payload_name"]
        file_body = json.loads(payload_file.read_text(encoding="utf-8"))
        openapi_body = openapi_first_example(path)

        if postman_body != endpoint["payload"]:
            raise AssertionError(f"Postman body does not match generator payload for {path}")
        if file_body != endpoint["payload"]:
            raise AssertionError(f"Payload file does not match generator payload for {path}")
        if openapi_body != endpoint["payload"]:
            raise AssertionError(f"OpenAPI first example does not match generator payload for {path}")

    env_keys = {item["key"] for item in environment["values"]}
    missing_env = sorted(REQUIRED_ENV_KEYS - env_keys)
    if missing_env:
        raise AssertionError(f"Missing environment keys: {missing_env}")

    print("uat_artifacts_ok")
    print(f"validated_endpoints={len(expected_by_path)}")
    print(f"validated_env_keys={len(REQUIRED_ENV_KEYS)}")


if __name__ == "__main__":
    main()
