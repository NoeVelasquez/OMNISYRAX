# -*- coding: utf-8 -*-
import requests
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.domain.models import Order, Product

logger = logging.getLogger(__name__)

class APIExporter:
    """
    Carga datos a la API de Omnio replicando el comportamiento del cargador original JS.
    """
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_company_id(self) -> Optional[str]:
        """Intenta obtener el Company ID asociado al token."""
        endpoint = f"{self.base_url}/api/1.0/users/information?include=company"
        try:
            res = requests.get(endpoint, headers=self.headers)
            if res.ok:
                data = res.json().get("data", res.json())
                return str(data.get("company", {}).get("id") or data.get("company_id", ""))
        except:
            pass
        return None

    def get_processes(self, company_id: str) -> List[Dict[str, Any]]:
        """Obtiene y filtra procesos para la compañía."""
        endpoint = f"{self.base_url}/api/1.0/processes?include=service"
        try:
            res = requests.get(endpoint, headers=self.headers)
            if res.ok:
                all_procs = res.json().get("data", res.json())
                if not isinstance(all_procs, list): all_procs = []
                # Filtrar por compañía
                return [p for p in all_procs if str(p.get("company_id") or p.get("company", {}).get("id")) == str(company_id)]
        except Exception as e:
            logger.error(f"Error obteniendo procesos: {e}")
        return []

    def get_tenant_skus(self, company_id: str) -> List[str]:
        """Intenta obtener la lista de SKUs activos de la compañía desde la API."""
        skus = []
        endpoints = [
            f"{self.base_url}/admin/api/2024-01/products?limit=250",
            f"{self.base_url}/api/1.0/products?company_id={company_id}"
        ]
        for endpoint in endpoints:
            try:
                res = requests.get(endpoint, headers=self.headers, timeout=10)
                if res.ok:
                    data = res.json()
                    products = data.get("data", data)
                    if isinstance(products, list):
                        for p in products:
                            skus_list = p.get("skus")
                            if isinstance(skus_list, list):
                                for s in skus_list:
                                    sku = s.get("sku")
                                    if sku:
                                        skus.append(sku)
                            else:
                                sku = p.get("sku") or p.get("variant_sku")
                                if sku:
                                    skus.append(sku)
                        if skus:
                            break
            except Exception as e:
                logger.debug(f"Error consultando endpoint {endpoint}: {e}")
        return skus

    def _upload_single_order(self, order: Order, company_id: str, process_id: str, index: int, endpoint: str, forced_currency: str = None) -> Dict[str, Any]:
        payload = self._build_order_payload(order, company_id, process_id, index, forced_currency)
        order_num_with_idx = payload.get("order_num", f"{order.order_num}-{index}")
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=15)
            
            # Si el error es de moneda inválida, reintentar automáticamente con "USD"
            if response.status_code == 422 and "currency" in response.text.lower() and payload.get("currency") != "USD":
                logger.info(f"⚠️ Moneda '{payload.get('currency')}' no soportada por el tenant. Auto-ajustando a 'USD' para {order_num_with_idx}...")
                payload["currency"] = "USD"
                response = requests.post(endpoint, json=payload, headers=self.headers, timeout=15)

            if response.status_code in [200, 201]:
                logger.info(f"✅ Orden {order_num_with_idx} cargada con éxito.")
                return {"order_num": order_num_with_idx, "success": True, "status": response.status_code, "error": ""}
            elif response.status_code == 422:
                err_msg = f"Datos inválidos (422) - {response.text}"
                logger.error(f"❌ Error en Orden {order_num_with_idx}: {err_msg}")
                return {"order_num": order_num_with_idx, "success": False, "status": response.status_code, "error": err_msg[:200]}
            else:
                err_msg = f"Error {response.status_code}: {response.text}"
                logger.error(f"❌ Error {order_num_with_idx}: {err_msg}")
                return {"order_num": order_num_with_idx, "success": False, "status": response.status_code, "error": err_msg[:200]}
        except Exception as e:
            logger.error(f"💥 Error de conexión al cargar {order_num_with_idx}: {e}")
            return {"order_num": order_num_with_idx, "success": False, "status": 0, "error": f"Error de conexión: {str(e)}"}

    def upload_orders(self, orders: List[Order], company_id: str, process_id: str, max_workers: int = 5, forced_currency: str = None) -> List[Dict[str, Any]]:
        endpoint = f"{self.base_url}/admin/api/2024-01/orders"
        results = []
        
        if not orders:
            logger.warning("No hay órdenes para cargar.")
            return []

        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            transient=True
        ) as progress:
            task = progress.add_task(f"Subiendo órdenes a CID {company_id}...", total=len(orders))
            
            if max_workers <= 1 or len(orders) <= 1:
                for i, order in enumerate(orders):
                    res = self._upload_single_order(order, company_id, process_id, i, endpoint, forced_currency)
                    results.append(res)
                    progress.advance(task)
            else:
                from concurrent.futures import ThreadPoolExecutor, as_completed
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {
                        executor.submit(self._upload_single_order, order, company_id, process_id, i, endpoint, forced_currency): order
                        for i, order in enumerate(orders)
                    }
                    for future in as_completed(futures):
                        results.append(future.result())
                        progress.advance(task)
                        
        return results

    def _build_order_payload(self, order: Order, company_id: str, process_id: str, index: int, forced_currency: str = None) -> Dict[str, Any]:
        # Mapeo ISO Alpha-2 a Alpha-3 (Omnio prefiere 3 letras)
        iso3 = {
            "US": "USA", "MX": "MEX", "ES": "ESP", "PT": "PRT", 
            "GB": "GBR", "FR": "FRA", "DE": "DEU", "CA": "CAN", 
            "IT": "ITA", "BR": "BRA"
        }
        country = iso3.get(order.shipping_address.country, "USA")

        currency = forced_currency if forced_currency else order.shipping_address.currency

        return {
            "order_num": f"{order.order_num}-{index}",
            "currency": currency,
            "order_date": order.order_date.strftime("%Y-%m-%d") if isinstance(order.order_date, datetime) else str(order.order_date),
            "status_name": "draft",
            "company_id": int(company_id) if str(company_id).isdigit() else company_id,
            "process_id": int(process_id) if str(process_id).isdigit() else process_id,
            "customer": {
                "customer_email": order.customer.email,
                "customer_phone": order.customer.phone,
                "customer_firstname": order.customer.firstname,
                "customer_lastname": order.customer.lastname,
                "customer_address1": order.shipping_address.address1,
                "customer_city": order.shipping_address.city,
                "customer_state": order.shipping_address.state or "FL",
                "customer_zip": order.shipping_address.postal_code,
                "customer_country": country
            },
            "customer_bill": {
                "customer_bill_firstname": order.customer.firstname,
                "customer_bill_lastname": order.customer.lastname,
                "customer_bill_address1": order.shipping_address.address1,
                "customer_bill_city": order.shipping_address.city,
                "customer_bill_state": order.shipping_address.state or "FL",
                "customer_bill_zip": order.shipping_address.postal_code,
                "customer_bill_country": country
            },
            "shipping_information": {
                "ship_method": "AVC-AIR",
                "ship_carrier": "AVC",
                "residential": "YES"
            },
            "line_items": [
                {
                    "sku": item.sku,
                    "description": item.description,
                    "quantity": int(item.quantity),
                    "sold_price": float(item.sold_price)
                } for item in order.items
            ],
            "total_price": float(order.total_price)
        }

    def get_order_details(self, order_num: str) -> Optional[Dict[str, Any]]:
        """Obtiene los detalles de una orden específica de la API de Omnio."""
        endpoint = f"{self.base_url}/admin/api/2024-01/orders/{order_num}"
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json().get("data")
            elif response.status_code == 404:
                logger.debug(f"Orden {order_num} no encontrada (404).")
            else:
                logger.error(f"Error GET {order_num}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error de conexión al obtener detalle de orden {order_num}: {e}")
        return None

    def upload_product(self, product: Product) -> Dict[str, Any]:
        """Crea un producto base con su SKU y datos asociados en Omnio."""
        endpoint = f"{self.base_url}/admin/api/2024-01/products"
        payload = {
            "name": product.name,
            "description_html": f"<p>{product.description}</p>",
            "type": "PURCHASED",
            "sku": product.sku,
            "upc": product.upc,
            "brand": product.brand,
            "pricing": {
                "retail_price": float(product.price_retail),
                "wholesale_price": float(product.price_wholesale),
                "cost": float(product.price_buy),
                "Retail": float(product.price_retail),
                "WholeSale": float(product.price_wholesale),
                "Buy": float(product.price_buy)
            },
            "shipping": {
                "weight": float(product.weight),
                "length": float(product.length),
                "width": float(product.width),
                "height": float(product.height)
            }
        }
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=15)
            if response.status_code in [200, 201]:
                logger.info(f"✅ Producto '{product.name}' (SKU: {product.sku}) creado con éxito.")
                return {"sku": product.sku, "name": product.name, "success": True, "error": ""}
            else:
                logger.error(f"❌ Error al crear producto {product.sku}: {response.status_code} - {response.text}")
                return {"sku": product.sku, "name": product.name, "success": False, "error": f"Error {response.status_code}: {response.text}"}
        except Exception as e:
            logger.error(f"❌ Excepción al crear producto {product.sku}: {e}")
            return {"sku": product.sku, "name": product.name, "success": False, "error": str(e)}

    def upload_products(self, products: List[Product], max_workers: int = 5) -> List[Dict[str, Any]]:
        """Sube múltiples productos concurrentemente usando un progress bar de rich."""
        results = []
        if not products:
            logger.warning("No hay productos para cargar.")
            return []

        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            transient=True
        ) as progress:
            task = progress.add_task(f"Subiendo {len(products)} productos...", total=len(products))
            
            if max_workers <= 1 or len(products) <= 1:
                for product in products:
                    res = self.upload_product(product)
                    results.append(res)
                    progress.advance(task)
            else:
                from concurrent.futures import ThreadPoolExecutor, as_completed
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {
                        executor.submit(self.upload_product, product): product
                        for product in products
                    }
                    for future in as_completed(futures):
                        results.append(future.result())
                        progress.advance(task)
                        
        return results

    def get_inventories(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de inventarios (SKUs con cantidades y localizaciones) de la API."""
        endpoint = f"{self.base_url}/admin/api/2024-01/inventories"
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                logger.error(f"Error al obtener inventarios: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Excepción al obtener inventarios: {e}")
        return []

    def update_inventories_stock(self, adjustments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Realiza un ajuste de stock en bloque en Omnio.
        adjustments es una lista de diccionarios con el formato requerido por la API:
        [
            {
                "iloc_id": int,
                "skus": [
                    {"sku_id": int, "qty_good": int},
                    ...
                ]
            }
        ]
        """
        endpoint = f"{self.base_url}/admin/api/2024-01/inventories"
        payload = {"inventories": adjustments}
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=15)
            if response.status_code in [200, 201]:
                return {"success": True, "error": ""}
            else:
                return {"success": False, "error": f"Error {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def upload_purchase_order(self, payload: Dict[str, Any], is_transfer: bool = False) -> Dict[str, Any]:
        """Sube una Purchase Order o una Transferencia vía API."""
        path = "transfers" if is_transfer else "purchase-orders"
        endpoint = f"{self.base_url}/admin/api/2024-01/{path}"
        doc_num = payload.get("po_num", "N/A")
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=15)
            if response.status_code in [200, 201]:
                logger.info(f"✅ {'Transferencia' if is_transfer else 'PO'} {doc_num} cargada con éxito.")
                return {"doc_num": doc_num, "success": True, "error": ""}
            else:
                logger.error(f"❌ Error al crear {path} {doc_num}: {response.status_code} - {response.text}")
                return {"doc_num": doc_num, "success": False, "error": f"Error {response.status_code}: {response.text}"}
        except Exception as e:
            logger.error(f"❌ Excepción al crear {path} {doc_num}: {e}")
            return {"doc_num": doc_num, "success": False, "error": str(e)}

    def get_purchase_orders(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtiene la lista de POs."""
        endpoint = f"{self.base_url}/admin/api/2024-01/purchase-orders"
        params = {"per_page": limit}
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                logger.error(f"Error al obtener POs: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Excepción al obtener POs: {e}")
        return []

    def get_transfers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtiene la lista de Transferencias."""
        endpoint = f"{self.base_url}/admin/api/2024-01/transfers"
        params = {"per_page": limit}
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                logger.error(f"Error al obtener Transferencias: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Excepción al obtener Transferencias: {e}")
        return []

    def get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su SKU usando search."""
        endpoint = f"{self.base_url}/admin/api/2024-01/products"
        params = {"search": f"sku:{sku}"}
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json().get("data", [])
                if data:
                    return data[0]
            else:
                logger.error(f"Error al buscar producto {sku}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Excepción al buscar producto {sku}: {e}")
        return None

    def fulfill_shipment(self, shipment_id: int, tracking_number: str) -> Dict[str, Any]:
        """Marca un envío como despachado (status shipped) y le asigna tracking."""
        endpoint = f"{self.base_url}/admin/api/2024-01/shipments/{shipment_id}/status"
        payload = {
            "status": "shipped",
            "tracking_number": tracking_number
        }
        try:
            response = requests.patch(endpoint, json=payload, headers=self.headers, timeout=15)
            if response.status_code in [200, 204]:
                return {"success": True, "error": ""}
            else:
                return {"success": False, "error": f"Error {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_order(self, order_id: Any) -> Dict[str, Any]:
        """Elimina/cancela una orden vía API usando su ID de base de datos."""
        endpoint = f"{self.base_url}/admin/api/2024-01/orders/{order_id}"
        try:
            response = requests.delete(endpoint, headers=self.headers, timeout=15)
            if response.status_code in [200, 204]:
                return {"success": True, "error": ""}
            else:
                return {"success": False, "error": f"Error {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cancel_order(self, order_id: Any) -> Dict[str, Any]:
        """Cambia el estado de una orden a CANCEL vía API usando su ID de base de datos."""
        endpoint = f"{self.base_url}/admin/api/2024-01/orders/{order_id}/change-status"
        payload = {"status": "cancel"}
        try:
            response = requests.patch(endpoint, json=payload, headers=self.headers, timeout=15)
            if response.status_code in [200, 204]:
                return {"success": True, "error": ""}
            else:
                return {"success": False, "error": f"Error {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def clear_inventories_stock(self, inventories_payload: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Elimina stock físico de inventario masivamente vía API."""
        endpoint = f"{self.base_url}/admin/api/2024-01/inventories-delete"
        payload = {"inventories": inventories_payload}
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=15)
            if response.status_code in [200, 201, 204]:
                return {"success": True, "error": ""}
            else:
                return {"success": False, "error": f"Error {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}





