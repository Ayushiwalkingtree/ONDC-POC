"""Mock ONDC FIS14 (Mutual Funds) payloads derived from ONDC-FIS-Specifications examples."""

MOCK_SCHEMES = [
    {
        "id": "138",
        "descriptor": {"name": "ABC Mid Cap Fund", "code": "SCHEME"},
        "category_ids": ["1101"],
        "creator": {"descriptor": {"name": "ABC Mutual Fund"}},
        "matched": True,
        "tags": [
            {
                "display": True,
                "descriptor": {"name": "Scheme Information", "code": "SCHEME_INFORMATION"},
                "list": [
                    {"descriptor": {"name": "Status", "code": "STATUS"}, "value": "active"},
                    {"descriptor": {"name": "Exit Load", "code": "EXIT_LOAD"}, "value": "1% on exit"},
                ],
            }
        ],
    },
    {
        "id": "12391",
        "descriptor": {"name": "XYZ Large Cap Fund", "code": "SCHEME"},
        "category_ids": ["1101"],
        "creator": {"descriptor": {"name": "XYZ Asset Management"}},
        "matched": True,
        "tags": [
            {
                "display": True,
                "descriptor": {"name": "Scheme Information", "code": "SCHEME_INFORMATION"},
                "list": [
                    {"descriptor": {"name": "Status", "code": "STATUS"}, "value": "active"},
                    {"descriptor": {"name": "Minimum SIP", "code": "MIN_SIP_AMOUNT"}, "value": "500"},
                ],
            }
        ],
    },
]


def mock_on_search_catalog() -> dict:
    return {
        "catalog": {
            "descriptor": {"name": "MF Seller POC"},
            "providers": [
                {
                    "id": "bpp_provider_id",
                    "descriptor": {"name": "Mutual Fund BPP Provider POC"},
                    "categories": [
                        {"id": "0", "descriptor": {"name": "Mutual Funds", "code": "MUTUAL_FUNDS"}},
                        {"id": "1", "descriptor": {"name": "Open Ended", "code": "OPEN_ENDED"}, "parent_category_id": "0"},
                        {"id": "11", "descriptor": {"name": "Equity", "code": "OPEN_ENDED_EQUITY"}, "parent_category_id": "1"},
                        {"id": "1101", "descriptor": {"name": "Mid Cap Fund", "code": "OPEN_ENDED_EQUITY_MIDCAP"}, "parent_category_id": "11"},
                    ],
                    "items": MOCK_SCHEMES,
                }
            ],
        }
    }


def mock_on_select_lumpsum(order: dict) -> dict:
    return {
        "order": {
            **order,
            "quote": {
                "price": {"currency": "INR", "value": "3000"},
                "breakup": [
                    {"title": "BASE_PRICE", "price": {"currency": "INR", "value": "3000"}},
                ],
            },
            "fulfillments": order.get("fulfillments", [])
            + [
                {
                    "id": "folio_ff_1",
                    "type": "LUMPSUM",
                    "customer": {"person": {"id": "pan:arrpp7771n"}},
                    "tags": [
                        {
                            "descriptor": {"code": "FOLIO_INFORMATION"},
                            "list": [
                                {"descriptor": {"code": "FOLIO_NUMBER"}, "value": "1234567890"},
                                {"descriptor": {"code": "HOLDING_PATTERN"}, "value": "SINGLE"},
                            ],
                        }
                    ],
                }
            ],
            "payments": [
                {
                    "type": "PRE-FULFILLMENT",
                    "collected_by": "BAP",
                    "params": {"amount": "3000", "currency": "INR", "transaction_id": "mock-txn-001"},
                }
            ],
        }
    }


def mock_on_init(order: dict) -> dict:
    return {
        "order": {
            **order,
            "state": "Created",
            "payments": [
                {
                    "type": "PRE-FULFILLMENT",
                    "status": "NOT-PAID",
                    "url": "https://mock-payment-gateway.example.com/pay/mock-order-001",
                    "params": {"amount": "3000", "currency": "INR"},
                }
            ],
        }
    }


def mock_on_confirm(order: dict) -> dict:
    return {
        "order": {
            **order,
            "state": "Accepted",
            "id": "order-mf-001",
        }
    }


def mock_on_status(order_id: str = "order-mf-001", payment_status: str = "PAID") -> dict:
    return {
        "order": {
            "id": order_id,
            "state": "In-progress",
            "payments": [
                {
                    "type": "PRE-FULFILLMENT",
                    "status": payment_status,
                    "params": {"transaction_id": "mock-payment-txn-001"},
                }
            ],
            "fulfillments": [
                {
                    "id": "ff_123",
                    "type": "LUMPSUM",
                    "state": {"descriptor": {"code": "PAYMENT_SUCCESS" if payment_status == "PAID" else "PAYMENT_PENDING"}},
                }
            ],
        }
    }


def mock_on_update(order_id: str = "order-mf-001") -> dict:
    return {
        "order": {
            "id": order_id,
            "state": "COMPLETED",
            "fulfillments": [
                {
                    "id": "ff_123",
                    "type": "LUMPSUM",
                    "state": {"descriptor": {"code": "SUCCESSFUL"}},
                }
            ],
        }
    }


def mock_on_cancel(order_id: str = "order-mf-001") -> dict:
    return {"order": {"id": order_id, "state": "CANCELLED"}}


def mock_on_track(order_id: str = "order-mf-001") -> dict:
    return {
        "tracking": {
            "id": f"track-{order_id}",
            "url": f"https://seller-app.example.com/tracking/{order_id}",
            "status": "active",
        }
    }


def mock_on_support(ref_id: str = "order-mf-001") -> dict:
    return {
        "support": {
            "ref_id": ref_id,
            "phone": "+91-9999999999",
            "email": "support@seller-app.example.com",
        }
    }
