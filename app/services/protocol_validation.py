from fastapi import HTTPException

from app.schemas.ondc import CALLBACK_ACTIONS, COMMAND_ACTIONS, FIS14ProtocolRequest


class ProtocolValidationService:
    def validate_command(self, request: FIS14ProtocolRequest, expected_action: str) -> None:
        self._validate_expected_action(request, expected_action)
        if request.context.action not in COMMAND_ACTIONS:
            raise HTTPException(status_code=400, detail=f"{request.context.action} is not a Buyer NP command action")

    def validate_callback(self, request: FIS14ProtocolRequest, expected_action: str) -> None:
        self._validate_expected_action(request, expected_action)
        if not request.context.message_id or not request.context.message_id.strip():
            raise HTTPException(status_code=400, detail="context.message_id is required for callbacks")
        if request.context.action not in CALLBACK_ACTIONS:
            raise HTTPException(status_code=400, detail=f"{request.context.action} is not a callback action")
        command_action = expected_action.replace("on_", "", 1)
        if command_action not in COMMAND_ACTIONS:
            raise HTTPException(status_code=400, detail=f"unsupported callback action: {expected_action}")

    def _validate_expected_action(self, request: FIS14ProtocolRequest, expected_action: str) -> None:
        if request.context.action != expected_action:
            raise HTTPException(
                status_code=400,
                detail=f"context.action must be '{expected_action}' for this endpoint",
            )


protocol_validation_service = ProtocolValidationService()
