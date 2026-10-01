from marketplace_models import SellerAssetRequest
from seller_asset_pipeline import SellerAssetPipeline


class FakeImageAPI:
    def metadata(self, image: str) -> dict:
        return {"source": image, "mime_type": "image/jpeg"}

    def smart_crop(self, image: str, aspect: str, idempotency_key: str | None = None) -> dict:
        return {"url": f"https://cdn.example.test/{aspect.replace(':', '-')}.jpg"}


class FakeInfraiClient:
    def __init__(self) -> None:
        self.image = FakeImageAPI()


def test_pipeline_builds_required_buyer_updates_and_ready_handoff() -> None:
    pipeline = SellerAssetPipeline(FakeInfraiClient())
    request = SellerAssetRequest(
        seller_asset_id="asset-101",
        order_id="ord-9001",
        source_image="https://images.example.com/scan-safe-product.jpg",
        seller_note="primary front pack image",
    )

    response = pipeline.create_renditions(request)

    assert [item.slot for item in response.buyer_updates] == [
        "listing_card",
        "search_result",
        "order_confirmation",
    ]
    assert response.order_handoff.status == "ready"
    assert response.order_handoff.required_slots == [
        "listing_card",
        "search_result",
        "order_confirmation",
    ]
    assert response.order_handoff.image_count == 3
