# -*- coding: utf-8 -*-
import os
import random
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from src.core.base_generator import BaseGenerator

class CHGenerator(BaseGenerator):
    """Generador de archivos .neworders para Cargo Hub (The Home Depot)."""
    
    def generate_batch(self, count: int, output_dir: str = "data/ch_neworders"):
        os.makedirs(output_dir, exist_ok=True)
        generated_files = []
        
        for i in range(count):
            now = datetime.now() + timedelta(minutes=i)
            po_number = f"CH{now.strftime('%Y%m%d%H%M')}"
            filename = f"{po_number}.neworders"
            filepath = os.path.join(output_dir, filename)
            
            root = self._create_ch_structure(now, po_number)
            tree = ET.ElementTree(root)
            tree.write(filepath, encoding="utf-8", xml_declaration=True)
            generated_files.append(filepath)
            
        return generated_files

    def _create_ch_structure(self, now: datetime, po_number: str) -> ET.Element:
        order_date = now.strftime("%Y%m%d")
        transaction_id = random.randint(3200000000, 3299999999)
        order_id = transaction_id + 2
        cust_order = f"WP{random.randint(56000000, 56999999)}"
        batch_number = now.strftime("%Y%m%d%H%M%S")
        
        root = ET.Element("OrderMessageBatch", batchNumber=str(batch_number))
        partner = ET.SubElement(root, "partnerID", name="Sunfuture Inc", roleType="vendor")
        partner.text = "sunfuture"
        
        hub = ET.SubElement(root, "hubOrder", transactionID=str(transaction_id))
        merchant = ET.SubElement(hub, "participatingParty", name="The Home Depot Inc", roleType="merchant", participationCode="From:")
        merchant.text = "thehomedepot"
        
        ET.SubElement(hub, "sendersIdForReceiver").text = "60011745"
        ET.SubElement(hub, "orderId").text = str(order_id)
        ET.SubElement(hub, "lineCount").text = "1"
        ET.SubElement(hub, "poNumber").text = po_number
        ET.SubElement(hub, "orderDate").text = order_date
        
        ET.SubElement(hub, "shipTo", personPlaceID="PP5871098487")
        ET.SubElement(hub, "billTo", personPlaceID="PP5871098487")
        ET.SubElement(hub, "customer", personPlaceID="PP5871098489")
        ET.SubElement(hub, "invoiceTo", personPlaceID="PP5871098488")
        
        ET.SubElement(hub, "shippingCode").text = "UNSP_CG"
        ET.SubElement(hub, "controlNumber").text = "100"
        ET.SubElement(hub, "salesDivision").text = "8119"
        ET.SubElement(hub, "custOrderNumber").text = cust_order
        ET.SubElement(hub, "buyingContract").text = "60011745"
        
        # poHdrData
        hdr = ET.SubElement(hub, "poHdrData")
        ET.SubElement(hdr, "merchDept").text = "28"
        ET.SubElement(hdr, "reqShipDate").text = order_date
        ET.SubElement(hdr, "custOrderNumber").text = cust_order
        ET.SubElement(hdr, "poTypeCode").text = "00"
        
        # Line Item
        line = ET.SubElement(hub, "lineItem")
        ET.SubElement(line, "lineItemId").text = str(random.randint(3300000000, 3399999999))
        ET.SubElement(line, "orderLineNumber").text = "1"
        ET.SubElement(line, "merchantLineNumber").text = "501"
        ET.SubElement(line, "qtyOrdered").text = str(random.randint(1, 10))
        ET.SubElement(line, "unitOfMeasure").text = "EA"
        ET.SubElement(line, "UPC").text = "".join(str(random.randint(0, 9)) for _ in range(12))
        ET.SubElement(line, "description").text = "Cargo Hub Product"
        ET.SubElement(line, "merchantSKU").text = f"MS-{random.randint(10000, 99999)}"
        ET.SubElement(line, "vendorSKU").text = f"VS-{random.randint(10000, 99999)}"
        ET.SubElement(line, "shoppingCartSKU").text = str(random.randint(310000000, 319999999))
        ET.SubElement(line, "unitCost").text = f"{random.uniform(50, 200):.4f}"
        ET.SubElement(line, "shippingCode").text = "UNSP_CG"
        ET.SubElement(line, "expectedShipDate").text = order_date
        ET.SubElement(line, "poLineData")
        
        # personPlace CUSTOMER
        pp_customer = ET.SubElement(hub, "personPlace", personPlaceID="PP5871098489")
        ET.SubElement(pp_customer, "name1").text = "Home Depot Customer"
        ET.SubElement(pp_customer, "partnerPersonPlaceId").text = "8119"
        
        # personPlace SHIP TO
        pp_ship = ET.SubElement(hub, "personPlace", personPlaceID="PP5871098487")
        ET.SubElement(pp_ship, "name1").text = "John Connor"
        ET.SubElement(pp_ship, "addressRateClass").text = "2"
        ET.SubElement(pp_ship, "address1").text = "C/O THD Ship to Store #4007"
        ET.SubElement(pp_ship, "address2").text = "1728 N Tomahawk Island Dr"
        ET.SubElement(pp_ship, "city").text = "Portland"
        ET.SubElement(pp_ship, "state").text = "OR"
        ET.SubElement(pp_ship, "country").text = "US"
        ET.SubElement(pp_ship, "postalCode").text = "97217"
        ET.SubElement(pp_ship, "dayPhone").text = "5032899200"
        ET.SubElement(pp_ship, "partnerPersonPlaceId").text = "4007"
        
        # personPlace INVOICE
        pp_invoice = ET.SubElement(hub, "personPlace", personPlaceID="PP5871098488")
        ET.SubElement(pp_invoice, "name1").text = "Home Depot"
        ET.SubElement(pp_invoice, "partnerPersonPlaceId").text = "8119"
        
        ET.SubElement(root, "messageCount").text = "1"
        return root

    def generate_single(self):
        pass
