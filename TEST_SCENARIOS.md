# Test Scenarios

## Search Flow

1. Send `POST /ondc/search` using `postman/payloads/search.json`.
2. Expect HTTP `200` with ACK.
3. Send `POST /ondc/on_search` using `postman/payloads/on_search.json`.
4. Expect HTTP `200` with ACK.
5. Verify `/ondc/transactions` contains command and callback events for the same `transaction_id`.

## Select Flow

1. Send `POST /ondc/select` using `postman/payloads/select.json`.
2. Expect HTTP `200` with ACK.
3. Send `POST /ondc/on_select` using `postman/payloads/on_select.json`.
4. Expect HTTP `200` with ACK.
5. Verify quote, folio, and payment option callback payload is persisted.

## Init Flow

1. Send `POST /ondc/init` using `postman/payloads/init.json`.
2. Expect HTTP `200` with ACK.
3. Send `POST /ondc/on_init` using `postman/payloads/on_init.json`.
4. Expect HTTP `200` with ACK.
5. Verify draft order/payment callback event is persisted.

## Confirm Flow

1. Send `POST /ondc/confirm` using `postman/payloads/confirm.json`.
2. Expect HTTP `200` with ACK.
3. Send `POST /ondc/on_confirm` using `postman/payloads/on_confirm.json`.
4. Expect HTTP `200` with ACK.
5. Verify accepted/rejected order state is persisted.

## Status Flow

1. Send `POST /ondc/status` using `postman/payloads/status.json`.
2. Expect HTTP `200` with ACK.
3. Send `POST /ondc/on_status` using `postman/payloads/on_status.json`.
4. Expect HTTP `200` with ACK.
5. Verify payment/fulfillment state is persisted.

## Update Flow

1. Send `POST /ondc/update` using `postman/payloads/update.json`.
2. Expect HTTP `200` with ACK.
3. Send `POST /ondc/on_update` using `postman/payloads/on_update.json`.
4. Expect HTTP `200` with ACK.
5. Verify payment retry, fulfillment success/failure, SIP update, or redemption update event is persisted.

## Cancel Flow

1. Send `POST /ondc/cancel` using `postman/payloads/cancel.json`.
2. Expect HTTP `200` with ACK.
3. Send `POST /ondc/on_cancel` using `postman/payloads/on_cancel.json`.
4. Expect HTTP `200` with ACK.
5. Verify cancelled state is persisted.

## Negative Scenarios

1. Re-send the same payload twice and expect the second response to be HTTP `409`.
2. Change `context.domain` to an invalid value and expect HTTP `422`.
3. Change `context.action` so it does not match the endpoint and expect HTTP `400`.
4. Remove `context.transaction_id` and expect HTTP `422`.
5. Remove `context.message_id` and expect HTTP `422`.
6. Change `context.ttl` to an invalid value and expect HTTP `422`.
