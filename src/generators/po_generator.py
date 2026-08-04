# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta
from src.core.base_generator import BaseGenerator
from src.domain.models import PurchaseOrder, OrderItem
from src.utils import data_pool

class POGenerator(BaseGenerator):
    """Generador de órdenes de compra (Purchase Orders)."""
    
    def __init__(self, lang: str = "es"):
        super().__init__(lang)
        self.available_skus = []
        self.products_by_supplier = {}

    def generate_batch(self, count: int, skus: list = None, products: list = None) -> list[PurchaseOrder]:
        if products:
            self.products_by_supplier = {}
            for p in products:
                if p.supplier not in self.products_by_supplier:
                    self.products_by_supplier[p.supplier] = []
                self.products_by_supplier[p.supplier].append(p.sku)
            self.available_skus = [p.sku for p in products]
        else:
            self.available_skus = skus or []
            self.products_by_supplier = {}
            
        return [self.generate_single() for _ in range(count)]

    def generate_single(self) -> PurchaseOrder:
        # Si tenemos productos agrupados por proveedor, elegir un proveedor que tenga SKUs
        if self.products_by_supplier:
            supplier_name = random.choice(list(self.products_by_supplier.keys()))
            # Buscar el objeto supplier completo en data_pool para obtener el código
            supplier = next((s for s in data_pool.SUPPLIERS_DATA if s["name"] == supplier_name), None)
            if not supplier:
                # Fallback si el nombre no coincide exactamente (no debería pasar)
                supplier = random.choice(data_pool.SUPPLIERS_DATA)
                available_for_this_po = self.products_by_supplier.get(supplier_name, self.available_skus)
            else:
                available_for_this_po = self.products_by_supplier[supplier_name]
        else:
            supplier = random.choice(data_pool.SUPPLIERS_DATA)
            available_for_this_po = self.available_skus

        num_items = random.randint(1, 10)
        items = []
        total_cost = 0
        used_skus = set()
        
        # Determinar SKUs únicos para esta PO
        po_skus = []
        if available_for_this_po:
            count_to_pick = min(num_items, len(available_for_this_po))
            po_skus = random.sample(available_for_this_po, count_to_pick)
        else:
            while len(po_skus) < num_items:
                sku = f"SKU-{random.randint(1000, 9999)}"
                if sku not in used_skus:
                    po_skus.append(sku)
                    used_skus.add(sku)
        
        for sku in po_skus:
            item = OrderItem(
                sku=sku,
                description=f"Supplied Item",
                quantity=random.randint(50, 500),
                sold_price=round(random.uniform(1, 50), 2)
            )
            items.append(item)
            total_cost += item.sold_price * item.quantity
            
        timestamp = datetime.now().strftime("%m%d%H%M%S")
        po_num = f"PO-{timestamp}-{random.randint(1000, 9999)}"

        return PurchaseOrder(
            po_number=po_num,
            date=datetime.now().date() - timedelta(days=random.randint(0, 60)),
            supplier_code=supplier["code"],
            supplier_name=supplier["name"],
            items=items,
            total_cost=round(total_cost, 2)
        )
