# -*- coding: utf-8 -*-
import random
from datetime import datetime
from typing import List, Dict, Any
from src.core.base_generator import BaseGenerator
from src.domain.models import ShopifyProduct
from src.utils import data_pool
from src.utils.api_product_fetcher import APIProductFetcher

class ShopifyGenerator(BaseGenerator):
    """Generador especializado en el formato de importación de Shopify con soporte Multi-SKU."""
    
    def __init__(self, seed: int = None, lang: str = "es", category: str = "all", brand: str = "all", sku_mode: str = "single"):
        super().__init__(seed=seed, lang=lang)
        self.selected_category = category
        self.selected_brand = brand
        self.sku_mode = sku_mode
        
    def _fetch_base_shopify_data(self) -> Dict[str, Any]:
        live_data = APIProductFetcher.get_live_product(category=self.selected_category, brand=self.selected_brand, lang=self.lang)
        
        if live_data:
            full_title = live_data["name"]
            brand = live_data.get("brand", "ShopifyBrand")
            category = live_data.get("category", "Electronics")
            body_html = f"<p>{live_data.get('description', full_title)}</p>"
            price = live_data.get("price", round(random.uniform(19.99, 499.99), 2))
            image_src = APIProductFetcher._clean_image_url(live_data.get("image")) or data_pool.get_real_category_image(category)
            weight = live_data.get("weight", round(random.uniform(0.1, 5.0), 2))
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
            brand = self.selected_brand if self.selected_brand != "all" else random.choice(lang_data.get("brands", ["ShopifyBrand"]))
            adj = random.choice(lang_data.get("adjectives", ["Premium"]))
            full_title = f"{adj} {product_name} - {brand}"
            body_html = f"<p>{lang_data.get('descriptions', ['Producto de alta calidad.'])[0]}</p>"
            price = round(random.uniform(19.99, 499.99), 2)
            image_src = data_pool.get_real_category_image(category)
            weight = round(random.uniform(0.2, 5.0), 2)
            
        handle = data_pool.clean_sku_token(full_title, max_len=30, default="prod").lower().replace(" ", "-")
        return {
            "title": full_title,
            "handle": handle,
            "brand": brand,
            "category": category,
            "body_html": body_html,
            "price": price,
            "weight": weight,
            "image_src": image_src
        }

    def generate_single(self) -> ShopifyProduct:
        base = self._fetch_base_shopify_data()
        clean_brand = data_pool.clean_sku_token(base["brand"], max_len=4, default="SHP")
        clean_cat = data_pool.clean_sku_token(base["category"], max_len=3, default="CAT")
        date_str = datetime.now().strftime("%y%m%d")
        random_suffix = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=4))
        sku = f"SHP-{clean_cat}-{clean_brand}-{date_str}-{random_suffix}"
        
        return ShopifyProduct(
            handle=base["handle"],
            title=base["title"],
            body_html=base["body_html"],
            vendor=base["brand"],
            type=base["category"],
            tags=f"{base['category'].lower()}, {base['brand'].lower()}, premium",
            option1_name="Title",
            option1_value="Default Title",
            variant_sku=sku,
            variant_grams=int(base["weight"] * 1000),
            variant_inventory_qty=random.randint(10, 100),
            variant_price=base["price"],
            image_src=base["image_src"]
        )

    def generate_product_with_variants(self, num_variants: int = 3) -> List[ShopifyProduct]:
        base = self._fetch_base_shopify_data()
        variants_info = data_pool.get_category_variants(base["category"], lang=self.lang, count=num_variants)
        clean_brand = data_pool.clean_sku_token(base["brand"], max_len=4, default="SHP")
        clean_cat = data_pool.clean_sku_token(base["category"], max_len=3, default="CAT")
        date_str = datetime.now().strftime("%y%m%d")
        
        opt_name = "Variante" if self.lang == "es" else "Variant"
        products = []
        for i, v in enumerate(variants_info):
            var_name = v["name"]
            var_code = data_pool.clean_sku_token(v["code"], max_len=6, default=f"V{i+1}")
            price_mult = v.get("price_factor", 1.0)
            weight_mult = v.get("weight_factor", 1.0)
            
            random_suffix = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=4))
            sku = f"SHP-{clean_cat}-{clean_brand}-{var_code}-{date_str}-{random_suffix}"
            
            p = ShopifyProduct(
                handle=base["handle"],
                title=base["title"],
                body_html=base["body_html"],
                vendor=base["brand"],
                type=base["category"],
                tags=f"{base['category'].lower()}, {base['brand'].lower()}, premium",
                option1_name=opt_name,
                option1_value=var_name,
                variant_sku=sku,
                variant_grams=int(base["weight"] * weight_mult * 1000),
                variant_inventory_qty=random.randint(10, 100),
                variant_price=round(base["price"] * price_mult, 2),
                image_src=base["image_src"]
            )
            products.append(p)
        return products

    def generate_batch(self, count: int, sku_mode: str = None) -> List[ShopifyProduct]:
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
