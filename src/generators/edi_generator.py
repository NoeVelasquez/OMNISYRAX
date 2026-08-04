# -*- coding: utf-8 -*-
import os
import random
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from src.core.base_generator import BaseGenerator

class EDIGenerator(BaseGenerator):
    """Generador de archivos XML en formato EDI Estándar."""
    
    def generate_batch(self, count: int, output_dir: str = "data/edi_xmls", items_mode: str = "single", sku_choice: str = "random"):
        os.makedirs(output_dir, exist_ok=True)
        generated_files = []
        
        base_now = datetime.now()
        for i in range(count):
            now = base_now + timedelta(milliseconds=i)
            timestamp_str = now.strftime("%Y%m%d%H%M%S%f")[:-3]
            filename = f"Edi{timestamp_str}.xml"
            filepath = os.path.join(output_dir, filename)
            
            root = self._create_xml_structure(timestamp_str, items_mode, sku_choice)
            # Pretty-print indentation
            ET.indent(root, space="    ")
            tree = ET.ElementTree(root)
            tree.write(filepath, encoding="utf-8", xml_declaration=True)
            generated_files.append(filepath)
            
        return generated_files

    def _create_xml_structure(self, timestamp_str: str, items_mode: str = "single", sku_choice: str = "random") -> ET.Element:
        order = ET.Element("Order")
        ET.SubElement(order, "poNumber").text = f"Edi{timestamp_str}"
        ET.SubElement(order, "ReferenceNumber").text = f"Ref-{timestamp_str}"
        ET.SubElement(order, "OrderDate").text = timestamp_str[:8]
        ET.SubElement(order, "ShippingMethod").text = "TEST"
        ET.SubElement(order, "Carrier").text = "FDEG"
        ET.SubElement(order, "ServiceLevelCode").text = "G2"
        
        ship_to = ET.SubElement(order, "ShipToAddress")
        ET.SubElement(ship_to, "ContactName").text = "EDI Helpdesk"
        ET.SubElement(ship_to, "Address1").text = "7000 Target Parkway"
        ET.SubElement(ship_to, "City").text = "Brooklyn Park"
        ET.SubElement(ship_to, "State").text = "MN"
        ET.SubElement(ship_to, "PostalCode").text = "55445"
        ET.SubElement(ship_to, "Country").text = "US"
        ET.SubElement(ship_to, "Phone").text = "612-304-3310"

        bill_to = ET.SubElement(order, "BillToAddress")
        ET.SubElement(bill_to, "ContactName").text = "Target.com Accounts Payable"
        ET.SubElement(bill_to, "Address1").text = "TNC 3110"
        ET.SubElement(bill_to, "Address2").text = "PO Box 1296"
        ET.SubElement(bill_to, "City").text = "Minneapolis"
        ET.SubElement(bill_to, "State").text = "MN"
        ET.SubElement(bill_to, "PostalCode").text = "55440"
        ET.SubElement(bill_to, "Country").text = "US"
        
        num_items = random.randint(2, 5) if items_mode == "multi" else 1
        
        for idx in range(num_items):
            line_item = ET.SubElement(order, "LineItem")
            ET.SubElement(line_item, "OrderLineNumber").text = str(idx + 1)
            ET.SubElement(line_item, "QtyOrdered").text = str(random.randint(1, 25))
            ET.SubElement(line_item, "UnitOfMeasure").text = "EA"
            ET.SubElement(line_item, "Description").text = "Standard EDI Item" if idx == 0 else f"Additional EDI Item {idx + 1}"
            
            # SKU selection logic
            if idx == 0 and sku_choice == "fixed":
                item_sku = "990394169"
            else:
                item_sku = f"SKU-{random.randint(1000, 9999)}"
                
            ET.SubElement(line_item, "SKU").text = item_sku
            ET.SubElement(line_item, "UPC").text = "".join(str(random.randint(0, 9)) for _ in range(12))
            ET.SubElement(line_item, "UnitCost").text = f"{random.uniform(10, 50):.2f}"
        
        return order

    def generate_single(self):
        # BaseGenerator requires this, but we override generate_batch for XML
        pass
