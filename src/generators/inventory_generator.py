import random
from src.core.base_generator import BaseGenerator
from src.domain.models import InventoryItem
from src.utils import data_pool

class InventoryGenerator(BaseGenerator):
    """Generador de stock/inventario con metadatos de producto."""
    
    def __init__(self, lang: str = "es"):
        super().__init__(lang)
        self.available_skus = []

    def generate_batch(self, count: int, skus: list = None) -> list[InventoryItem]:
        self.available_skus = skus or []
        return [self.generate_single() for _ in range(count)]

    def generate_single(self) -> InventoryItem:
        if self.available_skus:
            sku = random.choice(self.available_skus)
            category = sku.split("-")[1] if "-" in sku else random.choice(data_pool.PRODUCT_CATEGORIES)
            brand = random.choice(data_pool.BRANDS)
        else:
            category = random.choice(data_pool.PRODUCT_CATEGORIES)
            brand = random.choice(data_pool.BRANDS)
            product_id = random.randint(1000, 9999)
            sku = f"SKU-{category[:3].upper()}-{product_id}"
        
        # Obtener datos multilingües
        lang_data = data_pool.MULTILANG_DATA.get(self.lang, data_pool.MULTILANG_DATA["en"])
        noun = random.choice(lang_data["categories"].get(category, lang_data["categories"]["Electronics"]))
        adj = random.choice(lang_data["adjectives"])
        name = f"{adj} {noun} - {brand}"
        
        return InventoryItem(
            sku=sku,
            quantity=random.randint(10, 500),
            images=f"https://picsum.photos/seed/{sku}/600/600",
            name=name,
            description=random.choice(lang_data["descriptions"]),
            barcode="".join(str(random.randint(0, 9)) for _ in range(12)),
            price_buy=round(random.uniform(10, 50), 2),
            price_retail=round(random.uniform(100, 200), 2),
            price_wholesale=round(random.uniform(60, 90), 2),
            brand=brand,
            upc="".join(str(random.randint(0, 9)) for _ in range(12))
        )
