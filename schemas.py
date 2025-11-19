"""
Database Schemas for Jersey E-commerce (Bangladesh)

Each Pydantic model represents a MongoDB collection. Collection name is the
lowercase of the class name (e.g., Product -> "product").

These schemas are used for validation in both the backend endpoints and the
Flames database viewer.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Literal

# Core domain models

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product"
    """
    title: str = Field(..., description="Product name (e.g., Argentina 23/24 Home Jersey)")
    description: Optional[str] = Field(None, description="Product description")
    team: Optional[str] = Field(None, description="Team/Club/National team name")
    league: Optional[str] = Field(None, description="League or Competition (e.g., EPL, UCL)")
    sku: Optional[str] = Field(None, description="Unique stock keeping unit")
    price_bdt: int = Field(..., ge=0, description="Price in BDT")
    sizes: List[str] = Field(default_factory=lambda: ["S","M","L","XL"], description="Available sizes")
    stock_by_size: Dict[str, int] = Field(default_factory=dict, description="Stock count per size")
    image_url: Optional[str] = Field(None, description="Primary image URL")
    gallery: List[str] = Field(default_factory=list, description="Additional image URLs")
    category: Optional[str] = Field(None, description="Product category (e.g., Club, National, Retro)")
    tags: List[str] = Field(default_factory=list, description="Search/Filter tags")
    is_active: bool = Field(True, description="Whether product is active/visible")
    is_authentic: Optional[bool] = Field(None, description="Authentic or fan version")
    discount_bdt: int = Field(0, ge=0, description="Flat discount in BDT, if any")


class Customer(BaseModel):
    """Customers collection schema (optional future use)."""
    name: str
    phone: str = Field(..., min_length=6, max_length=20)
    email: Optional[EmailStr] = None
    address: str
    district: Optional[str] = None


class OrderItem(BaseModel):
    product_id: str = Field(..., description="ObjectId string of product")
    title: str
    size: str
    price_bdt: int
    quantity: int = Field(..., ge=1)
    image_url: Optional[str] = None


class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    items: List[OrderItem]
    customer_name: str
    customer_phone: str
    customer_email: Optional[EmailStr] = None
    shipping_address: str
    district: Optional[str] = None
    payment_method: Literal["COD", "bKash", "Nagad"] = "COD"
    subtotal_bdt: int = Field(..., ge=0)
    delivery_fee_bdt: int = Field(..., ge=0)
    total_bdt: int = Field(..., ge=0)
    status: Literal["pending", "confirmed", "shipped", "delivered", "cancelled"] = "pending"


# Legacy example schema kept for reference (not used for storefront)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True
