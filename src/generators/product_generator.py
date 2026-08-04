# -*- coding: utf-8 -*-
import random
from datetime import datetime
from src.core.base_generator import BaseGenerator
from src.domain.models import Product
from src.utils import data_pool
from src.utils.api_product_fetcher import APIProductFetcher

class ProductGenerator(BaseGenerator):
    """Generador dinámico de productos que consume APIs públicas reales (DummyJSON / FakeStoreAPI) con fallback local."""
    
    def __init__(self, seed: int = None, lang: str = "es", category: str = "all"):
        super().__init__(seed=seed, lang=lang)
        self.selected_category = category
        
    def generate_single(self) -> Product:
        # Intentar obtener un producto real en vivo desde APIs externas
        live_data = APIProductFetcher.get_live_product(category=self.selected_category)
        
        if live_data:
            product_name = live_data["name"]
            brand = live_data.get("brand", "Generic")
            category = live_data.get("category", "Electronics")
            description = live_data.get("description", f"{product_name} - {brand}")
            price_retail = live_data.get("price", round(random.uniform(20, 300), 2))
            image_url = live_data.get("image") or f"https://picsum.photos/seed/{random.randint(1000, 9999)}/600/600"
            weight = live_data.get("weight", round(random.uniform(0.1, 10.0), 2))
        else:
            # Fallback ligero si no hay conexión a las APIs
            if self.lang == "all":
                lang = random.choice(list(data_pool.MULTILANG_DATA.keys()))
            else:
                lang = self.lang if self.lang in data_pool.MULTILANG_DATA else "es"
                
            lang_categories = list(data_pool.MULTILANG_DATA[lang]["categories"].keys())
            if self.selected_category != "all" and self.selected_category in lang_categories:
                category = self.selected_category
            else:
                category = random.choice(lang_categories)
                
            lang_data = data_pool.MULTILANG_DATA[lang]
            base_name = random.choice(lang_data["categories"][category])
            brand = random.choice(lang_data.get("brands", ["TechCorp"]))
            adj = random.choice(lang_data.get("adjectives", ["Premium"]))
            product_name = f"{adj} {base_name}"
            description = f"{product_name} de {brand}."
            price_retail = round(random.uniform(50, 400), 2)
            image_url = f"https://picsum.photos/seed/{random.randint(1000, 9999)}/600/600"
            weight = round(random.uniform(0.5, 5.0), 2)
            
        # Generación de SKU extenso, profesional y 100% único
        clean_brand = "".join(c for c in brand if c.isalnum()).upper()[:4] or "GEN"
        date_str = datetime.now().strftime("%y%m%d")
        random_suffix = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=4))
        sku = f"SKU-{category[:3].upper()}-{clean_brand}-{date_str}-{random_suffix}"
        
        # Precios y dimensiones calculadas
        price_buy = round(price_retail * random.uniform(0.3, 0.5), 2)
        price_wholesale = round(price_retail * random.uniform(0.6, 0.8), 2)
        
        length = round(random.uniform(1.0, 50.0), 2)
        width = round(random.uniform(1.0, 30.0), 2)
        height = round(random.uniform(1.0, 20.0), 2)
        
        supplier_data = random.choice(data_pool.SUPPLIERS_DATA)
        hs_lookup_key = "Home" if "Home" in category else category
        hs_code = random.choice(data_pool.HS_CODES.get(hs_lookup_key, ["0000.00.00"]))
        
        return Product(
            product_id=random.randint(1000, 9999),
            name=product_name,
            description=description,
            category=category,
            brand=brand,
            sku=sku,
            upc="".join(str(random.randint(0, 9)) for _ in range(12)),
            price_buy=price_buy,
            price_wholesale=price_wholesale,
            price_retail=price_retail,
            weight=weight,
            length=length,
            width=width,
            height=height,
            hs_code=hs_code,
            country_origin=random.choice(list(data_pool.CITIES.keys())),
            supplier=supplier_data["name"],
            images=image_url,
            type_product="PURCHASED"
        )
