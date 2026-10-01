from __future__ import annotations

from marketplace_models import BuyerUpdate, MarketplaceRenditionsResponse, SellerAssetRequest
from marketplace_rules import REQUIRED_SLOTS, build_order_handoff
from infrai_client import InfraiClient


class SellerAssetPipeline:
    def __init__(self, infrai_client: InfraiClient) -> None:
        self.infrai = infrai_client

    def create_renditions(self, request: SellerAssetRequest) -> MarketplaceRenditionsResponse:
        metadata = self.infrai.image.metadata(image=request.source_image)
        buyer_updates: list[BuyerUpdate] = []

        for slot, aspect in REQUIRED_SLOTS:
            crop_result = self.infrai.image.smart_crop(
                image=request.source_image,
                aspect=aspect,
                idempotency_key=f"{request.seller_asset_id}:{slot}:{request.order_id}",
            )
            cropped_image = self._extract_cropped_image(crop_result)
            buyer_updates.append(BuyerUpdate(slot=slot, aspect=aspect, cropped_image=cropped_image))

        handoff = build_order_handoff(buyer_updates)
        return MarketplaceRenditionsResponse(
            seller_asset_id=request.seller_asset_id,
            order_id=request.order_id,
            source_image=request.source_image,
            metadata=metadata,
            buyer_updates=buyer_updates,
            order_handoff=handoff,
        )

    @staticmethod
    def _extract_cropped_image(crop_result: dict) -> str:
        for key in ("url", "image", "output", "result"):
            value = crop_result.get(key)
            if isinstance(value, str) and value:
                return value
        for value in crop_result.values():
            if isinstance(value, str) and value:
                return value
        raise ValueError("crop result did not include an image reference")
