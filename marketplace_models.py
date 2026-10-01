from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field


SlotName = Literal["listing_card", "search_result", "order_confirmation"]


class SellerAssetRequest(BaseModel):
    seller_asset_id: str = Field(min_length=1)
    order_id: str = Field(min_length=1)
    source_image: str = Field(min_length=1)
    seller_note: str = Field(default="")


class BuyerUpdate(BaseModel):
    slot: SlotName
    aspect: str
    cropped_image: str


class OrderHandoff(BaseModel):
    status: Literal["ready"]
    required_slots: List[SlotName]
    image_count: int


class MarketplaceRenditionsResponse(BaseModel):
    seller_asset_id: str
    order_id: str
    source_image: str
    metadata: Dict[str, Any]
    buyer_updates: List[BuyerUpdate]
    order_handoff: OrderHandoff
