"""Generate Buyer NP UAT Postman, payload, and curl artifacts from FIS14 examples."""

import json
from pathlib import Path
from typing import Any

from app.schemas import examples as ex


OUT = Path("postman")
PAYLOADS = OUT / "payloads"
COLLECTION = OUT / "ONDC_MF_BUYER_NP_UAT.postman_collection.json"
ENVIRONMENT = OUT / "ONDC_MF_BUYER_NP_UAT.postman_environment.json"
CURL_DOC = Path("CURL_EXAMPLES.md")

ENDPOINTS: list[dict[str, Any]] = [
    {
        "name": "search",
        "path": "/ondc/search",
        "payload_name": "search.json",
        "payload": ex.SEARCH,
        "description": "Buyer NP search command for MF scheme discovery.",
        "folder": "01 Search Flow",
    },
    {
        "name": "on_search",
        "path": "/ondc/on_search",
        "payload_name": "on_search.json",
        "payload": ex.ON_SEARCH,
        "description": "BPP catalog callback received by Buyer NP.",
        "folder": "01 Search Flow",
    },
    {
        "name": "select",
        "path": "/ondc/select",
        "payload_name": "select.json",
        "payload": ex.SELECT_LUMPSUM,
        "description": "Buyer NP selection command for a lumpsum MF order.",
        "folder": "02 Select Flow",
    },
    {
        "name": "on_select",
        "path": "/ondc/on_select",
        "payload_name": "on_select.json",
        "payload": ex.ON_SELECT_LUMPSUM,
        "description": "BPP quote and folio callback received by Buyer NP.",
        "folder": "02 Select Flow",
    },
    {
        "name": "init",
        "path": "/ondc/init",
        "payload_name": "init.json",
        "payload": ex.INIT_LUMPSUM,
        "description": "Buyer NP order initialization command.",
        "folder": "03 Init Flow",
    },
    {
        "name": "on_init",
        "path": "/ondc/on_init",
        "payload_name": "on_init.json",
        "payload": ex.ON_INIT_LUMPSUM,
        "description": "BPP draft order and payment callback received by Buyer NP.",
        "folder": "03 Init Flow",
    },
    {
        "name": "confirm",
        "path": "/ondc/confirm",
        "payload_name": "confirm.json",
        "payload": ex.CONFIRM_LUMPSUM,
        "description": "Buyer NP order confirmation command.",
        "folder": "04 Confirm Flow",
    },
    {
        "name": "on_confirm",
        "path": "/ondc/on_confirm",
        "payload_name": "on_confirm.json",
        "payload": ex.ON_CONFIRM_LUMPSUM,
        "description": "BPP order acceptance callback received by Buyer NP.",
        "folder": "04 Confirm Flow",
    },
    {
        "name": "status",
        "path": "/ondc/status",
        "payload_name": "status.json",
        "payload": ex.STATUS_REQUEST,
        "description": "Buyer NP order status command.",
        "folder": "05 Status Flow",
    },
    {
        "name": "on_status",
        "path": "/ondc/on_status",
        "payload_name": "on_status.json",
        "payload": ex.ON_STATUS,
        "description": "BPP status callback received by Buyer NP.",
        "folder": "05 Status Flow",
    },
    {
        "name": "update",
        "path": "/ondc/update",
        "payload_name": "update.json",
        "payload": ex.UPDATE_PAYMENT,
        "description": "Buyer NP update command, such as requesting a new payment option.",
        "folder": "06 Update Flow",
    },
    {
        "name": "on_update",
        "path": "/ondc/on_update",
        "payload_name": "on_update.json",
        "payload": ex.ON_UPDATE,
        "description": "BPP payment or fulfillment update callback received by Buyer NP.",
        "folder": "06 Update Flow",
    },
    {
        "name": "cancel",
        "path": "/ondc/cancel",
        "payload_name": "cancel.json",
        "payload": ex.CANCEL_REQUEST,
        "description": "Buyer NP cancellation command.",
        "folder": "07 Cancel Flow",
    },
    {
        "name": "on_cancel",
        "path": "/ondc/on_cancel",
        "payload_name": "on_cancel.json",
        "payload": ex.ON_CANCEL,
        "description": "BPP cancellation callback received by Buyer NP.",
        "folder": "07 Cancel Flow",
    },
    {
        "name": "track",
        "path": "/ondc/track",
        "payload_name": "track.json",
        "payload": ex.TRACK_REQUEST,
        "description": "Buyer NP tracking command.",
        "folder": "08 Track Flow",
    },
    {
        "name": "on_track",
        "path": "/ondc/on_track",
        "payload_name": "on_track.json",
        "payload": ex.ON_TRACK,
        "description": "BPP tracking callback received by Buyer NP.",
        "folder": "08 Track Flow",
    },
    {
        "name": "support",
        "path": "/ondc/support",
        "payload_name": "support.json",
        "payload": ex.SUPPORT_REQUEST,
        "description": "Buyer NP support command.",
        "folder": "09 Support Flow",
    },
    {
        "name": "on_support",
        "path": "/ondc/on_support",
        "payload_name": "on_support.json",
        "payload": ex.ON_SUPPORT,
        "description": "BPP support callback received by Buyer NP.",
        "folder": "09 Support Flow",
    },
]


