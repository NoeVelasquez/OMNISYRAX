# -*- coding: utf-8 -*-
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

class Address(BaseModel):
    address1: str
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str
    currency: str

class Customer(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    phone: str

class OrderItem(BaseModel):
    sku: str
    description: str
    quantity: int
    sold_price: float

class Order(BaseModel):
    order_num: str
    order_date: datetime
    customer: Customer
    shipping_address: Address
    billing_address: Address
    items: List[OrderItem]
    ship_method: str
    ship_carrier: str
    total_price: float

class Product(BaseModel):
    product_id: int
    name: str
    description: str
    category: str
    brand: str
    sku: str
    upc: str
    price_buy: float
    price_wholesale: float
    price_retail: float
    weight: float
    length: float
    width: float
    height: float
    hs_code: str
    country_origin: str
    supplier: str
    images: str
    type_product: str

class PurchaseOrder(BaseModel):
    po_number: str
    date: date
    supplier_code: str
    supplier_name: str
    items: List[OrderItem]
    total_cost: float

class Transfer(BaseModel):
    transfer_number: str
    ship_method: str
    ship_carrier: str
    instruction: str
    comments: str
    date: date
    total_price: float
    from_email: str
    from_phone: str
    from_first_name: str
    from_last_name: str
    from_address1: str
    from_city: str
    from_state: str
    from_country: str
    from_zip: str
    to_email: str
    to_phone: str
    to_first_name: str
    to_last_name: str
    to_address1: str
    to_city: str
    to_state: str
    to_country: str
    to_zip: str
    items: List[OrderItem]

class Package(BaseModel):
    name: str
    description: str
    type_pack: str
    price: float
    cost: float
    length: float
    width: float
    height: float
    inner_length: float
    inner_height: float
    inner_width: float
    box_weight: float
    max_weight: float
    volume_capacity: float
    stackeable: bool

class ShipEdgeProduct(BaseModel):
    SKU: str
    UPC: str
    Description: str
    Cost: float
    Declared: float
    Weight: float
    Length: float
    Width: float
    Height: float
    Quantity: int
    Supplier: str
    DistributionCenter: str
    SerialNumber: str
    Harmonization: str
    CountryOfOrigin: str

class InventoryItem(BaseModel):
    sku: str
    quantity: int
    images: str
    name: str
    description: str
    barcode: str
    price_buy: float
    price_retail: float
    price_wholesale: float
    brand: str
    upc: str

class ShopifyProduct(BaseModel):
    handle: str
    title: str
    body_html: str
    vendor: str
    type: str
    tags: str
    published: bool = True
    option1_name: str = "Title"
    option1_value: str = "Default Title"
    variant_sku: str
    variant_grams: int
    variant_inventory_tracker: str = "shopify"
    variant_inventory_qty: int
    variant_price: float
    image_src: Optional[str] = None
