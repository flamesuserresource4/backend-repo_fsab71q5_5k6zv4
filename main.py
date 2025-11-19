import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order

app = FastAPI(title="Jersey Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helpers
class ObjectIdStr(str):
    @classmethod
    def validate(cls, v):
        try:
            ObjectId(v)
            return v
        except Exception:
            raise ValueError("Invalid ObjectId")


# Public endpoints
@app.get("/")
def read_root():
    return {"message": "Jersey Store API is running"}


@app.get("/api/products", response_model=List[dict])
def list_products(q: Optional[str] = None, limit: int = 50):
    filter_dict = {"is_active": True}
    if q:
        # Basic text search on title/tags
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}},
            {"team": {"$regex": q, "$options": "i"}},
            {"league": {"$regex": q, "$options": "i"}},
        ]
    try:
        items = get_documents("product", filter_dict, limit)
        # Convert ObjectId to string
        for it in items:
            it["_id"] = str(it.get("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CreateProductRequest(Product):
    pass


@app.post("/api/products")
def create_product(payload: CreateProductRequest):
    try:
        new_id = create_document("product", payload)
        return {"_id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CreateOrderRequest(Order):
    pass


@app.post("/api/orders")
def create_order(payload: CreateOrderRequest):
    try:
        new_id = create_document("order", payload)
        return {"_id": new_id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    """Test endpoint to verify database connectivity and list first collections"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
