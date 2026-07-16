from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class ActionMockLiveOffers(Action):
    """Returns a deterministic local offers catalog until a live offers MCP service exists."""

    def name(self) -> Text:
        return "action_mock_live_offers"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        # MOCK — replace once a real MCP server for live offers is registered.
        message = str((tracker.latest_message or {}).get("text") or "").lower()
        sensitive_markers = ("password", "passcode", "card number", "credit card", "cvv")
        unavailable_markers = ("service unavailable", "offers unavailable", "timeout")
        no_match_markers = ("birthday", "student", "bogo", "buy one get one")

        if any(marker in message for marker in sensitive_markers):
            return [
                SlotSet("offers_lookup_result", "sensitive_data"),
                SlotSet("live_offers_summary", None),
            ]
        if any(marker in message for marker in unavailable_markers):
            return [
                SlotSet("offers_lookup_result", "unavailable"),
                SlotSet("live_offers_summary", None),
            ]
        if any(marker in message for marker in no_match_markers):
            return [
                SlotSet("offers_lookup_result", "no_match"),
                SlotSet("live_offers_summary", None),
            ]

        summary = (
            "• Rewards app entrée perk — 20% off one qualifying entrée; expires April 30, 2026. "
            "Use the Chipotle app while signed in, add one qualifying entrée, and apply the offer before checkout.\n"
            "• Delivery week deal — $0 delivery fee on a qualifying digital delivery order; expires April 7, 2026. "
            "Order in the Chipotle app or on chipotle.com and apply the offer at checkout.\n"
            "Each offer is one use per account, while available, and cannot be stacked with another offer."
        )
        return [
            SlotSet("offers_lookup_result", "available"),
            SlotSet("live_offers_summary", summary),
        ]
