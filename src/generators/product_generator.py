# -*- coding: utf-8 -*-
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.core.base_generator import BaseGenerator
from src.domain.models import Product
from src.utils import data_pool
from src.utils.api_product_fetcher import APIProductFetcher

class ProductGenerator(BaseGenerator):
    """Generador dinámico de productos que consume APIs públicas reales con fallback local y soporte Multi-SKU."""
    
    def __init__(self, seed: int = None, lang: str = "es", category: str = "all", brand: str = "all", sku_mode: str = "single"):
        super().__init__(seed=seed, lang=lang)
        self.selected_category = category
        self.selected_brand = brand
        self.sku_mode = sku_mode
        
    def _fetch_base_product_data(self) -> Dict[str, Any]:
        """Obtiene datos base de un producto (desde API en vivo o desde el catálogo local)."""
        live_data = APIProductFetcher.get_live_product(category=self.selected_category, brand=self.selected_brand, lang=self.lang)
        
        if live_data:
            product_name = live_data["name"]
            brand = live_data.get("brand") or (self.selected_brand if self.selected_brand != "all" else "Generic")
            category = live_data.get("category", "Electronics")
            description = live_data.get("description", f"{product_name} - {brand}")
            price_retail = live_data.get("price", round(random.uniform(20, 300), 2))
            price_buy = live_data.get("price_buy") or round(price_retail * random.uniform(0.3, 0.5), 2)
            price_wholesale = live_data.get("price_wholesale") or round(price_retail * random.uniform(0.6, 0.8), 2)
            image_url = APIProductFetcher._clean_image_url(live_data.get("image")) or data_pool.get_real_category_image(category)
            weight = live_data.get("weight", round(random.uniform(0.1, 10.0), 2))
            length = live_data.get("length", round(random.uniform(1.0, 50.0), 2))
            width = live_data.get("width", round(random.uniform(1.0, 30.0), 2))
            height = live_data.get("height", round(random.uniform(1.0, 20.0), 2))
            hs_code = live_data.get("hs_code")
        else:
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
            brand = self.selected_brand if self.selected_brand != "all" else random.choice(lang_data.get("brands", ["TechCorp"]))
            adj = random.choice(lang_data.get("adjectives", ["Premium"]))
            product_name = f"{adj} {base_name}"
            description = f"{product_name} de {brand}."
            price_retail = round(random.uniform(50, 400), 2)
            price_buy = round(price_retail * random.uniform(0.3, 0.5), 2)
            price_wholesale = round(price_retail * random.uniform(0.6, 0.8), 2)
            image_url = data_pool.get_real_category_image(category)
            weight = round(random.uniform(0.5, 5.0), 2)
            length = round(random.uniform(1.0, 50.0), 2)
            width = round(random.uniform(1.0, 30.0), 2)
            height = round(random.uniform(1.0, 20.0), 2)
            hs_code = None
            
        supplier_data = random.choice(data_pool.SUPPLIERS_DATA)
        if not hs_code:
            hs_lookup_key = "Home" if "Home" in category else category
            hs_code = random.choice(data_pool.HS_CODES.get(hs_lookup_key, ["0000.00.00"]))
            
        return {
            "name": product_name,
            "brand": brand,
            "category": category,
            "description": description,
            "price_retail": price_retail,
            "price_buy": price_buy,
            "price_wholesale": price_wholesale,
            "image_url": image_url,
            "weight": weight,
            "length": length,
            "width": width,
            "height": height,
            "hs_code": hs_code,
            "supplier": supplier_data["name"]
        }
        
    def generate_single(self) -> Product:
        """Genera un producto con 1 solo SKU principal."""
        base = self._fetch_base_product_data()
        clean_brand = data_pool.clean_sku_token(base["brand"], max_len=4, default="GEN")
        clean_cat = data_pool.clean_sku_token(base["category"], max_len=3, default="CAT")
        date_str = datetime.now().strftime("%y%m%d")
        random_suffix = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=6))
        sku = f"SKU-{clean_cat}-{clean_brand}-{date_str}-{random_suffix}"
        
        return Product(
            product_id=random.randint(1000, 9999),
            name=base["name"],
            parent_product=base["name"],
            variant_name="Standard",
            description=base["description"],
            category=base["category"],
            brand=base["brand"],
            sku=sku,
            upc="".join(str(random.randint(0, 9)) for _ in range(12)),
            price_buy=base["price_buy"],
            price_wholesale=base["price_wholesale"],
            price_retail=base["price_retail"],
            weight=base["weight"],
            length=base["length"],
            width=base["width"],
            height=base["height"],
            hs_code=base["hs_code"],
            country_origin=random.choice(list(data_pool.CITIES.keys())),
            supplier=base["supplier"],
            images=base["image_url"],
            type_product="PURCHASED"
        )

    def generate_product_with_variants(self, num_variants: int = 3) -> List[Product]:
        """
        Genera un producto padre con múltiples variantes/SKUs (Multi-SKU).
        Todos los SKUs comparten el mismo parent_product y product_id, pero difieren en
        variant_name, SKU, precio y peso según la variante.
        """
        base = self._fetch_base_product_data()
        variants_info = data_pool.get_category_variants(base["category"], lang=self.lang, count=num_variants)
        shared_product_id = random.randint(1000, 9999)
        country_origin = random.choice(list(data_pool.CITIES.keys()))
        clean_brand = data_pool.clean_sku_token(base["brand"], max_len=4, default="GEN")
        clean_cat = data_pool.clean_sku_token(base["category"], max_len=3, default="CAT")
        date_str = datetime.now().strftime("%y%m%d")
        
        products = []
        for i, v in enumerate(variants_info):
            var_name = v["name"]
            var_code = data_pool.clean_sku_token(v["code"], max_len=7, default=f"V{i+1}")
            price_mult = v.get("price_factor", 1.0)
            weight_mult = v.get("weight_factor", 1.0)
            
            random_suffix = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=4))
            sku = f"SKU-{clean_cat}-{clean_brand}-{var_code}-{date_str}-{random_suffix}"
            variant_full_name = f"{base['name']} - {var_name}"
            
            prod = Product(
                product_id=shared_product_id,
                name=variant_full_name,
                parent_product=base["name"],
                variant_name=var_name,
                description=base["description"],
                category=base["category"],
                brand=base["brand"],
                sku=sku,
                upc="".join(str(random.randint(0, 9)) for _ in range(12)),
                price_buy=round(base["price_buy"] * price_mult, 2),
                price_wholesale=round(base["price_wholesale"] * price_mult, 2),
                price_retail=round(base["price_retail"] * price_mult, 2),
                weight=round(base["weight"] * weight_mult, 2),
                length=base["length"],
                width=base["width"],
                height=base["height"],
                hs_code=base["hs_code"],
                country_origin=country_origin,
                supplier=base["supplier"],
                images=base["image_url"],
                type_product="PURCHASED"
            )
            products.append(prod)
        return products

    def generate_batch(self, count: int, sku_mode: str = None) -> List[Product]:
        """
        Genera un lote de productos según el modo de SKU:
        - 'single': 1 producto = 1 SKU
        - 'multi': 1 producto = 2 a 5 variantes/SKUs
        - 'mixed': mezcla aleatoria de single y multi-SKU
        """
        mode = sku_mode or self.sku_mode
        if mode == "single":
            return [self.generate_single() for _ in range(count)]
            
        results = []
        for _ in range(count):
            if mode == "multi":
                num_vars = random.randint(2, 5)
                results.extend(self.generate_product_with_variants(num_vars))
            elif mode == "mixed":
                if random.random() < 0.35:
                    results.append(self.generate_single())
                else:
                    num_vars = random.randint(2, 4)
                    results.extend(self.generate_product_with_variants(num_vars))
            else:
                results.append(self.generate_single())
        return results
