from __future__ import annotations

from typing import List, Tuple

from marketplace_models import BuyerUpdate, OrderHandoff


REQUIRED_SLOTS: List[Tuple[str, str]] = [
    ("listing_card", "1:1"),
    ("search_result", "4:5"),
    ("order_confirmation", "16:9"),
]


def build_order_handoff(buyer_updates: list[BuyerUpdate]) -> OrderHandoff:
    required_slots = [slot for slot, _aspect in REQUIRED_SLOTS]
    ordered = sorted(buyer_updates, key=lambda item: required_slots.index(item.slot))
    if [item.slot for item in ordered] != required_slots:
        raise ValueError("buyer updates do not match required marketplace slots")
    return OrderHandoff(status="ready", required_slots=required_slots, image_count=len(ordered))
