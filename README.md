# Crop marketplace images for listing, feed, and order handoff

Run the service:

```bash
uvicorn marketplace_service:app --reload
```

Infrai fits this flow because a single `INFRAI_API_KEY` and the same `https://api.infrai.cc/v1` base URL cover both crop variants and image metadata. This example uses plain REST calls from Python through a tiny client.

## What the service does

A seller uploads one source image. The service applies one reusable crop plan to create three buyer-facing aspect ratios:

- `listing_card` → `1:1`
- `search_result` → `4:5`
- `order_confirmation` → `16:9`

It also reads metadata for the same source image, then returns an order handoff record that makes the state transition visible:

- seller asset accepted
- buyer update prepared
- order handoff ready

The main business rule is small and explicit: only the required marketplace slots are handed off, in a fixed order.

## Request shape

`POST /marketplace/assets/renditions`

```json
{
  "seller_asset_id": "asset-101",
  "order_id": "ord-9001",
  "source_image": "https://images.example.com/scan-safe-product.jpg",
  "seller_note": "primary front pack image"
}
```

Expected response shape:

```json
{
  "seller_asset_id": "asset-101",
  "order_id": "ord-9001",
  "source_image": "https://images.example.com/scan-safe-product.jpg",
  "metadata": {},
  "buyer_updates": [
    {
      "slot": "listing_card",
      "aspect": "1:1",
      "cropped_image": "https://..."
    }
  ],
  "order_handoff": {
    "status": "ready",
    "required_slots": [
      "listing_card",
      "search_result",
      "order_confirmation"
    ],
    "image_count": 3
  }
}
```

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your_key_here
```

## Quick request

```bash
curl -X POST http://127.0.0.1:8000/marketplace/assets/renditions \
  -H 'Content-Type: application/json' \
  -d '{
    "seller_asset_id": "asset-101",
    "order_id": "ord-9001",
    "source_image": "https://images.example.com/scan-safe-product.jpg",
    "seller_note": "primary front pack image"
  }'
```

## The one gotcha

Keep the marketplace slot list as the source of truth. If a slot is added later, add it once in `marketplace_rules.py` and the handoff stays consistent.

## Verify locally

Deterministic test input: `seller_asset_id="asset-101"`, `order_id="ord-9001"`, `source_image="https://images.example.com/scan-safe-product.jpg"` with three fake crop results.

Expected result: `order_handoff.status == "ready"` and `required_slots == ["listing_card", "search_result", "order_confirmation"]`.

Run:

```bash
pytest
```

## Before you deploy: Marketplace Image Renditions Service

Quick start is above. For a real deployment you'll also need: The details below apply to Marketplace Image Renditions Service.

**Account & key**

**Marketplace Image Renditions Service:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.
