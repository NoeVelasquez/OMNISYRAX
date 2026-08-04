# -*- coding: utf-8 -*-
import random
from datetime import datetime
from src.core.base_generator import BaseGenerator
from src.domain.models import ShipEdgeProduct
from src.utils import data_pool
from src.utils.api_product_fetcher import APIProductFetcher

class ShipEdgeGenerator(BaseGenerator):
    """Generador especializado para productos con formato de importación Shipedge."""
    
    def __init__(self, seed: int = None, lang: str = "es", category: str = "all"):
        super().__init__(seed=seed, lang=lang)
        self.selected_category = category
        
    def generate_single(self) -> ShipEdgeProduct:
        # Intentar obtener producto real en vivo desde API
        live_data = APIProductFetcher.get_live_product(category=self.selected_category)
        
        if live_data:
            prod_name = live_data["name"]
            brand = live_data.get("brand", "ShipEdgeBrand")
            category = live_data.get("category", "Electronics")
            desc = f"{prod_name} - {brand}"
            cost = round(live_data.get("price", 29.99) * random.uniform(0.4, 0.6), 2)
            weight = round(live_data.get("weight", random.uniform(0.5, 10.0)), 2)
        else:
            if self.selected_category != "all" and self.selected_category in data_pool.HS_CODES:
                category = self.selected_category
            else:
                category = random.choice(list(data_pool.HS_CODES.keys()))
                
            brand = random.choice(data_pool.BRANDS)
            cost = round(random.uniform(5.0, 150.0), 2)
            desc = f"Shipedge Premium {category} - {brand} Edition"
            weight = round(random.uniform(0.5, 20.0), 2)
            
        clean_brand = "".join(c for c in brand if c.isalnum()).upper()[:4] or "SE"
        date_str = datetime.now().strftime("%y%m%d")
        random_suffix = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=4))
        sku = f"SE-{category[:3].upper()}-{clean_brand}-{date_str}-{random_suffix}"
        
        hs_lookup_key = "Home" if "Home" in category else category
        hs_code = random.choice(data_pool.HS_CODES.get(hs_lookup_key, ["0000.00.00"]))
        
        return ShipEdgeProduct(
            SKU=sku,
            UPC="".join(str(random.randint(0, 9)) for _ in range(12)),
            Description=desc,
            Cost=cost,
            Declared=round(cost * random.uniform(1.2, 1.8), 2),
            Weight=weight,
            Length=round(random.uniform(10, 100), 2),
            Width=round(random.uniform(10, 80), 2),
            Height=round(random.uniform(5, 50), 2),
            Quantity=random.randint(0, 1000),
            Supplier=random.choice(data_pool.SUPPLIERS_DATA)["name"],
            DistributionCenter="DC1",
            SerialNumber=f"SN-{random.getrandbits(32)}",
            Harmonization=hs_code,
            CountryOfOrigin=random.choice(["USA", "CA", "CN", "MX", "VN"])
        )
