from __future__ import annotations

from fastapi import FastAPI, HTTPException

from infrai_client import InfraiClient, InfraiError
from marketplace_models import MarketplaceRenditionsResponse, SellerAssetRequest
from seller_asset_pipeline import SellerAssetPipeline


app = FastAPI(title="Marketplace Image Renditions Service")
pipeline = SellerAssetPipeline(InfraiClient())


@app.post("/marketplace/assets/renditions", response_model=MarketplaceRenditionsResponse)
def create_marketplace_renditions(request: SellerAssetRequest) -> MarketplaceRenditionsResponse:
    try:
        return pipeline.create_renditions(request)
    except InfraiError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "error": exc.details}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
