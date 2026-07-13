from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class ActionMockCouponIssuance(Action):
    """Deterministic local coupon issuer used until a rewards MCP tool exists."""

    def name(self) -> Text:
        return "action_mock_coupon_issuance"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        # MOCK — replace once a real MCP server for coupon issuance is registered.
        order_id = str(tracker.get_slot("order_id") or "CHIPOTLE").upper()
        token = "".join(ch for ch in order_id if ch.isalnum())[-6:] or "MEAL"
        remedy = str(tracker.get_slot("suggested_remedy") or "next_meal_discount")
        prefix = "CREDIT" if remedy == "item_credit" else "FRESH"
        value = "$8 item credit" if remedy == "item_credit" else "20% off one entrée"
        return [
            SlotSet("coupon_code", f"{prefix}-{token}"),
            SlotSet("coupon_value", value),
            SlotSet("coupon_expiration", "30 days from today"),
            SlotSet("coupon_issued", True),
        ]
