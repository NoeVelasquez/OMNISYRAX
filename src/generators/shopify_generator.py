# -*- coding: utf-8 -*-
import random
from datetime import datetime
from src.core.base_generator import BaseGenerator
from src.domain.models import ShopifyProduct
from src.utils import data_pool
from src.utils.api_product_fetcher import APIProductFetcher

class ShopifyGenerator(BaseGenerator):
    """Generador especializado en el formato de importación de Shopify."""
    
    def __init__(self, seed: int = None, lang: str = "es", category: str = "all"):
        super().__init__(seed=seed, lang=lang)
        self.selected_category = category
        
    def generate_single(self) -> ShopifyProduct:
        # Intentar obtener producto real en vivo desde API
        live_data = APIProductFetcher.get_live_product(category=self.selected_category)
        
        if live_data:
            full_title = live_data["name"]
            brand = live_data.get("brand", "ShopifyBrand")
            category = live_data.get("category", "Electronics")
            body_html = f"<p>{live_data.get('description', full_title)}</p>"
            variant_price = live_data.get("price", round(random.uniform(19.99, 499.99), 2))
            image_src = live_data.get("image") or "https://picsum.photos/seed/shp/800/800.jpg"
            grams = int(live_data.get("weight", random.uniform(0.1, 5.0)) * 1000)
        else:
            if self.lang == "all":
                lang = random.choice(list(data_pool.MULTILANG_DATA.keys()))
            else:
                lang = self.lang if self.lang in data_pool.MULTILANG_DATA else "es"
                
            lang_data = data_pool.MULTILANG_DATA[lang]
            lang_categories = list(lang_data["categories"].keys())
            
            if self.selected_category != "all" and self.selected_category in lang_categories:
                category = self.selected_category
            else:
                category = random.choice(lang_categories)
                
            product_name = random.choice(lang_data["categories"][category])
            brand = random.choice(lang_data.get("brands", ["ShopifyBrand"]))
            adj = random.choice(lang_data.get("adjectives", ["Premium"]))
            full_title = f"{adj} {product_name} - {brand}"
            body_html = f"<p>{lang_data.get('descriptions', ['Producto de alta calidad.'])[0]}</p>"
            variant_price = round(random.uniform(19.99, 499.99), 2)
            image_src = f"https://picsum.photos/seed/{random.randint(1000, 9999)}/800/800.jpg"
            grams = random.randint(100, 5000)
            
        handle = full_title.lower().replace(" ", "-").replace("&", "and")
        clean_brand = "".join(c for c in brand if c.isalnum()).upper()[:4] or "SHP"
        date_str = datetime.now().strftime("%y%m%d")
        random_suffix = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=4))
        sku = f"SHP-{category[:3].upper()}-{clean_brand}-{date_str}-{random_suffix}"
        
        return ShopifyProduct(
            handle=handle,
            title=full_title,
            body_html=body_html,
            vendor=brand,
            type=category,
            tags=f"{category.lower()}, {brand.lower()}, premium",
            variant_sku=sku,
            variant_grams=grams,
            variant_inventory_qty=random.randint(10, 100),
            variant_price=variant_price,
            image_src=image_src
        )