def request_item(endpoint: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": endpoint["name"],
        "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "url": "{{base_url}}" + endpoint["path"],
            "description": endpoint["description"],
            "body": {
                "mode": "raw",
                "raw": json.dumps(endpoint["payload"], indent=2),
                "options": {"raw": {"language": "json"}},
            },
        },
    }


def grouped_items() -> list[dict[str, Any]]:
    folders: dict[str, list[dict[str, Any]]] = {}
    for endpoint in ENDPOINTS:
        folders.setdefault(endpoint["folder"], []).append(request_item(endpoint))

    items = [
        {
            "name": "Health",
            "item": [
                {
                    "name": "health",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": "{{base_url}}/health",
                        "description": "Verify Buyer NP service startup.",
                    },
                }
            ],
        }
    ]
    items.extend({"name": folder, "item": requests} for folder, requests in folders.items())
    items.append(
        {
            "name": "Debug",
            "item": [
                {
                    "name": "transactions",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": "{{base_url}}/ondc/transactions",
                        "description": "List repository events for the current local session.",
                    },
                }
            ],
        }
    )
    return items


def write_collection() -> None:
    collection = {
        "info": {
            "_postman_id": "ondc-mf-buyer-np-uat-001",
            "name": "ONDC MF Buyer NP UAT (FIS14)",
            "description": (
                "Buyer NP UAT collection for Mutual Funds using ONDC:FIS14. "
                "Run command endpoints and their matching callback receiver examples in order."
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "variable": [{"key": "base_url", "value": "http://127.0.0.1:8000"}],
        "item": grouped_items(),
    }
    COLLECTION.write_text(json.dumps(collection, indent=2), encoding="utf-8")


def write_environment() -> None:
    env = {
        "id": "ondc-mf-buyer-np-uat-env-001",
        "name": "ONDC MF Buyer NP UAT - Local",
        "values": [
            {"key": "base_url", "value": "http://127.0.0.1:8000", "enabled": True},
            {"key": "domain", "value": "ONDC:FIS14", "enabled": True},
            {"key": "version", "value": "2.0.0", "enabled": True},
            {"key": "transaction_id", "value": ex.SEARCH["context"]["transaction_id"], "enabled": True},
            {"key": "message_id", "value": "{{$guid}}", "enabled": True},
            {"key": "bap_id", "value": ex.SEARCH["context"]["bap_id"], "enabled": True},
            {"key": "bap_uri", "value": ex.SEARCH["context"]["bap_uri"], "enabled": True},
        ],
        "_postman_variable_scope": "environment",
    }
    ENVIRONMENT.write_text(json.dumps(env, indent=2), encoding="utf-8")


def write_payloads() -> None:
    PAYLOADS.mkdir(parents=True, exist_ok=True)
    for endpoint in ENDPOINTS:
        (PAYLOADS / endpoint["payload_name"]).write_text(
            json.dumps(endpoint["payload"], indent=2),
            encoding="utf-8",
        )


def curl_command(endpoint: dict[str, Any]) -> str:
    payload_file = f"postman/payloads/{endpoint['payload_name']}"
    return (
        f"curl -X POST \"{{{{base_url}}}}{endpoint['path']}\" `\n"
        "  -H \"Content-Type: application/json\" `\n"
        f"  --data-binary \"@{payload_file}\""
    )


def write_curl_examples() -> None:
    lines = [
        "# CURL Examples",
        "",
        "Set `base_url` to your local or UAT Buyer NP URL before running these commands.",
        "",
        "```powershell",
        "$base_url = \"http://127.0.0.1:8000\"",
        "```",
        "",
    ]
    for endpoint in ENDPOINTS:
        command = curl_command(endpoint).replace("{{base_url}}", "$base_url")
        lines.extend(
            [
                f"## {endpoint['name']}",
                "",
                "```powershell",
                command,
                "```",
                "",
            ]
        )
    CURL_DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    write_collection()
    write_environment()
    write_payloads()
    write_curl_examples()
    print("Generated:", COLLECTION)
    print("Generated:", ENVIRONMENT)
    print("Generated payloads:", PAYLOADS)
    print("Generated:", CURL_DOC)


if __name__ == "__main__":
    main()
