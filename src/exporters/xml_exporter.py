# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Any
from src.domain.models import Order

class XMLExporter:
    """Maneja la exportación de modelos a formatos XML específicos."""
    
    @staticmethod
    def export_edi(orders: List[Order], output_dir: Path):
        for order in orders:
            root = ET.Element("Order")
            ET.SubElement(root, "poNumber").text = order.order_num
            ET.SubElement(root, "OrderDate").text = str(order.order_date)
            
            ship_to = ET.SubElement(root, "ShipToAddress")
            ET.SubElement(ship_to, "ContactName").text = f"{order.customer.firstname} {order.customer.lastname}"
            ET.SubElement(ship_to, "Address1").text = order.shipping_address.address1
            ET.SubElement(ship_to, "City").text = order.shipping_address.city
            ET.SubElement(ship_to, "Country").text = order.shipping_address.country
            
            for item in order.items:
                line = ET.SubElement(root, "LineItem")
                ET.SubElement(line, "QtyOrdered").text = str(item.quantity)
                ET.SubElement(line, "SKU").text = item.sku
                ET.SubElement(line, "Description").text = item.description
                ET.SubElement(line, "UnitCost").text = str(item.sold_price)
            
            tree = ET.ElementTree(root)
            filename = f"EDI_{order.order_num}.xml"
            tree.write(output_dir / filename, encoding="utf-8", xml_declaration=True)
            
        return len(orders)
