# -*- coding: utf-8 -*-
import csv
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Any, Dict
from pydantic import BaseModel

class CSVExporter:
    """Maneja la exportación de modelos Pydantic a archivos CSV."""
    
    @staticmethod
    def export(data: List[BaseModel], filename: str, output_dir: Path) -> Path:
        if not data:
            raise ValueError("No hay datos para exportar.")
            
        output_path = output_dir / filename
        
        # Aplanar los modelos para CSV
        flat_data = []
        for item in data:
            if hasattr(item, 'items'): # Caso para órdenes, POs y transferencias
                # Determinar prefijos según el tipo
                if hasattr(item, 'customer'): # Órdenes
                    for line_item in item.items:
                        ship = item.shipping_address.model_dump()
                        bill = item.billing_address.model_dump()
                        row = {
                            "order_num": item.order_num,
                            "ship_method": item.ship_method,
                            "ship_carrier": item.ship_carrier,
                            "order_date": item.order_date.strftime("%Y-%m-%d"),
                            "total_price": item.total_price,
                            "customer_firstname": item.customer.firstname,
                            "customer_address1": ship["address1"],
                            "customer_city": ship["city"],
                            "customer_country": ship["country"],
                            "customer_bill_firstname": item.customer.firstname,
                            "customer_bill_address1": bill["address1"],
                            "customer_bill_city": bill["city"],
                            "customer_bill_country": bill["country"],
                            "currency": ship["currency"],
                            "sku": line_item.sku,
                            "sold_price": line_item.sold_price,
                            "on_hand": line_item.quantity,
                            "committed": random.randint(0, 2),
                            "available": max(0, line_item.quantity - 1)
                        }
                        flat_data.append(row)
                elif hasattr(item, 'supplier_code'): # POs
                    for line_item in item.items:
                        row = {
                            "po_num": item.po_number,
                            "ship_method": "standard",
                            "ship_carrier": "FedEx",
                            "instructions": "Handle with care",
                            "comments": "Regular shipment",
                            "date_po": item.date.strftime("%Y-%m-%d"),
                            "date_arrival": (item.date + timedelta(days=7)).strftime("%Y-%m-%d"),
                            "total_price": item.total_cost,
                            "supply/code": item.supplier_code,
                            "supply/name": item.supplier_name,
                            "suppliy/first_name": "Contact",
                            "suppliy/last_name": "Person",
                            "suppliy/phone": "123456789",
                            "suppliy/email": "supplier@example.com",
                            "suppliy/address": "123 Supplier St",
                            "suppliy/country": "USA",
                            "suppliy/state": "FL",
                            "suppliy/city": "Miami",
                            "sku": line_item.sku,
                            "name": line_item.description,
                            "barcode": "".join(str(random.randint(0, 9)) for _ in range(12)),
                            "sold_price": line_item.sold_price,
                            "description": line_item.description,
                            "quantity": line_item.quantity
                        }
                        flat_data.append(row)
                elif hasattr(item, 'transfer_number'): # Transferencias
                    for line_item in item.items:
                        row = {
                            "transfer_number": item.transfer_number,
                            "ship_method": item.ship_method,
                            "ship_carrier": item.ship_carrier,
                            "instruction": item.instruction,
                            "comments": item.comments,
                            "date": item.date.strftime("%Y-%m-%d"),
                            "total_price": item.total_price,
                            "from_email": item.from_email,
                            "from_phone": item.from_phone,
                            "from_first_name": item.from_first_name,
                            "from_last_name": item.from_last_name,
                            "from_address1": item.from_address1,
                            "from_city": item.from_city,
                            "from_state": item.from_state,
                            "from_country": item.from_country,
                            "from_zip": item.from_zip,
                            "to_email": item.to_email,
                            "to_phone": item.to_phone,
                            "to_first_name": item.to_first_name,
                            "to_last_name": item.to_last_name,
                            "to_address1": item.to_address1,
                            "to_city": item.to_city,
                            "to_state": item.to_state,
                            "to_country": item.to_country,
                            "to_zip": item.to_zip,
                            "sku": line_item.sku,
                            "quantity": line_item.quantity
                        }
                        flat_data.append(row)
            elif hasattr(item, 'supplier'): # Productos
                row = {
                    "product": item.name.split(" - ")[0], # Nombre base
                    "description": item.description,
                    "images": item.images,
                    "type_product": item.type_product,
                    "category": item.category,
                    "brand": item.brand,
                    "name": item.name, # Variant name
                    "sku": item.sku,
                    "supplier": item.supplier,
                    "upc": item.upc,
                    "hs_code": item.hs_code,
                    "country_origin": item.country_origin,
                    "length": item.length,
                    "width": item.width,
                    "height": item.height,
                    "weight": item.weight,
                    "price_buy": item.price_buy,
                    "price_wholesale": item.price_wholesale,
                    "price_retail": item.price_retail
                }
                flat_data.append(row)
            elif hasattr(item, 'type_pack'): # Paquetes
                row = {
                    "name": item.name,
                    "description": item.description,
                    "type_pack": item.type_pack,
                    "price": item.price,
                    "cost": item.cost,
                    "length": item.length,
                    "width": item.width,
                    "height": item.height,
                    "inner_length": item.inner_length,
                    "inner_height": item.inner_height,
                    "inner_width": item.inner_width,
                    "box_weight": item.box_weight,
                    "max_weight": item.max_weight,
                    "volume_capacity": item.volume_capacity,
                    "stackeable": "true" if item.stackeable else "false"
                }
                flat_data.append(row)
            elif hasattr(item, 'variant_sku') and hasattr(item, 'handle'): # Shopify
                row = {
                    "Handle": item.handle,
                    "Title": item.title,
                    "Body (HTML)": item.body_html,
                    "Vendor": item.vendor,
                    "Type": item.type,
                    "Tags": item.tags,
                    "Published": "TRUE" if item.published else "FALSE",
                    "Option1 Name": item.option1_name,
                    "Option1 Value": item.option1_value,
                    "Variant SKU": item.variant_sku,
                    "Variant Grams": item.variant_grams,
                    "Variant Inventory Tracker": "shopify",
                    "Variant Inventory Qty": item.variant_inventory_qty,
                    "Variant Inventory Policy": "deny",
                    "Variant Fulfillment Service": "manual",
                    "Variant Price": item.variant_price,
                    "Variant Requires Shipping": "TRUE",
                    "Variant Taxable": "TRUE",
                    "Image Src": item.image_src
                }
                flat_data.append(row)
            elif hasattr(item, 'sku') and hasattr(item, 'barcode'): # Inventario
                row = {
                    "sku": item.sku,
                    "quantity": item.quantity,
                    "images": item.images,
                    "name": item.name,
                    "description": item.description,
                    "barcode": item.barcode,
                    "price_buy": item.price_buy,
                    "price_retail": item.price_retail,
                    "price_wholesale": item.price_wholesale,
                    "brand": item.brand,
                    "upc": item.upc
                }
                flat_data.append(row)
            else:
                flat_data.append(item.model_dump())
        
        if not flat_data:
            return output_path

        fieldnames = flat_data[0].keys()
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\r\n')
            writer.writeheader()
            writer.writerows(flat_data)
            
        return output_path
