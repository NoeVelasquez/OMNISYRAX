# -*- coding: utf-8 -*-
import random
from datetime import datetime
from typing import List, Dict, Any
from src.core.base_generator import BaseGenerator
from src.domain.models import ShipEdgeProduct
from src.utils import data_pool
from src.utils.api_product_fetcher import APIProductFetcher

class ShipEdgeGenerator(BaseGenerator):
    """Generador especializado para productos con formato de importación Shipedge y soporte Multi-SKU."""
    
    def __init__(self, seed: int = None, lang: str = "es", category: str = "all", brand: str = "all", sku_mode: str = "single"):
        super().__init__(seed=seed, lang=lang)
        self.selected_category = category
        self.selected_brand = brand
        self.sku_mode = sku_mode
        
    def _fetch_base_shipedge_data(self) -> Dict[str, Any]:
        live_data = APIProductFetcher.get_live_product(category=self.selected_category, brand=self.selected_brand, lang=self.lang)
        
        if live_data:
            prod_name = live_data["name"]
            brand = live_data.get("brand", "ShipEdgeBrand")
            category = live_data.get("category", "Electronics")
            desc = f"{prod_name} - {brand}"
            cost = round(live_data.get("price", 29.99) * random.uniform(0.4, 0.6), 2)
            weight = round(live_data.get("weight", random.uniform(0.5, 10.0)), 2)
            hs_code = live_data.get("hs_code")
        else:
            if self.selected_category != "all" and self.selected_category in data_pool.HS_CODES:
                category = self.selected_category
            else:
                category = random.choice(list(data_pool.HS_CODES.keys()))
                
            brand = random.choice(data_pool.BRANDS)
            cost = round(random.uniform(5.0, 150.0), 2)
            prod_name = f"Shipedge {category} {brand}"
            desc = f"{prod_name} Edition"
            weight = round(random.uniform(0.5, 20.0), 2)
            hs_code = None
            
        if not hs_code:
            hs_lookup_key = "Home" if "Home" in category else category
            hs_code = random.choice(data_pool.HS_CODES.get(hs_lookup_key, ["0000.00.00"]))
            
        supplier = random.choice(data_pool.SUPPLIERS_DATA)["name"]
        return {
            "name": prod_name,
            "brand": brand,
            "category": category,
            "desc": desc,
            "cost": cost,
            "weight": weight,
            "hs_code": hs_code,
            "supplier": supplier
        }

    def generate_single(self) -> ShipEdgeProduct:
        base = self._fetch_base_shipedge_data()
        clean_brand = data_pool.clean_sku_token(base["brand"], max_len=4, default="SE")
        clean_cat = data_pool.clean_sku_token(base["category"], max_len=3, default="CAT")
        date_str = datetime.now().strftime("%y%m%d")
        random_suffix = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=4))
        sku = f"SE-{clean_cat}-{clean_brand}-{date_str}-{random_suffix}"
        
        return ShipEdgeProduct(
            SKU=sku,
            UPC="".join(str(random.randint(0, 9)) for _ in range(12)),
            Description=base["desc"],
            Cost=base["cost"],
            Declared=round(base["cost"] * random.uniform(1.2, 1.8), 2),
            Weight=base["weight"],
            Length=round(random.uniform(10, 100), 2),
            Width=round(random.uniform(10, 80), 2),
            Height=round(random.uniform(5, 50), 2),
            Quantity=random.randint(0, 1000),
            Supplier=base["supplier"],
            DistributionCenter="DC1",
            SerialNumber=f"SN-{random.getrandbits(32)}",
            Harmonization=base["hs_code"],
            CountryOfOrigin=random.choice(["USA", "CA", "CN", "MX", "VN"])
        )

    def generate_product_with_variants(self, num_variants: int = 3) -> List[ShipEdgeProduct]:
        base = self._fetch_base_shipedge_data()
        variants_info = data_pool.get_category_variants(base["category"], lang=self.lang, count=num_variants)
        clean_brand = data_pool.clean_sku_token(base["brand"], max_len=4, default="SE")
        clean_cat = data_pool.clean_sku_token(base["category"], max_len=3, default="CAT")
        date_str = datetime.now().strftime("%y%m%d")
        
        products = []
        for i, v in enumerate(variants_info):
            var_name = v["name"]
            var_code = data_pool.clean_sku_token(v["code"], max_len=6, default=f"V{i+1}")
            price_mult = v.get("price_factor", 1.0)
            weight_mult = v.get("weight_factor", 1.0)
            
            random_suffix = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=4))
            sku = f"SE-{clean_cat}-{clean_brand}-{var_code}-{date_str}-{random_suffix}"
            desc = f"{base['name']} - {var_name}"
            var_cost = round(base["cost"] * price_mult, 2)
            
            p = ShipEdgeProduct(
                SKU=sku,
                UPC="".join(str(random.randint(0, 9)) for _ in range(12)),
                Description=desc,
                Cost=var_cost,
                Declared=round(var_cost * random.uniform(1.2, 1.8), 2),
                Weight=round(base["weight"] * weight_mult, 2),
                Length=round(random.uniform(10, 100), 2),
                Width=round(random.uniform(10, 80), 2),
                Height=round(random.uniform(5, 50), 2),
                Quantity=random.randint(0, 1000),
                Supplier=base["supplier"],
                DistributionCenter="DC1",
                SerialNumber=f"SN-{random.getrandbits(32)}",
                Harmonization=base["hs_code"],
                CountryOfOrigin=random.choice(["USA", "CA", "CN", "MX", "VN"])
            )
            products.append(p)
        return products

    def generate_batch(self, count: int, sku_mode: str = None) -> List[ShipEdgeProduct]:
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
