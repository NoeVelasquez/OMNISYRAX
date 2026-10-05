# -*- coding: utf-8 -*-
import requests
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.domain.models import Order, Product

logger = logging.getLogger(__name__)

class APIExporter:
    """
    Carga datos a la API de Omnio replicando el comportamiento del cargador original JS.
    Soporta Idempotencia y los endpoints tanto públicos como por tenant.
    """
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        clean_token = str(token or "").strip().strip('"').strip("'")
        if clean_token.lower().startswith("bearer "):
            clean_token = clean_token[7:].strip()
        self.base_headers = {
            "Authorization": f"Bearer {clean_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    @property
    def headers(self) -> Dict[str, str]:
        """Propiedad de compatibilidad que retorna los headers base con Idempotency-Key."""
        return self._get_headers()

    def _get_headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        """Genera los headers incluyendo la clave de idempotencia única si se solicita o por defecto."""
        headers = self.base_headers.copy()
        key = idempotency_key or str(uuid.uuid4())
        headers["Idempotency-Key"] = key
        headers["X-Idempotency-Key"] = key
        return headers

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
        headers = self._get_headers(idempotency_key=f"order-{order_num_with_idx}")
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
            
            # Si el error es de moneda inválida, reintentar automáticamente con "USD"
            if response.status_code == 422 and "currency" in response.text.lower() and payload.get("currency") != "USD":
                logger.info(f"⚠️ Moneda '{payload.get('currency')}' no soportada por el tenant. Auto-ajustando a 'USD' para {order_num_with_idx}...")
                payload["currency"] = "USD"
                response = requests.post(endpoint, json=payload, headers=headers, timeout=15)

            # Si 401 Unauthenticated en el endpoint público, reintentar con el endpoint de tenant (/api/1.0/tenants/{company_id}/orders)
            if response.status_code == 401 and "/admin/api/2024-01/" in endpoint:
                alt_endpoint = f"{self.base_url}/api/1.0/tenants/{company_id}/orders"
                logger.info(f"🔄 Reintentando con endpoint alternativo de tenant: {alt_endpoint}")
                response = requests.post(alt_endpoint, json=payload, headers=headers, timeout=15)

            # Si 429 Too Many Attempts (rate limit de Laravel), pausar brevemente y reintentar
            if response.status_code == 429:
                import time
                logger.info(f"⏳ Rate limit alcanzado (429) para {order_num_with_idx}. Pausando 2 segundos antes de reintentar...")
                time.sleep(2)
                target = alt_endpoint if 'alt_endpoint' in locals() else endpoint
                response = requests.post(target, json=payload, headers=headers, timeout=15)
                if response.status_code == 429:
                    time.sleep(3)
                    response = requests.post(target, json=payload, headers=headers, timeout=15)

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
        endpoint = f"{self.base_url}/api/1.0/tenants/{company_id}/orders"
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
            "currency_id": 1,
            "ship_method": "AVC-AIR",
            "ship_carrier": "AVC",
            "order_date": order.order_date.strftime("%Y-%m-%d") if isinstance(order.order_date, datetime) else str(order.order_date),
            "status_name": "draft",
            "company_id": int(company_id) if str(company_id).isdigit() else company_id,
            "process_id": int(process_id) if str(process_id).isdigit() else process_id,
            "customer_email": order.customer.email,
            "customer_phone": order.customer.phone,
            "customer_firstname": order.customer.firstname,
            "customer_lastname": order.customer.lastname,
            "customer_address1": order.shipping_address.address1,
            "customer_city": order.shipping_address.city,
            "customer_state": order.shipping_address.state or "FL",
            "customer_zip": order.shipping_address.postal_code,
            "customer_country": country,
            "customer_bill_firstname": order.customer.firstname,
            "customer_bill_lastname": order.customer.lastname,
            "customer_bill_address1": order.shipping_address.address1,
            "customer_bill_city": order.shipping_address.city,
            "customer_bill_state": order.shipping_address.state or "FL",
            "customer_bill_zip": order.shipping_address.postal_code,
            "customer_bill_country": country,
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
        """Obtiene un producto por su SKU buscando en las variantes de la API."""
        endpoint = f"{self.base_url}/admin/api/2024-01/products"
        target_sku = sku.strip().lower()
        
        # Iterar las primeras páginas de productos buscando el SKU exacto
        for page in range(1, 10):
            try:
                params = {"include": "skus", "page": page, "per_page": 100}
                response = requests.get(endpoint, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json().get("data", [])
                    if not data:
                        break
                    for prod in data:
                        skus_list = prod.get("skus") or []
                        for s in skus_list:
                            if str(s.get("sku")).strip().lower() == target_sku:
                                return prod
                        if str(prod.get("sku")).strip().lower() == target_sku:
                            return prod
                else:
                    break
            except Exception as e:
                logger.error(f"Excepción al buscar producto {sku}: {e}")
                break
        return None

    def fulfill_shipment(self, shipment_id: int, tracking_number: str) -> Dict[str, Any]:
        """Marca una orden/envío como despachado (status shipped)."""
        # Usamos change-status en la orden directamente para no disparar el bug del backend de CONDOR (Undefined array key -1)
        endpoint = f"{self.base_url}/admin/api/2024-01/orders/{shipment_id}/change-status"
        payload = {"status": "shipped"}
        try:
            response = requests.patch(endpoint, json=payload, headers=self.headers, timeout=15)
            if response.status_code in [200, 204]:
                return {"success": True, "error": ""}
            else:
                return {"success": False, "error": f"Error {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_all_open_shipments(self, company_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtiene envíos pendientes (no despachados) de las órdenes del tenant."""
        endpoint = f"{self.base_url}/api/1.0/tenants/{company_id}/orders" if company_id else f"{self.base_url}/admin/api/2024-01/orders"
        params = {"include": "shipments", "per_page": limit}
        shipments = []
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=15)
            if response.status_code == 401 and company_id:
                alt = f"{self.base_url}/api/1.0/tenants/{company_id}/orders"
                response = requests.get(alt, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                orders = response.json().get("data", response.json() if isinstance(response.json(), list) else [])
                if isinstance(orders, dict): orders = orders.get("data", [])
                for order in orders:
                    for s in (order.get("shipments") or []):
                        if str(s.get("status")).lower() != "shipped":
                            s["order_num"] = order.get("order_num")
                            shipments.append(s)
        except Exception as e:
            logger.error(f"Error obteniendo envíos: {e}")
        return shipments

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

    def upload_tenant_metadata(self, tenant_id: str, key: str, value: Any, entity_type: str = "sku") -> Dict[str, Any]:
        """Agrega o actualiza metadatos dinámicos por tenant (/api/1.0/tenants/{tenant_id}/metadata)."""
        endpoint = f"{self.base_url}/api/1.0/tenants/{tenant_id}/metadata"
        payload = {
            "key": key,
            "value": value,
            "entity_type": entity_type
        }
        headers = self._get_headers(idempotency_key=f"meta-{tenant_id}-{key}")
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
            if response.status_code in [200, 201]:
                return {"success": True, "status": response.status_code, "error": ""}
            else:
                return {"success": False, "status": response.status_code, "error": response.text[:200]}
        except Exception as e:
            return {"success": False, "status": 0, "error": str(e)}

    def upload_sku_alternative(self, tenant_id: str, original_sku: str, alternative_sku: str) -> Dict[str, Any]:
        """Registra un SKU alternativo/equivalente en el tenant."""
        endpoint = f"{self.base_url}/api/1.0/tenants/{tenant_id}/sku-alternative"
        payload = {
            "sku": original_sku,
            "alternative_sku": alternative_sku
        }
        headers = self._get_headers(idempotency_key=f"skualt-{tenant_id}-{original_sku}-{alternative_sku}")
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
            if response.status_code in [200, 201]:
                return {"success": True, "status": response.status_code, "error": ""}
            else:
                return {"success": False, "status": response.status_code, "error": response.text[:200]}
        except Exception as e:
            return {"success": False, "status": 0, "error": str(e)}

    def run_qa_api_suite(self, company_id: str, process_id: str, max_tests: int = 50) -> Dict[str, Any]:
        """Ejecuta una Suite de Pruebas de QA Masiva iterando dinámicamente sobre el catálogo completo de endpoints (609 endpoints)."""
        import os
        import json
        logger.info(f"🧪 Iniciando Suite Masiva de QA de APIs para Company ID: {company_id}")
        suite_results = {"passed": 0, "failed": 0, "details": []}
        
        catalog_path = "data/condor_api_catalog.json"
        endpoints_to_test = []

        if os.path.exists(catalog_path):
            with open(catalog_path, "r") as f:
                catalog = json.load(f)
                # Filtrar métodos GET seguros para auditoría automatizada
                get_endpoints = [ep for ep in catalog if ep["method"] == "GET"]
                endpoints_to_test = get_endpoints[:max_tests]
        
        if not endpoints_to_test:
            # Fallback si no existe catálogo
            endpoints_to_test = [
                {"method": "GET", "path": "/api/1.0/users/information", "spec": "omnio"},
                {"method": "GET", "path": "/admin/api/2024-01/products", "spec": "tenant"},
                {"method": "GET", "path": f"/api/1.0/tenants/{company_id}/orders", "spec": "tenant"},
                {"method": "GET", "path": f"/api/1.0/tenants/{company_id}/skus", "spec": "tenant"},
                {"method": "GET", "path": f"/api/1.0/tenants/{company_id}/shipments", "spec": "tenant"},
                {"method": "GET", "path": f"/api/1.0/tenants/{company_id}/boxes", "spec": "tenant"},
                {"method": "GET", "path": f"/api/1.0/tenants/{company_id}/metadata", "spec": "tenant"}
            ]

        from concurrent.futures import ThreadPoolExecutor, as_completed

        def _test_single(ep):
            raw_path = ep["path"]
            if raw_path.startswith("/tenants/"):
                raw_path = f"/api/1.0{raw_path}"
            elif raw_path.startswith("tenants/"):
                raw_path = f"/api/1.0/{raw_path}"

            path = raw_path.replace("{tenant_id}", str(company_id)).replace("{company_id}", str(company_id)).replace("{tenant}", str(company_id))
            url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
            
            try:
                res = requests.get(url, headers=self._get_headers(), timeout=4)
                passed = res.status_code in [200, 201, 204]
                return {
                    "test": f"{ep['method']} {ep['path']}",
                    "code": res.status_code,
                    "passed": passed
                }
            except Exception:
                return {
                    "test": f"{ep['method']} {ep['path']}",
                    "code": 0,
                    "passed": False
                }

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(_test_single, ep) for ep in endpoints_to_test]
            for future in as_completed(futures):
                res = future.result()
                suite_results["details"].append(res)
                if res["passed"]:
                    suite_results["passed"] += 1
                else:
                    suite_results["failed"] += 1

        return suite_results

    def run_stress_test(self, company_id: str, total_requests: int = 50, concurrency: int = 10, target_path: str = "/api/1.0/tenants/{tenant_id}/orders") -> Dict[str, Any]:
        """
        Fase 1: Ejecuta una prueba de estrés y carga masiva sobre las APIs de Condor.
        Mide latencia (min, max, avg, p95), peticiones por segundo (RPS) y desglose de códigos HTTP.
        """
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed

        path = target_path.replace("{tenant_id}", str(company_id)).replace("{company_id}", str(company_id)).replace("{tenant}", str(company_id))
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"

        latencies = []
        status_counts = {}
        errors = 0

        start_total = time.time()

        def _make_request(idx: int):
            t0 = time.time()
            headers = self._get_headers(idempotency_key=f"stress-{company_id}-{idx}-{t0}")
            try:
                res = requests.get(url, headers=headers, timeout=10)
                t1 = time.time()
                elapsed_ms = (t1 - t0) * 1000
                return {"code": res.status_code, "latency_ms": elapsed_ms, "error": None}
            except Exception as e:
                t1 = time.time()
                elapsed_ms = (t1 - t0) * 1000
                return {"code": 0, "latency_ms": elapsed_ms, "error": str(e)}

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(_make_request, i) for i in range(total_requests)]
            for future in as_completed(futures):
                res = future.result()
                code = res["code"]
                latencies.append(res["latency_ms"])
                status_counts[code] = status_counts.get(code, 0) + 1
                if code == 0 or code >= 500:
                    errors += 1

        end_total = time.time()
        total_duration = end_total - start_total
        rps = total_requests / total_duration if total_duration > 0 else 0

        latencies.sort()
        min_lat = latencies[0] if latencies else 0
        max_lat = latencies[-1] if latencies else 0
        avg_lat = sum(latencies) / len(latencies) if latencies else 0
        p95_idx = int(len(latencies) * 0.95)
        p95_lat = latencies[min(p95_idx, len(latencies) - 1)] if latencies else 0

        return {
            "total_requests": total_requests,
            "concurrency": concurrency,
            "total_duration_sec": round(total_duration, 2),
            "rps": round(rps, 2),
            "latency_ms": {
                "min": round(min_lat, 2),
                "max": round(max_lat, 2),
                "avg": round(avg_lat, 2),
                "p95": round(p95_lat, 2)
            },
            "status_counts": status_counts,
            "errors": errors,
            "target_url": url
        }

    def send_return_rma(self, tenant_id: str, order_num: str, sku: str, quantity: int = 1, reason: str = "Defective") -> Dict[str, Any]:
        """Fase 2: Crea e inyecta un RMA / Registro de Devolución vía API."""
        endpoint = f"{self.base_url}/api/1.0/tenants/{tenant_id}/return-item"
        payload = {
            "order_num": order_num,
            "sku": sku,
            "quantity": quantity,
            "reason": reason,
            "status": "pending",
            "rma_number": f"RMA-{order_num}-{int(datetime.now().timestamp())}"
        }
        headers = self._get_headers(idempotency_key=f"rma-{tenant_id}-{order_num}-{sku}")
        try:
            res = requests.post(endpoint, json=payload, headers=headers, timeout=15)
            if res.status_code in [200, 201]:
                return {"success": True, "status": res.status_code, "rma": payload["rma_number"], "error": ""}
            else:
                return {"success": False, "status": res.status_code, "error": res.text[:200]}
        except Exception as e:
            return {"success": False, "status": 0, "error": str(e)}

    def simulate_webhook_event(self, company_id: str, event_type: str = "orders/canceled", order_num: str = "ORD-TEST-100", process_id: str = None) -> Dict[str, Any]:
        """Fase 2: Simula el envío de un evento Webhook externo (Shopify/Shipedge WMS) hacia la API de Condor."""
        pid = process_id or "1"
        if "shipedge" in event_type:
            sub = event_type.replace("shipedge/", "")
            endpoint = f"{self.base_url}/api/1.0/tenants/{company_id}/webhooks/shipedge/{sub}"
        elif "mercado" in event_type:
            endpoint = f"{self.base_url}/api/1.0/webhooks/mercado_libre"
        else:
            endpoint = f"{self.base_url}/api/1.0/processes/{pid}/shopify/webhook/{event_type}"

        payload = {
            "id": int(datetime.now().timestamp()),
            "order_num": order_num,
            "event": event_type,
            "created_at": datetime.now().isoformat(),
            "note": "Simulado desde OMNISYRAX Phase 2 Webhook Simulator"
        }
        headers = self._get_headers(idempotency_key=f"wh-{company_id}-{order_num}-{event_type}")
        try:
            res = requests.post(endpoint, json=payload, headers=headers, timeout=15)
            if res.status_code in [200, 201, 204]:
                return {"success": True, "status": res.status_code, "event": event_type, "error": ""}
            else:
                return {"success": False, "status": res.status_code, "event": event_type, "error": res.text[:200]}
        except Exception as e:
            return {"success": False, "status": 0, "event": event_type, "error": str(e)}

    def get_any_endpoint(self, raw_path: str, company_id: str = "1", params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Consume cualquier endpoint GET del catálogo dinámicamente sustituyendo los parámetros de tenant."""
        clean_path = raw_path
        if clean_path.startswith("/tenants/"):
            clean_path = f"/api/1.0{clean_path}"
        elif clean_path.startswith("tenants/"):
            clean_path = f"/api/1.0/{clean_path}"

        clean_path = clean_path.replace("{tenant_id}", str(company_id)).replace("{company_id}", str(company_id)).replace("{tenant}", str(company_id))
        url = f"{self.base_url}{clean_path}" if clean_path.startswith("/") else f"{self.base_url}/{clean_path}"

        try:
            res = requests.get(url, headers=self._get_headers(), params=params, timeout=15)
            if res.status_code == 200:
                return {"success": True, "status": res.status_code, "data": res.json(), "error": ""}
            else:
                return {"success": False, "status": res.status_code, "data": None, "error": res.text[:300]}
        except Exception as e:
            return {"success": False, "status": 0, "data": None, "error": str(e)}
