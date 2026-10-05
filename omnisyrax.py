import os
import csv
import random
from pathlib import Path
import typer
import logging
import questionary
import warnings
from datetime import datetime
from typing import Optional, List, Any, Dict
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

# Suprimir advertencias molestas
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")
warnings.filterwarnings("ignore", message=".*OpenSSL.*")

def extract_skus_from_csv(file_path: str) -> List[str]:
    """Extrae una lista de SKUs únicos desde cualquier archivo CSV."""
    path = Path(file_path.strip())
    if not path.exists():
        console.print(f"[bold red]❌ Error: El archivo '{file_path}' no existe.[/bold red]")
        return []
    
    skus = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            sku_col = None
            for col in fieldnames:
                if "sku" in col.lower():
                    sku_col = col
                    break
            
            if not sku_col:
                console.print(f"[bold yellow]⚠️ No se detectó ninguna columna de SKU en '{file_path}'. Columnas leídas: {fieldnames}[/bold yellow]")
                return []
            
            for row in reader:
                val = row.get(sku_col)
                if val and val.strip():
                    skus.add(val.strip())
    except Exception as e:
        console.print(f"[bold red]❌ Error al leer el archivo CSV: {e}[/bold red]")
        return []

    return sorted(list(skus))

from src.core.config_manager import config
from src.generators.order_generator import OrderGenerator
from src.generators.product_generator import ProductGenerator
from src.generators.po_generator import POGenerator
from src.generators.transfer_generator import TransferGenerator
from src.generators.shopify_generator import ShopifyGenerator
from src.generators.package_generator import PackageGenerator
from src.generators.inventory_generator import InventoryGenerator
from src.generators.shipedge_generator import ShipEdgeGenerator
from src.generators.edi_generator import EDIGenerator
from src.generators.ch_generator import CHGenerator
from src.generators.pdf_generator import PDFGenerator

from src.exporters.csv_exporter import CSVExporter
from src.exporters.api_exporter import APIExporter
from src.utils.tenant_importer import TenantImporter

import io

# Configuración de Logging
log_buffer = io.StringIO()
logging.basicConfig(
    level="INFO", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    handlers=[
        RichHandler(rich_tracebacks=True),
        logging.StreamHandler(log_buffer)
    ]
)
logger = logging.getLogger("omnisyrax")

def save_error_log():
    """Guarda el buffer de logs en un archivo solo si hay un error."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"omnisyrax-error-{timestamp}.log"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(log_buffer.getvalue())
    return filename
console = Console()
app = typer.Typer(help="🌌 OMNISYRAX: Generación de Datos")

def get_timestamp_filename(prefix: str, ext: str = "csv") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{prefix}_{timestamp}.{ext}"
    target_path = os.path.join(config.output_dir, base_name)
    if not os.path.exists(target_path):
        return base_name
    
    counter = 1
    while True:
        candidate = f"{prefix}_{timestamp}_{counter}.{ext}"
        if not os.path.exists(os.path.join(config.output_dir, candidate)):
            return candidate
        counter += 1

def get_valid_profiles() -> List[str]:
    """Retorna una lista de perfiles que no sean marcadores de posición (placeholders)."""
    valid = []
    for p_name, p_data in config.credentials.items():
        token = str(p_data.get("token", ""))
        cid = str(p_data.get("company_id", ""))
        if not ("AQUÍ" in token or "REAL" in token or cid in ["1", "2", "3"]):
            valid.append(p_name)
    return valid

def print_summary_table(results: List[Dict[str, Any]]):
    """Muestra una hermosa tabla con el resultado detallado de la carga de órdenes."""
    if not results:
        return
    from rich.table import Table
    table = Table(title="📊 Resumen de Carga de Órdenes vía API", show_header=True, header_style="bold magenta")
    table.add_column("Tenant / Perfil", style="cyan")
    table.add_column("Orden #", style="white")
    table.add_column("Resultado", justify="center")
    table.add_column("Detalle / Error", style="yellow")
    for r in results:
        status_symbol = "[bold green]✅ Éxito[/bold green]" if r["success"] else "[bold red]❌ Falló[/bold red]"
        error_msg = r["error"] or "-"
        table.add_row(
            r.get("tenant", "Desconocido"),
            r["order_num"],
            status_symbol,
            error_msg
        )
    console.print("\n")
    console.print(table)
    console.print("\n")

def list_and_verify_profiles():
    console.print("\n[yellow]🔍 Cargando y verificando perfiles...[/yellow]")
    credentials_path = config.config_dir / "credentials.yaml"
    if credentials_path.exists():
        config.load_credentials(str(credentials_path))
        
    profiles = config.credentials
    if not profiles:
        console.print("[bold red]⚠️ No hay perfiles configurados en credentials.yaml.[/bold red]")
        return

    from rich.table import Table
    table = Table(title="📋 Perfiles en credentials.yaml", show_header=True, header_style="bold magenta")
    table.add_column("Perfil", style="cyan")
    table.add_column("Base URL", style="dim")
    table.add_column("CID", style="green")
    table.add_column("PID", style="yellow")
    table.add_column("Moneda", style="magenta")
    table.add_column("Estado de Salud", style="bold")

    for name, p_data in profiles.items():
        url = p_data.get("api_base_url") or config.get("api_base_url")
        token = p_data.get("token", "")
        cid = p_data.get("company_id", "N/A")
        pid = p_data.get("process_id", "N/A")
        currency = p_data.get("currency", "-")
        
        status = "[bold red]❌ Expirado (401)[/bold red]"
        if token:
            if "AQUÍ" in str(token) or "REAL" in str(token) or str(cid) in ["1", "2", "3"]:
                status = "[dim]Placeholder / Inactivo[/dim]"
            else:
                try:
                    exporter = APIExporter(url, token)
                    check_cid = exporter.get_company_id()
                    if check_cid:
                        status = "[bold green]✅ Conectado[/bold green]"
                    else:
                        status = "[bold red]❌ Expirado (401)[/bold red]"
                except Exception:
                    status = "[bold yellow]⚠️ Sin Conexión[/bold yellow]"
        else:
            status = "[dim]Sin Token[/dim]"
            
        table.add_row(name, url, str(cid), str(pid), str(currency), status)

    console.print(table)

def clean_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    # Si el usuario concatenó dos URLs por accidente
    if url.count("http") > 1:
        parts = url.split("http")
        url = "http" + parts[-1]
    return url.rstrip('/') + '/'

def add_or_edit_profile_flow():
    console.print("\n[bold green]➕ Agregar / Editar Perfil[/bold green]")
    profiles = config.credentials
    
    name = questionary.text(
        "Nombre del perfil (si ingresas uno existente lo editarás):",
        validate=lambda text: True if text.strip() else "El nombre no puede estar vacío"
    ).ask()
    if not name: return
    
    name = name.strip()
    existing_data = profiles.get(name, {})
    
    default_url = existing_data.get("api_base_url") or config.get("api_base_url") or "https://qa5-condor.omniorders.com/"
    url = questionary.text("URL Base de la API?", default=default_url).ask()
    if not url: return
    url = clean_url(url)
    
    token = questionary.password("Token API Bearer:", default=existing_data.get("token", "")).ask()
    if not token: return
    
    console.print("[yellow]🔍 Conectando con la API para validar e importar...[/yellow]")
    exporter = APIExporter(url, token)
    cid = exporter.get_company_id()
    
    if not cid:
        console.print("[bold red]❌ Error: No se pudo obtener el Company ID con el token ingresado.[/bold red]")
        proceed = questionary.confirm("¿Deseas continuar e ingresar los datos manualmente?", default=False).ask()
        if not proceed:
            return
        cid = questionary.text("Company ID (Manual):", default=str(existing_data.get("company_id", ""))).ask()
        pid = questionary.text("Process ID (Manual):", default=str(existing_data.get("process_id", ""))).ask()
    else:
        console.print(f"   ✅ Company ID Resuelto: [green]{cid}[/green]")
        procs = exporter.get_processes(cid)
        pid = "1"
        if procs:
            omnio_procs = [p for p in procs if str(p.get('service', {}).get('type') or p.get('service_type') or "").upper() == "INTEGRATION_OMNIO"]
            display_procs = omnio_procs if omnio_procs else procs
            
            if len(display_procs) == 1:
                pid = str(display_procs[0]['id'])
                p_title = display_procs[0].get('title') or display_procs[0].get('name') or "Sin título"
                console.print(f"   ✅ Process ID Resuelto: [green]{pid}[/green] ({p_title}) [Único canal INTEGRATION_OMNIO detectado]")
            else:
                choices = []
                for p in display_procs:
                    p_id = p.get('id')
                    p_title = p.get('title') or p.get('name') or "Sin título"
                    s_type = p.get('service', {}).get('type') or p.get('service_type') or "N/A"
                    choices.append(f"{p_id} - ({p_title}) - {s_type}")
                
                selected_p = questionary.select(
                    "Selecciona el canal correcto (Process ID):",
                    choices=choices
                ).ask()
                if not selected_p: return
                pid = selected_p.split(" - ")[0]
        else:
            console.print("[bold red]⚠️ No se pudieron obtener procesos automáticamente.[/bold red]")
            pid = questionary.text("Process ID (Manual):", default=str(existing_data.get("process_id", "1"))).ask()
            if not pid: return

    currency = questionary.text(
        "Moneda predeterminada del perfil (ej. USD, EUR - Opcional, presiona Enter para omitir):",
        default=existing_data.get("currency", "")
    ).ask()
    currency = currency.strip().upper() if currency else None
    
    if config.save_profile(name, token, cid, pid, api_base_url=url, currency=currency):
        console.print(f"\n[bold green]💾 Perfil '{name}' guardado correctamente en credentials.yaml.[/bold green]\n")
    else:
        console.print("\n[bold red]❌ Error al guardar el perfil.[/bold red]\n")

def delete_profile_flow():
    console.print("\n[bold red]❌ Eliminar Perfil[/bold red]")
    profiles = config.credentials
    if not profiles:
        console.print("[bold red]⚠️ No hay perfiles configurados para eliminar.[/bold red]")
        return
        
    choices = list(profiles.keys())
    profile_to_delete = questionary.select("Selecciona el perfil que deseas eliminar:", choices=choices).ask()
    if not profile_to_delete: return
    
    confirm = questionary.confirm(f"¿Estás seguro de que deseas eliminar permanentemente el perfil '{profile_to_delete}'?", default=False).ask()
    if confirm:
        if config.delete_profile(profile_to_delete):
            console.print(f"\n[bold green]🗑️ Perfil '{profile_to_delete}' eliminado con éxito.[/bold green]\n")
        else:
            console.print("\n[bold red]❌ Error al eliminar el perfil.[/bold red]\n")

def manage_profiles_menu():
    while True:
        console.print("\n[bold cyan]⚙️ GESTOR DE PERFILES (credentials.yaml)[/bold cyan]")
        choice = questionary.select(
            "¿Qué deseas hacer?",
            choices=[
                "📋 Listar y Verificar Perfiles",
                "➕ Agregar / Editar Perfil",
                "❌ Eliminar Perfil",
                "↩️ Volver"
            ]
        ).ask()

        if not choice or choice == "↩️ Volver":
            break

        if choice == "📋 Listar y Verificar Perfiles":
            list_and_verify_profiles()
        elif choice == "➕ Agregar / Editar Perfil":
            add_or_edit_profile_flow()
        elif choice == "❌ Eliminar Perfil":
            delete_profile_flow()

def inspect_resource_flow():
    console.print("\n[bold cyan]🔍 INSPECTOR DE RECURSOS EN OMNIO[/bold cyan]")
    
    credentials_path = config.config_dir / "credentials.yaml"
    if credentials_path.exists():
        config.load_credentials(str(credentials_path))
        
    profiles = config.credentials
    if not profiles:
        console.print("[bold red]⚠️ No hay perfiles configurados en credentials.yaml.[/bold red]")
        return
        
    valid_profiles = {}
    for name, p_data in profiles.items():
        token = p_data.get("token", "")
        cid = p_data.get("company_id")
        if token and "AQUÍ" not in str(token) and "REAL" not in str(token) and str(cid) not in ["1", "2", "3"]:
            valid_profiles[name] = p_data
            
    if not valid_profiles:
        console.print("[bold yellow]⚠️ No tienes perfiles con credenciales reales configurados en credentials.yaml.[/bold yellow]")
        return
        
    p_choice = questionary.select(
        "Selecciona el perfil/tenant a consultar:",
        choices=list(valid_profiles.keys())
    ).ask()
    if not p_choice: return
    
    profile_data = valid_profiles[p_choice]
    url = profile_data.get("api_base_url") or config.get("api_base_url")
    token = profile_data.get("token")
    
    resource_type = questionary.select(
        "Selecciona el tipo de recurso que deseas consultar:",
        choices=[
            "🛍️ Estado de Orden (Order)",
            "📝 Estado de Purchase Order (PO)",
            "🔄 Estado de Transferencia (Stock Transfer)",
            "📦 Estado de Producto (Catalog Product)",
            "📈 Estado de Inventario (Stock Level)",
            "🌐 Consumir cualquier Endpoint GET del Catálogo (OpenAPI 609 Catalog)"
        ]
    ).ask()
    if not resource_type: return

    exporter = APIExporter(url, token)
    cid = profile_data.get("company_id", "1")

    if "Catálogo" in resource_type:
        import json, os
        catalog_path = "data/condor_api_catalog.json"
        if not os.path.exists(catalog_path):
            console.print("[bold red]❌ No se encontró el archivo de catálogo data/condor_api_catalog.json[/bold red]")
            return
            
        with open(catalog_path) as f:
            catalog = json.load(f)
            
        get_eps = [f"{ep['method']} {ep['path']} - ({ep['summary']})" for ep in catalog if ep["method"] == "GET"]
        
        selected_ep = questionary.select(
            "Selecciona el Endpoint GET que deseas consumir:",
            choices=get_eps[:40]
        ).ask()
        if not selected_ep: return
        
        raw_path = selected_ep.split(" ")[1]
        
        # Si el path requiere un ID específico y contiene llaves {id}, solicitarlo
        if "{" in raw_path and "tenant_id" not in raw_path and "company_id" not in raw_path:
            param_name = raw_path.split("{")[1].split("}")[0]
            val = questionary.text(f"Ingresa el valor para {{{param_name}}}:").ask()
            if val:
                raw_path = raw_path.replace(f"{{{param_name}}}", val.strip())

        console.print(f"[yellow]⚙️ Consumiendo GET {raw_path} en {p_choice}...[/yellow]")
        res = exporter.get_any_endpoint(raw_path, company_id=cid)
        
        if res.get("success"):
            console.print(f"[bold green]✅ HTTP {res.get('status')} - Respuesta recibida con éxito:[/bold green]")
            import json
            pretty_json = json.dumps(res.get("data"), indent=2, ensure_ascii=False)
            if len(pretty_json) > 1500:
                console.print_json(pretty_json[:1500] + "\n... (respuesta truncada por longitud)")
            else:
                console.print_json(pretty_json)
        else:
            console.print(f"[bold red]❌ Error HTTP {res.get('status')}: {res.get('error')}[/bold red]")
        return
    
    from rich.panel import Panel
    from rich.table import Table
    from rich.columns import Columns

    if "Orden" in resource_type:
        order_num = questionary.text(
            "Ingresa el número de la orden a consultar (ej. ORD-...):",
            validate=lambda text: True if text.strip() else "El número de orden es requerido"
        ).ask()
        if not order_num: return
        order_num = order_num.strip()
        
        console.print(f"[yellow]🔍 Consultando orden '{order_num}' en {p_choice}...[/yellow]")
        order = exporter.get_order_details(order_num)
        
        if not order:
            console.print(f"[bold red]❌ Orden '{order_num}' no fue encontrada o el token no es válido.[/bold red]")
            return
            
        status = order.get("status", "desconocido").upper()
        status_color = "green" if status == "OPEN" else ("blue" if status == "SHIPPED" else "yellow")
        
        header_text = (
            f"[bold white]ID Interno:[/bold white] {order.get('id')}  |  "
            f"[bold white]Fecha:[/bold white] {order.get('order_date')}  |  "
            f"[bold white]Moneda:[/bold white] {order.get('currency')}  |  "
            f"[bold white]Total:[/bold white] [green]${order.get('total_price')}[/green]\n"
            f"[bold white]Estado General:[/bold white] [bold {status_color}]{status}[/bold {status_color}]"
        )
        console.print(Panel(header_text, title=f"📦 Detalles de Orden: {order.get('order_num')}", border_style="cyan"))
        
        cust = order.get("customer", {})
        cust_text = (
            f"[bold cyan]Nombre:[/bold cyan] {cust.get('customer_firstname', '')} {cust.get('customer_lastname', '')}\n"
            f"[bold cyan]Email:[/bold cyan] {cust.get('customer_email') or '-'}\n"
            f"[bold cyan]Teléfono:[/bold cyan] {cust.get('customer_phone') or '-'}\n"
            f"[bold cyan]Dirección:[/bold cyan] {cust.get('customer_address1', '')} {cust.get('customer_address2', '') or ''}\n"
            f"[bold cyan]Ciudad/Estado/Zip:[/bold cyan] {cust.get('customer_city', '')}, {cust.get('customer_state') or '-'}, {cust.get('customer_zip') or '-'}\n"
            f"[bold cyan]País:[/bold cyan] {cust.get('customer_country', 'US')}"
        )
        
        bill = order.get("customer_bill", {})
        bill_text = (
            f"[bold magenta]Nombre:[/bold magenta] {bill.get('customer_bill_firstname', '')} {bill.get('customer_bill_lastname', '')}\n"
            f"[bold magenta]Dirección:[/bold magenta] {bill.get('customer_bill_address1') or '-'}\n"
            f"[bold magenta]Ciudad/Zip:[/bold magenta] {bill.get('customer_bill_city') or '-'}, {bill.get('customer_bill_zip') or '-'}\n"
            f"[bold magenta]País:[/bold magenta] {bill.get('customer_bill_country') or '-'}"
        )
        
        console.print(Columns([
            Panel(cust_text, title="👤 Información de Despacho", border_style="dim"),
            Panel(bill_text, title="💳 Información de Facturación", border_style="dim")
        ]))
        
        items_table = Table(title="🛒 Productos en la Orden (Line Items)", show_header=True, header_style="bold yellow", expand=True)
        items_table.add_column("SKU", style="cyan")
        items_table.add_column("Descripción", style="white")
        items_table.add_column("Cantidad", justify="right", style="green")
        items_table.add_column("Precio Unitario", justify="right", style="magenta")
        
        for item in order.get("line_items", []):
            items_table.add_row(
                item.get("sku", "N/A"),
                item.get("description") or "Sin descripción",
                str(item.get("quantity", 0)),
                f"${item.get('sold_price', '0.00')}"
            )
        console.print(items_table)
        
        shipments = order.get("shipments", [])
        if shipments:
            ship_table = Table(title="🚢 Envíos / Shipments Asociados", show_header=True, header_style="bold blue", expand=True)
            ship_table.add_column("ID Envío", style="cyan")
            ship_table.add_column("Método", style="white")
            ship_table.add_column("Transportista", style="white")
            ship_table.add_column("Estado Envío", style="bold")
            ship_table.add_column("Tracking Number", style="green")
            
            for s in shipments:
                s_status = s.get("status", "N/A").upper()
                s_status_color = "red" if s_status == "BACKORDER" else ("green" if s_status == "SHIPPED" else "yellow")
                ship_table.add_row(
                    str(s.get("id")),
                    s.get("shipping", {}).get("ship_method") or "-",
                    s.get("shipping", {}).get("ship_carrier") or "-",
                    f"[bold {s_status_color}]{s_status}[/bold {s_status_color}]",
                    s.get("tracking_number") or "[Pendiente]"
                )
            console.print(ship_table)
        else:
            console.print("\n[dim]ℹ️ No hay despachos (shipments) creados para esta orden aún.[/dim]")
        console.print("\n")

    elif "Purchase Order" in resource_type or "Transferencia" in resource_type:
        is_trf = "Transferencia" in resource_type
        doc_label = "Transferencia" if is_trf else "PO"
        doc_num = questionary.text(
            f"Ingresa el número de la {doc_label} a consultar (ej. {'TRF' if is_trf else 'PO'}-...):",
            validate=lambda text: True if text.strip() else f"El número de {doc_label} es requerido"
        ).ask()
        if not doc_num: return
        doc_num = doc_num.strip()
        
        console.print(f"[yellow]🔍 Buscando {doc_label} '{doc_num}' en {p_choice}...[/yellow]")
        docs = exporter.get_transfers(100) if is_trf else exporter.get_purchase_orders(100)
        
        found_doc = None
        for d in docs:
            if d.get("po_num") == doc_num:
                found_doc = d
                break
                
        if not found_doc:
            console.print(f"[bold red]❌ {doc_label} '{doc_num}' no fue encontrada en los últimos 100 registros.[/bold red]")
            return
            
        status = found_doc.get("status", "desconocido").upper()
        status_color = "green" if status in ["CONFIRMED", "COMPLETED"] else "yellow"
        
        header_text = (
            f"[bold white]ID Interno:[/bold white] {found_doc.get('id')}  |  "
            f"[bold white]Fecha Documento:[/bold white] {found_doc.get('date_po')}  |  "
            f"[bold white]Total Valor:[/bold white] [green]${found_doc.get('total_price')}[/green]\n"
            f"[bold white]Estado General:[/bold white] [bold {status_color}]{status}[/bold {status_color}]"
        )
        console.print(Panel(header_text, title=f"📋 Detalles de {doc_label}: {found_doc.get('po_num')}", border_style="cyan"))
        
        shipments = found_doc.get("shipments") or []
        for index, shp in enumerate(shipments):
            shipment_number = shp.get("shipment_number", f"Envío #{index+1}")
            iloc = shp.get("iloc") or {}
            iloc_name = iloc.get("name") or f"ID: {shp.get('iloc_id')}"
            
            iloc_od = shp.get("ilocOD") or shp.get("iloc_od") or {}
            iloc_od_name = iloc_od.get("name") or (f"ID: {shp.get('iloc_id_od')}" if shp.get('iloc_id_od') else "N/A")
            
            shp_status = shp.get("status", "desconocido").upper()
            shp_status_color = "green" if shp_status in ["DELIVERED", "COMPLETED", "ROUTING"] else "yellow"
            
            shp_text = (
                f"[bold cyan]Número de Envío:[/bold cyan] {shipment_number}\n"
                f"[bold cyan]Costo de Envío:[/bold cyan] ${shp.get('shipping_cost')}\n"
                f"[bold cyan]Almacén Destino:[/bold cyan] {iloc_name}\n"
                f"[bold cyan]Almacén Origen (Transfer):[/bold cyan] {iloc_od_name}\n"
                f"[bold cyan]Estado Envío:[/bold cyan] [bold {shp_status_color}]{shp_status}[/bold {shp_status_color}]"
            )
            console.print(Panel(shp_text, title=f"🚢 Envío: {shipment_number}", border_style="dim"))
            
            shp_items_table = Table(show_header=True, header_style="bold yellow", expand=True)
            shp_items_table.add_column("SKU ID", style="magenta")
            shp_items_table.add_column("SKU Code", style="cyan")
            shp_items_table.add_column("Cantidad", justify="right", style="green")
            shp_items_table.add_column("Precio de Compra", justify="right", style="magenta")
            
            for item in shp.get("items", []):
                sku_info = item.get("sku") or {}
                sku_code = sku_info.get("sku") or f"ID: {item.get('sku_id')}"
                shp_items_table.add_row(
                    str(item.get("sku_id")),
                    sku_code,
                    str(item.get("quantity", 0)),
                    f"${item.get('buy_price', 0.0)}"
                )
            console.print(shp_items_table)
        console.print("\n")

    elif "Producto" in resource_type:
        sku = questionary.text(
            "Ingresa el SKU del producto a consultar:",
            validate=lambda text: True if text.strip() else "El SKU es requerido"
        ).ask()
        if not sku: return
        sku = sku.strip()
        
        console.print(f"[yellow]🔍 Buscando producto con SKU '{sku}' en {p_choice}...[/yellow]")
        prod = exporter.get_product_by_sku(sku)
        
        if not prod:
            console.print(f"[bold red]❌ Producto con SKU '{sku}' no fue encontrado en Omnio.[/bold red]")
            return
            
        brand = prod.get("brand") or {}
        brand_name = brand.get("name") or "-"
        
        prod_text = (
            f"[bold white]ID Interno:[/bold white] {prod.get('id')}\n"
            f"[bold white]Nombre:[/bold white] {prod.get('name')}\n"
            f"[bold white]Marca:[/bold white] {brand_name}\n"
            f"[bold white]Tipo de Producto:[/bold white] {prod.get('type_product')}\n"
            f"[bold white]Creado el:[/bold white] {prod.get('created_at')}"
        )
        console.print(Panel(prod_text, title=f"📦 Detalles de Producto (Catálogo)", border_style="cyan"))
        
        sku_table = Table(title="🔍 Variantes / SKUs del Producto", show_header=True, header_style="bold yellow", expand=True)
        sku_table.add_column("SKU ID", style="magenta")
        sku_table.add_column("SKU Code", style="cyan")
        sku_table.add_column("UPC", style="white")
        sku_table.add_column("Creado el", style="dim")
        
        skus_list = prod.get("skus") or []
        for s in skus_list:
            sku_table.add_row(
                str(s.get("id")),
                s.get("sku", "N/A"),
                s.get("upc") or "-",
                s.get("created_at", "-")
            )
        console.print(sku_table)
        console.print("\n")

    elif "Inventario" in resource_type:
        sku = questionary.text(
            "Ingresa el SKU del inventario a consultar (vacío para listar primeros 10):"
        ).ask()
        
        console.print(f"[yellow]🔍 Consultando niveles de inventario en {p_choice}...[/yellow]")
        inventories = exporter.get_inventories()
        
        if not inventories:
            console.print("[bold red]❌ No hay inventario registrado en este tenant.[/bold red]")
            return
            
        sku = sku.strip() if sku else ""
        
        if sku:
            filtered = [x for x in inventories if sku.lower() in x.get("sku", "").lower()]
            if not filtered:
                console.print(f"[bold red]❌ No se encontró inventario para el SKU '{sku}'.[/bold red]")
                return
            display_list = filtered
        else:
            display_list = inventories[:10]
            console.print(f"[dim]Mostrando primeros {len(display_list)} SKUs de inventario...[/dim]")
            
        inv_table = Table(title="📈 Niveles de Stock de Inventario por Ubicación", show_header=True, header_style="bold yellow", expand=True)
        inv_table.add_column("SKU ID", style="magenta")
        inv_table.add_column("SKU Code", style="cyan")
        inv_table.add_column("Ubicación", style="yellow")
        inv_table.add_column("Disponible", justify="right", style="green")
        inv_table.add_column("Físico (Good)", justify="right", style="green")
        inv_table.add_column("Reservado", justify="right", style="magenta")
        inv_table.add_column("Hold", justify="right", style="yellow")
        inv_table.add_column("Dañado (Hurt)", justify="right", style="red")
        
        for item in display_list:
            sku_id = str(item.get("sku_id") or "-")
            sku_code = item.get("sku", "N/A")
            quantities = item.get("quantities") or []
            if not quantities:
                inv_table.add_row(sku_id, sku_code, "Sin ubicación asignada", "0", "0", "0", "0", "0")
            else:
                for q in quantities:
                    iloc_info = q.get("iloc") or {}
                    iloc_name = iloc_info.get("name") or f"ID: {q.get('iloc_id')}"
                    inv_table.add_row(
                        sku_id,
                        sku_code,
                        iloc_name,
                        str(q.get("qty_available", 0)),
                        str(q.get("qty_good", 0)),
                        str(q.get("qty_reserved", 0)),
                        str(q.get("qty_hold", 0)),
                        str(q.get("qty_hurt", 0))
                    )
        console.print(inv_table)
        console.print("\n")


def prompt_category() -> str:
    cat_choice = questionary.select(
        "¿Qué categoría de productos deseas generar?",
        choices=[
            "🎲 Aleatorio (Todas las categorías)",
            "🔌 Electrónica (Electronics)",
            "👕 Ropa y Calzado (Clothing)",
            "🍎 Alimentos (Food)",
            "📚 Libros (Books)",
            "🏡 Hogar y Jardín (Home & Garden)",
            "⚽ Deportes (Sports)",
            "🧸 Juguetes (Toys)",
            "🩺 Salud (Health)",
            "💄 Belleza (Beauty)",
            "🚗 Automotriz (Automotive)",
            "💎 Joyería y Accesorios (Jewelry & Accessories)",
            "🛠️ Herramientas y Ferretería (Tools & Hardware)"
        ]
    ).ask()
    if not cat_choice: return "all"
    
    cat_map = {
        "🎲 Aleatorio (Todas las categorías)": "all",
        "🔌 Electrónica (Electronics)": "Electronics",
        "👕 Ropa y Calzado (Clothing)": "Clothing",
        "🍎 Alimentos (Food)": "Food",
        "📚 Libros (Books)": "Books",
        "🏡 Hogar y Jardín (Home & Garden)": "Home & Garden",
        "⚽ Deportes (Sports)": "Sports",
        "🧸 Juguetes (Toys)": "Toys",
        "🩺 Salud (Health)": "Health",
        "💄 Belleza (Beauty)": "Beauty",
        "🚗 Automotriz (Automotive)": "Automotive",
        "💎 Joyería y Accesorios (Jewelry & Accessories)": "Jewelry & Accessories",
        "🛠️ Herramientas y Ferretería (Tools & Hardware)": "Tools & Hardware"
    }
    return cat_map.get(cat_choice, "all")

def prompt_brand(category: str = "all") -> str:
    brand_choice = questionary.select(
        "¿Deseas especificar una marca para los productos?",
        choices=[
            "🎲 Aleatorio / Todas las marcas",
            "📋 Seleccionar de una lista de marcas destacadas",
            "✍️ Ingresar marca manualmente por teclado"
        ]
    ).ask()
    
    if not brand_choice or "Aleatorio" in brand_choice:
        return "all"
        
    if "lista" in brand_choice or "marcas destacadas" in brand_choice:
        from src.utils.data_pool import CATEGORY_BRAND_SUGGESTIONS
        default_list = ["JBL", "Sony", "Apple", "Samsung", "Bose", "Nike", "Adidas", "Logitech", "Philips", "Puma"]
        suggestions = CATEGORY_BRAND_SUGGESTIONS.get(category, default_list)
        chosen = questionary.select(
            "Selecciona la marca:",
            choices=suggestions
        ).ask()
        return chosen.strip() if chosen else "all"
        
    elif "manualmente" in brand_choice:
        user_brand = questionary.text("Ingresa el nombre de la marca (ej. JBL, Bose, Samsung, Nike):").ask()
        return user_brand.strip() if user_brand else "all"
        
    return "all"

def prompt_language() -> str:
    lang_choice = questionary.select(
        "¿Idioma de los productos?",
        choices=[
            "Todos los idiomas (Multilingüe)",
            "Solo Español (es)",
            "Solo Inglés (en)"
        ]
    ).ask()
    if not lang_choice: return "all"
    
    lang_map = {
        "Todos los idiomas (Multilingüe)": "all",
        "Solo Español (es)": "es",
        "Solo Inglés (en)": "en"
    }
    return lang_map.get(lang_choice, "all")

def run_local_generator(action: str):
    if action == "🛍️ Órdenes de Venta (CSV)":
        qty = questionary.text("Cantidad?", "10").ask()
        if not qty: return
        
        sku_mode = questionary.select(
            "¿Tipo de orden?",
            choices=[
                "Multi-SKU (1-5 productos por orden)",
                "Single-SKU (1 solo producto por orden)"
            ]
        ).ask()
        
        sku_source = questionary.select(
            "¿Origen de los SKUs para las órdenes?",
            choices=[
                "🎲 Generar SKUs nuevos al azar",
                "📄 Extraer SKUs desde un archivo CSV existente",
                "✍️ Ingresar SKUs manualmente (separados por coma)"
            ]
        ).ask()
        
        extracted_skus = None
        if sku_source == "📄 Extraer SKUs desde un archivo CSV existente":
            csv_path = questionary.text("Ruta del archivo CSV (ej. data/orders_20260806_1452.csv):").ask()
            if csv_path:
                extracted_skus = extract_skus_from_csv(csv_path)
                if extracted_skus:
                    console.print(f"[bold green]✅ Se extrajeron {len(extracted_skus)} SKUs únicos del archivo.[/bold green]")
                else:
                    return
            else:
                return
        elif sku_source == "✍️ Ingresar SKUs manualmente (separados por coma)":
            raw_skus = questionary.text("Ingresa los SKUs separados por coma:").ask()
            if raw_skus:
                extracted_skus = [s.strip() for s in raw_skus.split(",") if s.strip()]

        date_range = questionary.select(
            "¿Rango de fechas?",
            choices=[
                "Solo hoy",
                "Últimos 30 días",
                "Último año (365 días)",
                "Últimos 2 años (730 días)"
            ]
        ).ask()
        
        days_map = {
            "Solo hoy": 0,
            "Últimos 30 días": 30,
            "Último año (365 días)": 365,
            "Últimos 2 años (730 días)": 730
        }
        days = days_map.get(date_range, 0)
        
        country_choice = questionary.select(
            "¿Tipo de alcance geográfico de las órdenes?",
            choices=[
                "📍 Local (Solo estados de EE.UU. / Domestic US)",
                "🌍 Global / Internacional (Fuera de EE.UU.: MX, CA, ES, GB, DE)",
                "🔀 Mixto / Ambos (Mayoría Local EE.UU. + Global Internacional)"
            ]
        ).ask()
        
        country_map = {
            "📍 Local (Solo estados de EE.UU. / Domestic US)": "US",
            "🌍 Global / Internacional (Fuera de EE.UU.: MX, CA, ES, GB, DE)": "INT",
            "🔀 Mixto / Ambos (Mayoría Local EE.UU. + Global Internacional)": "MIXED"
        }
        selected_country = country_map.get(country_choice, "US")

        if int(qty) > 2000:
            console.print(f"\n[bold cyan]⚡ Generando {qty} órdenes masivas con direcciones residenciales reales únicas (Dataset local + API en vivo)...[/bold cyan]\n")

        multi = True if "Multi-SKU" in sku_mode else False
        orders(count=int(qty), format="csv", multi_sku=multi, days_back=days, skus=extracted_skus, country=selected_country)
    elif action == "📦 Productos Estándar (CSV)":
        qty = questionary.text("Cantidad?", "50").ask()
        if not qty: return
        selected_cat = prompt_category()
        selected_brand = prompt_brand(selected_cat)
        selected_lang = prompt_language()
        search_target = selected_brand if selected_brand != "all" else selected_cat
        console.print(f"\n[bold yellow]🌐 Consultando APIs y catálogos en vivo vía Internet para productos de '{search_target}'... Por favor espera un momento ⏳[/bold yellow]\n")
        products(count=int(qty), lang=selected_lang, category=selected_cat, brand=selected_brand)
    elif action == "🏪 Productos Shopify (CSV)":
        qty = questionary.text("Cantidad?", "20").ask()
        if not qty: return
        selected_cat = prompt_category()
        selected_brand = prompt_brand(selected_cat)
        selected_lang = prompt_language()
        search_target = selected_brand if selected_brand != "all" else selected_cat
        console.print(f"\n[bold yellow]🌐 Consultando APIs y catálogos en vivo vía Internet para productos de '{search_target}'... Por favor espera un momento ⏳[/bold yellow]\n")
        shopify(count=int(qty), lang=selected_lang, category=selected_cat, brand=selected_brand)
    elif action == "📈 Inventario / Stock (CSV)":
        qty = questionary.text("Cantidad?", "100").ask()
        if not qty: return
        inventory(count=int(qty))
    elif action == "📝 Purchase Orders / PO (CSV)":
        qty = questionary.text("Cantidad?", "10").ask()
        if not qty: return
        po(count=int(qty))
    elif action == "🔄 Transferencias (CSV)":
        qty = questionary.text("Cantidad?", "10").ask()
        if not qty: return
        transfers(count=int(qty))
    elif action == "📦 Paquetes / Cajas (CSV)":
        qty = questionary.text("Cantidad?", "30").ask()
        if not qty: return
        packages(count=int(qty))
    elif action == "🚢 Productos Shipedge (Específicos)":
        qty = questionary.text("Cantidad?", "50").ask()
        if not qty: return
        selected_cat = prompt_category()
        selected_brand = prompt_brand(selected_cat)
        selected_lang = prompt_language()
        search_target = selected_brand if selected_brand != "all" else selected_cat
        console.print(f"\n[bold yellow]🌐 Consultando APIs y catálogos en vivo vía Internet para productos de '{search_target}'... Por favor espera un momento ⏳[/bold yellow]\n")
        shipedge(count=int(qty), lang=selected_lang, category=selected_cat, brand=selected_brand)
    elif action == "📠 Generar EDI (Standard XML)":
        qty = questionary.text("¿Cuántos archivos EDI XML?", "5").ask()
        if not qty: return
        
        items_choice = questionary.select(
            "¿Composición de la orden EDI?",
            choices=[
                "Una sola línea (1 producto)",
                "Multi-línea aleatorio (2-5 productos)"
            ]
        ).ask()
        if not items_choice: return
        
        sku_choice_val = questionary.select(
            "¿Qué SKU deseas usar para la orden EDI?",
            choices=[
                "Usar SKU específico (990394169)",
                "Generar nuevo SKU aleatorio"
            ]
        ).ask()
        if not sku_choice_val: return
        
        items_mode = "single" if "Una sola" in items_choice else "multi"
        sku_choice = "fixed" if "específico" in sku_choice_val else "random"
        
        edi(count=int(qty), items_mode=items_mode, sku_choice=sku_choice)
    elif action == "🏠 Generar CH (Cargo Hub XML)":
        qty = questionary.text("¿Cuántos archivos CH .neworders?", "5").ask()
        if not qty: return
        ch(count=int(qty))
    elif action == "📄 Generar Archivos PDF (Test)":
        qty = questionary.text("¿Cuántos archivos PDF?", "3").ask()
        if not qty: return
        size = questionary.text("¿Tamaño objetivo por PDF (MB)?", "1.0").ask()
        if not size: return
        pdf(count=int(qty), size_mb=float(size))

def local_files_menu():
    while True:
        console.print("\n[bold cyan]📄 GENERACIÓN DE ARCHIVOS LOCALES[/bold cyan]")
        choice = questionary.select(
            "Selecciona el tipo de archivo a generar:",
            choices=[
                "🛍️ Órdenes de Venta (CSV)",
                "📦 Productos Estándar (CSV)",
                "🏪 Productos Shopify (CSV)",
                "📈 Inventario / Stock (CSV)",
                "📝 Purchase Orders / PO (CSV)",
                "🔄 Transferencias (CSV)",
                "📦 Paquetes / Cajas (CSV)",
                "🚢 Productos Shipedge (Específicos)",
                "📠 Generar EDI (Standard XML)",
                "🏠 Generar CH (Cargo Hub XML)",
                "📄 Generar Archivos PDF (Test)",
                "↩️ Volver"
            ]
        ).ask()
        
        if not choice or choice == "↩️ Volver":
            break
            
        run_local_generator(choice)

def api_orders_upload_flow():
    mode = questionary.select(
        "¿Cómo deseas configurar la conexión?",
        choices=[
            "Usar archivo de perfiles (Multi-compañía)",
            "Importar desde archivo .txt (Estilo Octane)",
            "Configuración manual (Una sola compañía)"
        ]
    ).ask()
    
    if not mode: return
    qty = questionary.text("¿Cuántas órdenes cargar?", default="5").ask()
    if not qty: return
    count = int(qty)
    
    if mode == "Configuración manual (Una sola compañía)":
        url = questionary.text("URL Base de la API?", default="https://qa5-condor.omniorders.com/").ask()
        token = questionary.password("Token API?").ask()
        if not all([url, token]): return
        url = clean_url(url)
        
        exporter = APIExporter(url, token)
        console.print("[yellow]🔍 Detectando Company ID...[/yellow]")
        auto_cid = exporter.get_company_id()
        
        cid = questionary.text("Company ID?", default=auto_cid or "").ask()
        if not cid: return
        
        console.print("[yellow]🔍 Obteniendo listado de procesos...[/yellow]")
        procs = exporter.get_processes(cid)
        
        if procs:
            omnio_procs = [p for p in procs if str(p.get('service', {}).get('type') or p.get('service_type') or "").upper() == "INTEGRATION_OMNIO"]
            display_procs = omnio_procs if omnio_procs else procs
            
            choices = []
            for p in display_procs:
                p_id = p.get('id')
                p_title = p.get('title') or p.get('name') or "Sin título"
                s_type = p.get('service', {}).get('type') or p.get('service_type') or "N/A"
                choices.append(f"{p_id} - ({p_title}) - {s_type}")
            
            selected_p = questionary.select("Selecciona el proceso (Correcto):", choices=choices).ask()
            if not selected_p: return
            pid = selected_p.split(" - ")[0]
        else:
            console.print("[bold red]⚠️ No se pudieron obtener procesos automáticamente.[/bold red]")
            pid = questionary.text("Ingresar Process ID manualmente:").ask()
            if not pid: return

        save_opt = questionary.confirm("¿Deseas guardar estos datos en credentials.yaml para uso futuro?", default=True).ask()
        if save_opt:
            default_pname = f"Tenant_CID_{cid}"
            pname = questionary.text("Nombre para el perfil:", default=default_pname).ask()
            if pname and pname.strip():
                pname = pname.strip()
                if config.save_profile(pname, token, cid, pid, api_base_url=url):
                    console.print(f"[bold green]💾 Perfil '{pname}' guardado exitosamente en credentials.yaml[/bold green]\n")
            
        orders(count=count, format="api", token=token, company_id=cid, process_id=pid, api_url=url)
    elif mode == "Importar desde archivo .txt (Estilo Octane)":
        path = questionary.text("Ruta del archivo .txt?", default="config/tenants_import.txt").ask()
        if not path: return
        
        imported = TenantImporter.load_from_file(path)
        if not imported:
            console.print(f"[bold red]❌ No se encontraron tenants en {path}[/bold red]")
            return
        
        console.print(f"\n[bold green]📂 {len(imported)} Tenants detectados.[/bold green]")
        
        choices = [t['name'] for t in imported]
        selected_names = questionary.checkbox(
            "Selecciona los que deseas importar para la carga:", 
            choices=choices,
            validate=lambda secs: True if len(secs) > 0 else "Debes seleccionar al menos un tenant (usa Barra Espaciadora para marcar, luego Enter)"
        ).ask()
        if not selected_names:
            console.print("\n[bold yellow]⚠️ No seleccionaste ningún tenant. Operación cancelada.[/bold yellow]\n")
            return
        
        target_tenants = [t for t in imported if t['name'] in selected_names]
        
        final_profiles = []
        console.print("\n[bold yellow]🔍 Resolviendo Company/Process IDs automáticamente...[/bold yellow]")
        
        for t in target_tenants:
            exporter = APIExporter(config.get("api_base_url"), t['token'])
            cid = exporter.get_company_id()
            pid = "1" # Fallback
            
            if cid:
                procs = exporter.get_processes(cid)
                if procs:
                    omnio_procs = [p for p in procs if str(p.get('service', {}).get('type') or p.get('service_type') or "").upper() == "INTEGRATION_OMNIO"]
                    display_procs = omnio_procs if omnio_procs else procs
                    
                    if len(display_procs) == 1:
                        pid = str(display_procs[0]['id'])
                        p_title = display_procs[0].get('title') or display_procs[0].get('name') or "Sin título"
                        console.print(f"   ✅ {t['name']} -> CID: {cid}, PID: {pid} ({p_title}) [Único canal INTEGRATION_OMNIO detectado]")
                    else:
                        console.print(f"\n[cyan]⚙️ Se encontraron múltiples procesos/canales para {t['name']} (CID: {cid}):[/cyan]")
                        choices = []
                        for p in display_procs:
                            p_id = p.get('id')
                            p_title = p.get('title') or p.get('name') or "Sin título"
                            s_type = p.get('service', {}).get('type') or p.get('service_type') or "N/A"
                            choices.append(f"{p_id} - ({p_title}) - {s_type}")
                        
                        selected_p = questionary.select(
                            f"Selecciona el canal correcto para {t['name']}:", 
                            choices=choices
                        ).ask()
                        if not selected_p: 
                            console.print(f"   ⚠️ Saltando {t['name']}: Selección de proceso cancelada.")
                            continue
                        pid = selected_p.split(" - ")[0]
                        console.print(f"   ✅ {t['name']} -> CID: {cid}, PID: {pid} (Seleccionado)")
            
            if cid:
                final_profiles.append({
                    "name": t['name'],
                    "token": t['token'],
                    "company_id": cid,
                    "process_id": pid
                })
                config.save_profile(t['name'], t['token'], cid, pid)
            else:
                console.print(f"   ⚠️ Saltando {t['name']}: No se pudo obtener Company ID (¿Token expirado?)")
        
        if final_profiles:
            console.print("[bold green]💾 Perfiles guardados en credentials.yaml para uso futuro.[/bold green]")
            
            gen = OrderGenerator()
            data = gen.generate_batch(count)
            
            all_results = []
            for prof in final_profiles:
                console.print(f"\n[bold cyan]🚀 Subiendo a: {prof['name']}...[/bold cyan]")
                exporter = APIExporter(config.get("api_base_url"), prof['token'])
                
                tenant_skus = exporter.get_tenant_skus(prof['company_id'])
                if tenant_skus:
                    console.print(f"   ℹ️ Detectados {len(tenant_skus)} SKUs activos en el tenant. Generando órdenes con SKUs reales...")
                    tenant_data = gen.generate_batch(count, skus=tenant_skus)
                else:
                    tenant_data = data
                    
                results = exporter.upload_orders(tenant_data, prof['company_id'], prof['process_id'], max_workers=5)
                for r in results:
                    r["tenant"] = prof["name"]
                all_results.extend(results)
                console.print(f"[bold green]✅ Carga para {prof['name']} finalizada.[/bold green]")
            
            print_summary_table(all_results)
    else:
        valid_choices = get_valid_profiles()
        if not valid_choices:
            console.print("\n[bold yellow]⚠️ No tienes perfiles con credenciales reales configurados en credentials.yaml.[/bold yellow]")
            console.print("[dim]Usa la opción 'Importar desde archivo .txt' para autodetectar y guardar credenciales reales.[/dim]\n")
            return
        
        profs = questionary.checkbox(
            "Selecciona los perfiles para la carga masiva (Espacio para marcar):", 
            choices=valid_choices,
            validate=lambda secs: True if len(secs) > 0 else "Debes seleccionar al menos un perfil (usa Barra Espaciadora para marcar, luego Enter)"
        ).ask()
        if not profs:
            console.print("\n[bold yellow]⚠️ No seleccionaste ningún perfil. Operación cancelada.[/bold yellow]\n")
            return
        orders(count=count, format="api", profiles=profs)

def api_products_upload_flow():
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles con credenciales reales configurados en credentials.yaml.[/bold yellow]")
        console.print("[dim]Usa la opción 'Importar desde archivo .txt' para autodetectar y guardar credenciales reales.[/dim]\n")
        return
        
    qty = questionary.text("¿Cuántos productos deseas crear?", default="10").ask()
    if not qty: return
    count = int(qty)
    
    cat_choice = questionary.select(
        "¿Qué categoría de productos deseas generar para subir?",
        choices=[
            "🎲 Aleatorio (Todas las categorías)",
            "🔌 Electrónica (Electronics)",
            "👕 Ropa y Calzado (Clothing)",
            "🍎 Alimentos (Food)",
            "📚 Libros (Books)",
            "🏡 Hogar y Jardín (Home & Garden)",
            "⚽ Deportes (Sports)",
            "🧸 Juguetes (Toys)",
            "🩺 Salud (Health)",
            "💄 Belleza (Beauty)",
            "🚗 Automotriz (Automotive)",
            "💎 Joyería y Accesorios (Jewelry & Accessories)",
            "🛠️ Herramientas y Ferretería (Tools & Hardware)"
        ]
    ).ask()
    if not cat_choice: return
    
    cat_map = {
        "🎲 Aleatorio (Todas las categorías)": "all",
        "🔌 Electrónica (Electronics)": "Electronics",
        "👕 Ropa y Calzado (Clothing)": "Clothing",
        "🍎 Alimentos (Food)": "Food",
        "📚 Libros (Books)": "Books",
        "🏡 Hogar y Jardín (Home & Garden)": "Home & Garden",
        "⚽ Deportes (Sports)": "Sports",
        "🧸 Juguetes (Toys)": "Toys",
        "🩺 Salud (Health)": "Health",
        "💄 Belleza (Beauty)": "Beauty",
        "🚗 Automotriz (Automotive)": "Automotive",
        "💎 Joyería y Accesorios (Jewelry & Accessories)": "Jewelry & Accessories",
        "🛠️ Herramientas y Ferretería (Tools & Hardware)": "Tools & Hardware"
    }
    selected_cat = cat_map.get(cat_choice, "all")
    
    profs = questionary.checkbox(
        "Selecciona los perfiles para subir productos (Espacio para marcar):", 
        choices=valid_choices,
        validate=lambda secs: True if len(secs) > 0 else "Debes seleccionar al menos un perfil (usa Barra Espaciadora para marcar, luego Enter)"
    ).ask()
    if not profs:
        console.print("\n[bold yellow]⚠️ No seleccionaste ningún perfil. Operación cancelada.[/bold yellow]\n")
        return
        
    gen = ProductGenerator(category=selected_cat)
    products_data = gen.generate_batch(count)
    
    all_results = []
    for prof_name in profs:
        prof = config.get_profile(prof_name)
        if not prof: continue
        console.print(f"\n[bold cyan]🚀 Subiendo productos a: {prof_name}...[/bold cyan]")
        exporter = APIExporter(config.get("api_base_url"), prof['token'])
        results = exporter.upload_products(products_data, max_workers=5)
        for r in results:
            r["tenant"] = prof_name
        all_results.extend(results)
        console.print(f"[bold green]✅ Carga de productos para {prof_name} finalizada.[/bold green]")
        
    # Imprimir tabla resumen
    from rich.table import Table
    table = Table(title="📊 Resumen de Carga de Productos vía API")
    table.add_column("Tenant / Perfil", style="cyan")
    table.add_column("SKU", style="magenta")
    table.add_column("Nombre de Producto", style="white")
    table.add_column("Resultado", style="green")
    table.add_column("Detalle / Error", style="red")
    
    for r in all_results:
        status = "✅ Éxito" if r["success"] else "❌ Falló"
        err = r["error"] or "-"
        table.add_row(r["tenant"], r["sku"], r["name"], status, err)
        
    console.print(table)

def api_stock_adjust_flow():
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles con credenciales reales configurados en credentials.yaml.[/bold yellow]")
        console.print("[dim]Usa la opción 'Importar desde archivo .txt' para autodetectar y guardar credenciales reales.[/dim]\n")
        return

    qty = questionary.text("¿Qué nivel de stock deseas asignar a todos tus SKUs?", default="1000").ask()
    if not qty: return
    target_qty = int(qty)

    profs = questionary.checkbox(
        "Selecciona los perfiles para ajustar stock (Espacio para marcar):", 
        choices=valid_choices,
        validate=lambda secs: True if len(secs) > 0 else "Debes seleccionar al menos un perfil (usa Barra Espaciadora para marcar, luego Enter)"
    ).ask()
    if not profs:
        console.print("\n[bold yellow]⚠️ No seleccionaste ningún perfil. Operación cancelada.[/bold yellow]\n")
        return

    all_results = []
    for prof_name in profs:
        prof = config.get_profile(prof_name)
        if not prof: continue
        console.print(f"\n[bold cyan]🚀 Consultando inventario actual en: {prof_name}...[/bold cyan]")
        exporter = APIExporter(config.get("api_base_url"), prof['token'])
        
        inventories = exporter.get_inventories()
        if not inventories:
            console.print(f"   ⚠️ No se encontraron SKUs en el tenant {prof_name} para ajustar stock (¿El tenant está vacío?).")
            all_results.append({
                "tenant": prof_name,
                "skus_count": 0,
                "qty": target_qty,
                "success": False,
                "error": "El tenant no tiene SKUs creados."
            })
            continue

        iloc_groups = {}
        seen_skus = set()
        for item in inventories:
            sku_id = item.get("sku_id")
            if not sku_id: continue
            
            if sku_id in seen_skus:
                continue
            seen_skus.add(sku_id)
            
            quantities = item.get("quantities") or []
            target_iloc = 1
            if quantities:
                for q in quantities:
                    iloc_id = q.get("iloc_id")
                    if iloc_id:
                        target_iloc = iloc_id
                        break
            
            if target_iloc not in iloc_groups:
                iloc_groups[target_iloc] = []
            iloc_groups[target_iloc].append(sku_id)

        adjustments = []
        total_skus = 0
        for iloc_id, sku_ids in iloc_groups.items():
            skus_payload = [{"sku_id": sid, "qty_good": target_qty} for sid in sku_ids]
            adjustments.append({
                "iloc_id": iloc_id,
                "skus": skus_payload
            })
            total_skus += len(sku_ids)

        if not adjustments:
            console.print("   ⚠️ No se pudieron estructurar ajustes válidos.")
            all_results.append({
                "tenant": prof_name,
                "skus_count": 0,
                "qty": target_qty,
                "success": False,
                "error": "Estructura de ajuste vacía."
            })
            continue

        console.print(f"   ⚙️ Enviando ajuste masivo para {total_skus} SKUs a la API...")
        res = exporter.update_inventories_stock(adjustments)
        
        all_results.append({
            "tenant": prof_name,
            "skus_count": total_skus,
            "qty": target_qty,
            "success": res["success"],
            "error": res["error"]
        })
        if res["success"]:
            adjusted_sku_names = [item.get("sku") for item in inventories if item.get("sku_id") in seen_skus and item.get("sku")]
            console.print(f"[bold green]✅ Ajuste de stock para {prof_name} completado con éxito.[/bold green]")
            console.print(f"   [cyan]📝 SKUs modificados ({len(adjusted_sku_names)}):[/cyan] [dim]{', '.join(adjusted_sku_names)}[/dim]")
        else:
            console.print(f"[bold red]❌ Error al ajustar stock en {prof_name}: {res['error']}[/bold red]")

    # Imprimir tabla resumen
    from rich.table import Table
    table = Table(title="📊 Resumen de Ajuste de Stock de Inventario vía API")
    table.add_column("Tenant / Perfil", style="cyan")
    table.add_column("SKUs Ajustados", style="magenta")
    table.add_column("Nivel de Stock", style="white")
    table.add_column("Resultado", style="green")
    table.add_column("Detalle / Error", style="red")

    for r in all_results:
        status = "✅ Éxito" if r["success"] else "❌ Falló"
        err = r["error"] or "-"
        table.add_row(r["tenant"], str(r["skus_count"]), str(r["qty"]), status, err)

    console.print(table)

def api_po_transfer_upload_flow():
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles con credenciales reales configurados en credentials.yaml.[/bold yellow]")
        console.print("[dim]Usa la opción 'Importar desde archivo .txt' para autodetectar y guardar credenciales reales.[/dim]\n")
        return

    doc_type = questionary.select(
        "Selecciona el tipo de documento a cargar:",
        choices=[
            "📝 Purchase Order (PO)",
            "🔄 Transferencia (Stock Transfer)"
        ]
    ).ask()
    if not doc_type: return
    is_transfer = "Transferencia" in doc_type

    qty = questionary.text("¿Cuántos registros deseas cargar?", default="1").ask()
    if not qty: return
    count = int(qty)

    profs = questionary.checkbox(
        "Selecciona los perfiles para la carga masiva (Espacio para marcar):", 
        choices=valid_choices,
        validate=lambda secs: True if len(secs) > 0 else "Debes seleccionar al menos un perfil (usa Barra Espaciadora para marcar, luego Enter)"
    ).ask()
    if not profs:
        console.print("\n[bold yellow]⚠️ No seleccionaste ningún perfil. Operación cancelada.[/bold yellow]\n")
        return

    all_results = []
    import random

    for prof_name in profs:
        prof = config.get_profile(prof_name)
        if not prof: continue
        console.print(f"\n[bold cyan]🚀 Consultando SKUs e ilocs activos en: {prof_name}...[/bold cyan]")
        exporter = APIExporter(config.get("api_base_url"), prof['token'])
        
        inventories = exporter.get_inventories()
        if not inventories:
            console.print(f"   ⚠️ No se encontraron SKUs activos en el tenant {prof_name}. Carga cancelada para este tenant.")
            all_results.append({
                "tenant": prof_name,
                "type": "Transfer" if is_transfer else "PO",
                "doc_num": "N/A",
                "success": False,
                "error": "El tenant no tiene SKUs creados."
            })
            continue

        sku_map = {}
        iloc_ids = set()
        
        for item in inventories:
            sku_id = item.get("sku_id")
            sku_name = item.get("sku")
            if sku_id and sku_name:
                sku_map[sku_id] = sku_name
                
            quantities = item.get("quantities") or []
            for q in quantities:
                iloc_id = q.get("iloc_id")
                if iloc_id:
                    iloc_ids.add(iloc_id)
        
        if not sku_map:
            console.print(f"   ⚠️ No se pudieron obtener SKUs con ID válido en el tenant {prof_name}.")
            all_results.append({
                "tenant": prof_name,
                "type": "Transfer" if is_transfer else "PO",
                "doc_num": "N/A",
                "success": False,
                "error": "No se encontraron IDs de SKU."
            })
            continue

        iloc_list = list(iloc_ids)
        if not iloc_list:
            iloc_list = [1]

        console.print(f"   ⚙️ Generando {count} {'Transferencias' if is_transfer else 'POs'} para {prof_name}...")
        
        for i in range(count):
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            rand_suffix = random.randint(100, 999)
            doc_num = f"{'TRF' if is_transfer else 'PO'}-{timestamp}-{rand_suffix}-{i}"
            
            valid_skus_for_doc = []
            for item in inventories:
                sku_id = item.get("sku_id")
                sku_name = item.get("sku")
                if not sku_id or not sku_name:
                    continue
                
                item_ilocs = []
                quantities = item.get("quantities") or []
                for q in quantities:
                    iloc_id = q.get("iloc_id")
                    if iloc_id:
                        item_ilocs.append(iloc_id)
                
                if is_transfer and not item_ilocs:
                    continue
                
                valid_skus_for_doc.append({
                    "sku_id": sku_id,
                    "sku": sku_name,
                    "ilocs": item_ilocs
                })

            if not valid_skus_for_doc:
                console.print(f"   ⚠️ No hay SKUs válidos listos para la carga en {prof_name}.")
                all_results.append({
                    "tenant": prof_name,
                    "type": "Transfer" if is_transfer else "PO",
                    "doc_num": doc_num,
                    "success": False,
                    "error": "No hay SKUs elegibles."
                })
                continue

            selected_items = random.sample(valid_skus_for_doc, min(len(valid_skus_for_doc), random.randint(1, 3)))
            
            first_item = selected_items[0]
            if is_transfer:
                source_iloc = first_item["ilocs"][0]
                selected_items = [x for x in selected_items if source_iloc in x["ilocs"]]
                
                other_ilocs = [x for x in iloc_list if x != source_iloc]
                if not other_ilocs:
                    console.print(f"   ⚠️ El tenant {prof_name} solo tiene 1 ubicación ({source_iloc}). No se puede transferir sin otra ubicación.")
                    all_results.append({
                        "tenant": prof_name,
                        "type": "Transfer",
                        "doc_num": doc_num,
                        "success": False,
                        "error": "Se requieren al menos 2 ubicaciones para transferir stock."
                    })
                    continue
                dest_iloc = other_ilocs[0]
            else:
                source_iloc = None
                dest_iloc = iloc_list[0]

            address_from = {
                "firstname": "Fulfillment",
                "lastname": "Source",
                "email": "source@example.com",
                "phone": "555-0100",
                "address1": "100 Warehouse Way",
                "country": "USA",
                "state": "FL",
                "city": "Miami",
                "zip": "33101"
            }
            address_to = {
                "firstname": "Fulfillment",
                "lastname": "Destination",
                "email": "destination@example.com",
                "phone": "555-0200",
                "address1": "200 Delivery Dr",
                "country": "USA",
                "state": "CA",
                "city": "Los Angeles",
                "zip": "90001"
            }

            items_payload = []
            total_price = 0.0
            for it in selected_items:
                qty_val = random.randint(10, 50)
                price_val = round(random.uniform(5.0, 30.0), 2)
                items_payload.append({
                    "sku_id": it["sku_id"],
                    "quantity": qty_val,
                    "price": price_val
                })
                total_price += qty_val * price_val
                
            payload = {
                "po_num": doc_num,
                "total_price": round(total_price, 2),
                "date_po": datetime.now().strftime("%Y-%m-%d"),
                "status_name": "confirmed",
                "shipments": [
                    {
                        "shipment_number": f"{doc_num}-S1",
                        "iloc_id": dest_iloc,
                        "iloc_id_od": source_iloc,
                        "shipped_date": None,
                        "shipping_cost": 0.0,
                        "from": address_from,
                        "to": address_to,
                        "items": items_payload
                    }
                ]
            }

            res = exporter.upload_purchase_order(payload, is_transfer=is_transfer)
            all_results.append({
                "tenant": prof_name,
                "type": "Transfer" if is_transfer else "PO",
                "doc_num": doc_num,
                "success": res["success"],
                "error": res["error"]
            })

    from rich.table import Table
    table = Table(title="📊 Resumen de Carga de POs / Transferencias vía API")
    table.add_column("Tenant / Perfil", style="cyan")
    table.add_column("Tipo", style="yellow")
    table.add_column("Documento #", style="magenta")
    table.add_column("Resultado", style="green")
    table.add_column("Detalle / Error", style="red")

    for r in all_results:
        status = "✅ Éxito" if r["success"] else "❌ Falló"
        err = r["error"] or "-"
        table.add_row(r["tenant"], r["type"], r["doc_num"], status, err)

    console.print(table)

def api_fulfill_shipment_flow():
    console.print("\n[bold cyan]🚢 DESPACHAR ENVÍOS (FULFILL SHIPMENTS) VÍA API[/bold cyan]")
    
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles con credenciales reales configurados en credentials.yaml.[/bold yellow]")
        return
        
    p_choice = questionary.select(
        "Selecciona el perfil/tenant para despachar envíos:",
        choices=valid_choices
    ).ask()
    if not p_choice: return
    
    profile_data = config.get_profile(p_choice)
    url = profile_data.get("api_base_url") or config.get("api_base_url")
    token = profile_data.get("token")
    exporter = APIExporter(url, token)
    
    mode = questionary.select(
        "¿Cómo deseas despachar los envíos?",
        choices=[
            "⚡ Despachar TODOS los envíos pendientes del tenant (Autodespacho Masivo)",
            "✍️ Ingresar IDs de envío manualmente (separados por comas)",
            "🎯 Despachar un solo envío por ID"
        ]
    ).ask()
    if not mode: return

    shipments_to_fulfill = []

    if "TODOS" in mode:
        console.print(f"[yellow]🔍 Buscando envíos pendientes de órdenes en {p_choice}...[/yellow]")
        open_shipments = exporter.get_all_open_shipments(cid)
        if not open_shipments:
            console.print("[bold yellow]⚠️ No se encontraron envíos pendientes en este tenant.[/bold yellow]")
            return
            
        console.print(f"[bold white]Se encontraron {len(open_shipments)} envíos pendientes para despachar.[/bold white]")
        confirm = questionary.confirm(f"¿Deseas despachar los {len(open_shipments)} envíos ahora?", default=True).ask()
        if not confirm: return
        
        for s in open_shipments:
            s_id = s.get("id")
            if s_id:
                shipments_to_fulfill.append(s_id)

    elif "comas" in mode:
        ids_str = questionary.text(
            "Ingresa los IDs numéricos de envío a despachar (ej. 101, 102, 103):",
            validate=lambda text: True if text.strip() else "Debes ingresar al menos un ID"
        ).ask()
        if not ids_str: return
        for raw_id in ids_str.split(","):
            raw_id = raw_id.strip()
            if raw_id.isdigit():
                shipments_to_fulfill.append(int(raw_id))

    else:
        shipment_id_str = questionary.text(
            "Ingresa el ID numérico del envío a despachar:",
            validate=lambda text: True if text.strip().isdigit() else "El ID del envío debe ser un número entero"
        ).ask()
        if not shipment_id_str: return
        shipments_to_fulfill.append(int(shipment_id_str.strip()))

    if not shipments_to_fulfill:
        console.print("[bold red]❌ No hay IDs de envío válidos para procesar.[/bold red]")
        return

    console.print(f"\n[bold yellow]⚙️ Procesando despacho de {len(shipments_to_fulfill)} envíos en {p_choice}...[/bold yellow]")
    
    success_count = 0
    fail_count = 0
    
    for sid in shipments_to_fulfill:
        tracking_number = f"TRK-{datetime.now().strftime('%Y%m%d%H%M')}-{random.randint(1000, 9999)}"
        res = exporter.fulfill_shipment(sid, tracking_number)
        if res.get("success"):
            success_count += 1
            console.print(f"  ✅ Envío #{sid} despachado (Tracking: {tracking_number})")
        else:
            fail_count += 1
            console.print(f"  ❌ Envío #{sid} falló: {res.get('error')}")

    console.print(f"\n[bold green]✅ Resumen de Despacho: {success_count} exitosos, {fail_count} fallidos.[/bold green]\n")

def api_cancel_order_flow():
    console.print("\n[bold cyan]❌ CANCELAR/ELIMINAR ORDEN VÍA API[/bold cyan]")
    
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles con credenciales reales configurados en credentials.yaml.[/bold yellow]")
        return
        
    p_choice = questionary.select(
        "Selecciona el perfil/tenant de la orden:",
        choices=valid_choices
    ).ask()
    if not p_choice: return
    
    order_num = questionary.text(
        "Ingresa el número de orden a cancelar (ej. ORD-...):",
        validate=lambda text: True if text.strip() else "El número de orden es requerido"
    ).ask()
    if not order_num: return
    order_num = order_num.strip()
    
    profile_data = config.get_profile(p_choice)
    url = profile_data.get("api_base_url") or config.get("api_base_url")
    token = profile_data.get("token")
    
    confirm = questionary.confirm(f"¿Estás seguro de que deseas cancelar la orden '{order_num}' en {p_choice}?", default=False).ask()
    if not confirm: return
    
    console.print(f"[yellow]⚙️ Consultando ID de orden para '{order_num}' en {p_choice}...[/yellow]")
    exporter = APIExporter(url, token)
    order_details = exporter.get_order_details(order_num)
    
    if not order_details:
        console.print(f"[bold red]❌ La orden '{order_num}' no existe o no pudo ser obtenida.[/bold red]")
        return
        
    order_id = order_details.get("id")
    if not order_id:
        console.print(f"[bold red]❌ No se pudo obtener el ID de base de datos de la orden '{order_num}'.[/bold red]")
        return
        
    console.print(f"[yellow]⚙️ Cancelando orden '{order_num}' (ID: {order_id}) en {p_choice}...[/yellow]")
    res = exporter.cancel_order(order_id)
    
    if res.get("success"):
        console.print(f"[bold green]✅ Orden '{order_num}' cambiada a estado CANCEL exitosamente.[/bold green]")
    else:
        console.print(f"[bold red]❌ Error al cambiar el estado de la orden: {res.get('error')}[/bold red]")

def api_clear_stock_flow():
    console.print("\n[bold cyan]🗑️ VACIAR / LIMPIAR STOCK DE INVENTARIO VÍA API[/bold cyan]")
    
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles con credenciales reales configurados en credentials.yaml.[/bold yellow]")
        return
        
    p_choice = questionary.select(
        "Selecciona el perfil/tenant para vaciar stock:",
        choices=valid_choices
    ).ask()
    if not p_choice: return
    
    profile_data = config.get_profile(p_choice)
    url = profile_data.get("api_base_url") or config.get("api_base_url")
    token = profile_data.get("token")
    
    exporter = APIExporter(url, token)
    
    console.print(f"[yellow]🔍 Consultando inventario actual en: {p_choice}...[/yellow]")
    inventories = exporter.get_inventories()
    if not inventories:
        console.print("[bold yellow]⚠️ No se encontró inventario activo en este tenant.[/bold yellow]")
        return
        
    iloc_groups = {}
    for inv in inventories:
        sku_id = inv.get("sku_id")
        quantities = inv.get("quantities") or []
        for q in quantities:
            iloc_id = q.get("iloc_id")
            if iloc_id and sku_id:
                if iloc_id not in iloc_groups:
                    iloc_groups[iloc_id] = set()
                iloc_groups[iloc_id].add(sku_id)
                
    if not iloc_groups:
        console.print("[bold yellow]⚠️ No hay ubicaciones/SKUs con stock registrado para purgar.[/bold yellow]")
        return
        
    console.print(f"[bold white]Se detectaron {len(iloc_groups)} almacenes con productos registrados.[/bold white]")
    for iloc_id, skus_set in iloc_groups.items():
        console.print(f"   - Almacén ID {iloc_id}: {len(skus_set)} SKUs registrados")
        
    confirm = questionary.confirm(f"¿Deseas purgar TODO el stock de estos SKUs/Ubicaciones en {p_choice}? (Esto borrará físicamente el stock)", default=False).ask()
    if not confirm: return
    
    inventories_payload = []
    for iloc_id, skus_set in iloc_groups.items():
        skus_list = list(skus_set)
        for i in range(0, len(skus_list), 50):
            chunk = skus_list[i:i+50]
            inventories_payload.append({
                "iloc_id": int(iloc_id),
                "skus": chunk
            })
            
    console.print(f"[yellow]⚙️ Enviando solicitud de purga en {len(inventories_payload)} lotes...[/yellow]")
    
    success_count = 0
    fail_count = 0
    for i in range(0, len(inventories_payload), 10):
        sub_payload = inventories_payload[i:i+10]
        res = exporter.clear_inventories_stock(sub_payload)
        if res.get("success"):
            success_count += sum(len(x["skus"]) for x in sub_payload)
        else:
            fail_count += sum(len(x["skus"]) for x in sub_payload)
            console.print(f"[bold red]❌ Error en un lote de purga: {res.get('error')}[/bold red]")
            
    if success_count > 0:
        console.print(f"[bold green]✅ Purgado stock de {success_count} SKUs exitosamente.[/bold green]")
    if fail_count > 0:
        console.print(f"[bold red]⚠️ Falló la purga de {fail_count} SKUs.[/bold red]")

def api_metadata_upload_flow():
    console.print("\n[bold cyan]🏷️ CARGA DE METADATOS DINÁMICOS VÍA API[/bold cyan]")
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles reales configurados.[/bold yellow]")
        return
    p_choice = questionary.select("Selecciona el perfil para cargar metadatos:", choices=valid_choices).ask()
    if not p_choice: return
    
    key = questionary.text("Ingresa la clave del atributo/metadata (ej. color, weight_class, fragile):").ask()
    val = questionary.text("Ingresa el valor del atributo (ej. Red, Heavy, True):").ask()
    if not key or not val: return

    prof = config.credentials.get(p_choice, {})
    url = prof.get("api_base_url") or config.get("api_base_url")
    exporter = APIExporter(url, prof.get("token"))
    res = exporter.upload_tenant_metadata(prof.get("company_id"), key, val)
    if res.get("success"):
        console.print(f"[bold green]✅ Metadata '{key}: {val}' cargada con éxito en {p_choice}.[/bold green]")
    else:
        console.print(f"[bold red]❌ Error al cargar metadata: {res.get('error')}[/bold red]")

def api_sku_alt_upload_flow():
    console.print("\n[bold cyan]🔀 REGISTRO DE SKU ALTERNATIVO VÍA API[/bold cyan]")
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles reales configurados.[/bold yellow]")
        return
    p_choice = questionary.select("Selecciona el perfil para registrar SKU alternativo:", choices=valid_choices).ask()
    if not p_choice: return

    orig_sku = questionary.text("Ingresa el SKU original (ej. SKU-BASE-001):").ask()
    alt_sku = questionary.text("Ingresa el SKU alternativo/equivalente (ej. ALT-SKU-001):").ask()
    if not orig_sku or not alt_sku: return

    prof = config.credentials.get(p_choice, {})
    url = prof.get("api_base_url") or config.get("api_base_url")
    exporter = APIExporter(url, prof.get("token"))
    res = exporter.upload_sku_alternative(prof.get("company_id"), orig_sku, alt_sku)
    if res.get("success"):
        console.print(f"[bold green]✅ SKU alternativo '{alt_sku}' mapeado a '{orig_sku}' con éxito en {p_choice}.[/bold green]")
    else:
        console.print(f"[bold red]❌ Error al registrar SKU alternativo: {res.get('error')}[/bold red]")

def api_generation_menu():
    import json, os
    catalog_path = "data/condor_api_catalog.json"
    catalog_get_choices = []
    if os.path.exists(catalog_path):
        with open(catalog_path) as f:
            cat = json.load(f)
            for ep in cat:
                if ep.get("method") == "GET":
                    path = ep["path"]
                    summary = ep.get("summary", "")
                    
                    # Formato visual elegante con emojis temáticos según la entidad
                    if "order" in path: icon = "🛍️"
                    elif "address" in path: icon = "🏠"
                    elif "alert" in path: icon = "🔔"
                    elif "box" in path: icon = "📦"
                    elif "brand" in path: icon = "🏷️"
                    elif "carrier" in path: icon = "🚚"
                    elif "categor" in path: icon = "📂"
                    elif "contact" in path: icon = "📇"
                    elif "currenc" in path: icon = "💱"
                    elif "filter" in path: icon = "🔍"
                    elif "flow" in path: icon = "🔄"
                    elif "iloc" in path or "inventory" in path or "stock" in path: icon = "🏭"
                    elif "product" or "sku" in path: icon = "🏷️"
                    else: icon = "📡"
                    
                    catalog_get_choices.append(f"🔍 GET {path} — ({summary})")

    webhook_choices = [
        "⚡ WEBHOOK: orders/create — (Shopify Orden Creada)",
        "⚡ WEBHOOK: orders/paid — (Shopify Orden Pagada)",
        "⚡ WEBHOOK: orders/canceled — (Shopify Orden Cancelada)",
        "⚡ WEBHOOK: shipedge/orders/shipped — (WMS Shipedge Orden Enviada)",
        "⚡ WEBHOOK: shipedge/inventory/changes — (WMS Shipedge Ajuste Inventario)",
        "⚡ WEBHOOK: refunds/create — (Shopify Reembolso Creado)"
    ]

    base_choices = [
        "⚡ Prueba de Estrés y Rendimiento (Fase 1 Stress Test)",
        "🛍️ Cargar Órdenes vía API",
        "📦 Cargar Productos vía API",
        "📈 Ajustar Stock de Inventario vía API",
        "📝 Cargar POs o Transferencias vía API",
        "🚢 Despachar Envío (Fulfill Shipment) vía API",
        "🏷️ Cargar Metadatos Dinámicos vía API",
        "🔀 Cargar SKUs Alternativos vía API"
    ]

    all_menu_choices = base_choices + webhook_choices + catalog_get_choices + ["🗑️ Vaciar Stock de Inventario vía API", "↩️ Volver"]

    while True:
        console.print("\n[bold cyan]🛍️ GENERACIÓN Y CARGA VÍA API[/bold cyan]")
        choice = questionary.select(
            "Selecciona la acción por API:",
            choices=all_menu_choices
        ).ask()
        
        if not choice or choice == "↩️ Volver":
            break
            
        if choice == "⚡ Prueba de Estrés y Rendimiento (Fase 1 Stress Test)":
            api_stress_test_flow()
        elif choice == "🛍️ Cargar Órdenes vía API":
            api_orders_upload_flow()
        elif choice == "📦 Cargar Productos vía API":
            api_products_upload_flow()
        elif choice == "📈 Ajustar Stock de Inventario vía API":
            api_stock_adjust_flow()
        elif choice == "📝 Cargar POs o Transferencias vía API":
            api_po_transfer_upload_flow()
        elif choice == "🚢 Despachar Envío (Fulfill Shipment) vía API":
            api_fulfill_shipment_flow()
        elif choice == "🏷️ Cargar Metadatos Dinámicos vía API":
            api_metadata_upload_flow()
        elif choice == "🔀 Cargar SKUs Alternativos vía API":
            api_sku_alt_upload_flow()
        elif choice == "🗑️ Vaciar Stock de Inventario vía API":
            api_clear_stock_flow()
        elif choice.startswith("⚡ WEBHOOK:"):
            event_clean = choice.replace("⚡ WEBHOOK: ", "").split(" ")[0]
            _execute_direct_webhook(event_clean)
        elif choice.startswith("🔍 GET "):
            raw_path = choice.replace("🔍 GET ", "").split(" ")[0]
            _execute_direct_get(raw_path)

def _execute_direct_webhook(event_type: str):
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles reales configurados.[/bold yellow]")
        return
    p_choice = questionary.select("Selecciona el perfil/tenant destino:", choices=valid_choices).ask()
    if not p_choice: return

    order_num = questionary.text("Ingresa el número de orden objetivo (ej. ORD-20260827-001):", "ORD-20260827-001").ask()
    prof = config.credentials.get(p_choice, {})
    url = prof.get("api_base_url") or config.get("api_base_url")
    exporter = APIExporter(url, prof.get("token"))

    console.print(f"[yellow]⚙️ Enviando simulación de webhook '{event_type}'...[/yellow]")
    res = exporter.simulate_webhook_event(prof.get("company_id"), event_type=event_type, order_num=order_num, process_id=prof.get("process_id"))
    if res.get("success"):
        console.print(f"[bold green]✅ Webhook '{event_type}' procesado por la API con HTTP {res.get('status')}.[/bold green]")
    else:
        console.print(f"[bold red]❌ Error o rechazo de Webhook ({res.get('status')}): {res.get('error')}[/bold red]")

def _execute_direct_get(raw_path: str):
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles reales configurados.[/bold yellow]")
        return
    p_choice = questionary.select("Selecciona el perfil/tenant a consultar:", choices=valid_choices).ask()
    if not p_choice: return

    profile_data = config.get_profile(p_choice)
    url = profile_data.get("api_base_url") or config.get("api_base_url")
    token = profile_data.get("token")
    cid = profile_data.get("company_id", "1")

    import re
    # Encontrar todas las variables entre llaves {variable} en la URL
    params_to_replace = re.findall(r"\{([^}]+)\}", raw_path)
    for p_name in params_to_replace:
        if p_name not in ["tenant_id", "company_id", "tenant"]:
            val = questionary.text(f"🔑 Ingresa el ID/Valor para {{{p_name}}}:").ask()
            if val and val.strip():
                raw_path = raw_path.replace(f"{{{p_name}}}", val.strip())

    console.print(f"[yellow]⚙️ Consumiendo GET {raw_path} en {p_choice}...[/yellow]")
    exporter = APIExporter(url, token)
    res = exporter.get_any_endpoint(raw_path, company_id=cid)
    
    if res.get("success"):
        console.print(f"\n[bold green]✅ HTTP {res.get('status')} - Respuesta recibida con éxito de GET {raw_path}:[/bold green]")
        import json
        from rich.panel import Panel
        from rich.syntax import Syntax
        
        pretty_json = json.dumps(res.get("data"), indent=2, ensure_ascii=False)
        if len(pretty_json) > 2500:
            content_show = pretty_json[:2500] + "\n\n... ⚠️ (Respuesta truncada a 2500 caracteres por longitud)"
        else:
            content_show = pretty_json
            
        syntax = Syntax(content_show, "json", theme="ansi_dark", line_numbers=False)
        console.print(Panel(syntax, title=f"📦 JSON Response: {raw_path}", border_style="cyan", expand=False))
    else:
        console.print(f"[bold red]❌ Error HTTP {res.get('status')}: {res.get('error')}[/bold red]")
        
    questionary.press_any_key_to_continue("Presiona cualquier tecla para continuar...").ask()

def api_catalog_explorer_flow():
    console.print("\n[bold cyan]🌐 EXPLORADOR Y CONSUMIDOR DE ENDPOINTS (OPENAPI 609 CATALOG)[/bold cyan]")
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles reales configurados.[/bold yellow]")
        return
    p_choice = questionary.select("Selecciona el perfil/tenant destino:", choices=valid_choices).ask()
    if not p_choice: return

    profile_data = config.get_profile(p_choice)
    url = profile_data.get("api_base_url") or config.get("api_base_url")
    token = profile_data.get("token")
    cid = profile_data.get("company_id", "1")

    import json, os
    catalog_path = "data/condor_api_catalog.json"
    if not os.path.exists(catalog_path):
        console.print("[bold red]❌ No se encontró el catálogo en data/condor_api_catalog.json[/bold red]")
        return
        
    with open(catalog_path) as f:
        catalog = json.load(f)
        
    get_eps = [f"{ep['method']} {ep['path']} - ({ep['summary']})" for ep in catalog if ep["method"] == "GET"]
    
    selected_ep = questionary.select(
        "Selecciona la API GET que deseas consumir:",
        choices=get_eps[:50]
    ).ask()
    if not selected_ep: return
    
    raw_path = selected_ep.split(" ")[1]
    
    if "{" in raw_path and "tenant_id" not in raw_path and "company_id" not in raw_path:
        param_name = raw_path.split("{")[1].split("}")[0]
        val = questionary.text(f"Ingresa el valor para {{{param_name}}}:").ask()
        if val:
            raw_path = raw_path.replace(f"{{{param_name}}}", val.strip())

    console.print(f"[yellow]⚙️ Consumiendo GET {raw_path} en {p_choice}...[/yellow]")
    exporter = APIExporter(url, token)
    res = exporter.get_any_endpoint(raw_path, company_id=cid)
    
    if res.get("success"):
        console.print(f"[bold green]✅ HTTP {res.get('status')} - Respuesta recibida con éxito:[/bold green]")
        pretty_json = json.dumps(res.get("data"), indent=2, ensure_ascii=False)
        if len(pretty_json) > 1500:
            console.print_json(pretty_json[:1500] + "\n... (respuesta truncada por longitud)")
        else:
            console.print_json(pretty_json)
    else:
        console.print(f"[bold red]❌ Error HTTP {res.get('status')}: {res.get('error')}[/bold red]")

def api_webhook_simulator_flow():
    console.print("\n[bold cyan]🔄 FASE 2: SIMULADOR DE WEBHOOKS EXTERNOS[/bold cyan]")
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles reales configurados.[/bold yellow]")
        return
    p_choice = questionary.select("Selecciona el perfil/tenant destino:", choices=valid_choices).ask()
    if not p_choice: return

    event_type = questionary.select(
        "Selecciona el tipo de evento Webhook a simular:",
        choices=[
            "orders/create (Shopify Orden Creada)",
            "orders/paid (Shopify Orden Pagada)",
            "orders/canceled (Shopify Orden Cancelada)",
            "shipedge/orders/shipped (WMS Shipedge Orden Enviada)",
            "shipedge/inventory/changes (WMS Shipedge Ajuste Inventario)",
            "refunds/create (Shopify Reembolso Creado)"
        ]
    ).ask()
    if not event_type: return

    clean_event = event_type.split(" ")[0]
    order_num = questionary.text("Ingresa el número de orden objetivo (ej. ORD-20260827-001):", "ORD-20260827-001").ask()
    
    prof = config.credentials.get(p_choice, {})
    url = prof.get("api_base_url") or config.get("api_base_url")
    exporter = APIExporter(url, prof.get("token"))

    console.print(f"[yellow]⚙️ Enviando simulación de webhook '{clean_event}'...[/yellow]")
    res = exporter.simulate_webhook_event(prof.get("company_id"), event_type=clean_event, order_num=order_num, process_id=prof.get("process_id"))
    
    if res.get("success"):
        console.print(f"[bold green]✅ Webhook '{event_type}' procesado por la API con HTTP {res.get('status')}.[/bold green]")
    else:
        console.print(f"[bold red]❌ Error o rechazo de Webhook ({res.get('status')}): {res.get('error')}[/bold red]")

def api_rma_return_flow():
    console.print("\n[bold cyan]↩️ FASE 2: REGISTRO DE DEVOLUCIÓN / RMA VÍA API[/bold cyan]")
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles reales configurados.[/bold yellow]")
        return
    p_choice = questionary.select("Selecciona el perfil para registrar la devolución:", choices=valid_choices).ask()
    if not p_choice: return

    order_num = questionary.text("Número de Orden (ej. ORD-20260827-001):").ask()
    sku = questionary.text("SKU del producto a devolver (ej. SKU-DEFECT-01):").ask()
    qty = int(questionary.text("Cantidad a devolver?", "1").ask() or 1)
    reason = questionary.select("Motivo de la devolución:", choices=["Defective", "Customer Return", "Wrong Item", "Damaged in Transit"]).ask()
    
    if not order_num or not sku: return

    prof = config.credentials.get(p_choice, {})
    url = prof.get("api_base_url") or config.get("api_base_url")
    exporter = APIExporter(url, prof.get("token"))

    res = exporter.send_return_rma(prof.get("company_id"), order_num, sku, quantity=qty, reason=reason)
    if res.get("success"):
        console.print(f"[bold green]✅ RMA '{res.get('rma')}' registrado con éxito en la API.[/bold green]")
    else:
        console.print(f"[bold red]❌ Error al registrar RMA ({res.get('status')}): {res.get('error')}[/bold red]")

def api_stress_test_flow():
    console.print("\n[bold magenta]⚡ FASE 1: PRUEBA DE ESTRÉS Y RENDIMIENTO DE APIS[/bold magenta]")
    valid_choices = get_valid_profiles()
    if not valid_choices:
        console.print("\n[bold yellow]⚠️ No tienes perfiles reales configurados.[/bold yellow]")
        return
    p_choice = questionary.select("Selecciona el perfil para auditar:", choices=valid_choices).ask()
    if not p_choice: return
    
    n_req = int(questionary.text("¿Cuántas peticiones HTTP deseas enviar?", "30").ask() or 30)
    c_threads = int(questionary.text("¿Nivel de concurrencia (hilos en paralelo)?", "10").ask() or 10)
    
    stress_test(profile=p_choice, requests_count=n_req, concurrency=c_threads)

def interactive_menu(ctx: typer.Context):
    while True:
        console.print("[bold cyan]╔══════════════════════════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║            🌌 OMNISYRAX: Generación de Datos             ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════════════════════════════╝[/bold cyan]\n")
        
        action = questionary.select(
            "🔮 ¿Cuál es tu misión hoy?",
            choices=[
                "🛍️ Generar por API (Cargar a Omnio)",
                "📄 Generar Archivos locales (CSV/XML/PDF)",
                "🔍 Consultar Estado de Recursos (Órdenes, POs, SKUs, Stock)",
                "🔄 Flujo Completo (Sincronizado)",
                "📦 Generar Todo (Batch)",
                "⚙️ Gestionar Perfiles (credentials.yaml)",
                "ℹ️ Ver Ayuda",
                "🚪 Salir"
            ]
        ).ask()
        
        if not action or action == "🚪 Salir":
            break
 
        if action == "🛍️ Generar por API (Cargar a Omnio)":
            api_generation_menu()
        elif action == "📄 Generar Archivos locales (CSV/XML/PDF)":
            local_files_menu()
        elif action == "🔍 Consultar Estado de Recursos (Órdenes, POs, SKUs, Stock)":
            inspect_resource_flow()
        elif action == "🔄 Flujo Completo (Sincronizado)":
            generate_synchronized_flow()
        elif action == "📦 Generar Todo (Batch)":
            generate_batch_interactive()
        elif action == "⚙️ Gestionar Perfiles (credentials.yaml)":
            manage_profiles_menu()
        elif action == "ℹ️ Ver Ayuda":
            console.print(ctx.get_help())

class ISODatetime(datetime):
    def __str__(self):
        return self.isoformat(timespec='seconds')

def generate_synchronized_flow():
    import random
    from datetime import timedelta
    
    console.print("\n[bold cyan]🔄 CONFIGURACIÓN DE FLUJO COMPLETO[/bold cyan]")
    console.print("[dim]Este modo garantiza que todos los archivos compartan los mismos SKUs.[/dim]")
    console.print("[bold yellow]LÓGICA: 📦 PRODUCTOS (SKUs) ➔ 🛍️ ÓRDENES ➔ 📝 POs[/bold yellow]\n")
    
    q_products = int(questionary.text("¿Cuántos Productos base quieres generar?", "20").ask() or 0)
    
    # Pregunta A
    repeat_skus = questionary.select(
        "¿Quieres que los SKUs se repitan en diferentes órdenes?",
        choices=["Sí", "No"]
    ).ask()
    if not repeat_skus: return
    sku_repetition = (repeat_skus == "Sí")
    
    # Pregunta B
    composition_choice = questionary.select(
        "¿Cuántos SKUs diferentes puede tener una sola orden?",
        choices=["Una sola línea", "Multi-línea aleatorio 1-5"]
    ).ask()
    if not composition_choice: return
    multiline_enabled = (composition_choice == "Multi-línea aleatorio 1-5")
    
    # Pregunta C
    temporalidad_choice = questionary.select(
        "¿Cuál es el rango de fechas de las órdenes?",
        choices=["Solo el día de hoy", "Historial hacia atrás (Semanas/Meses/Años)"]
    ).ask()
    if not temporalidad_choice: return
    
    if temporalidad_choice == "Historial hacia atrás (Semanas/Meses/Años)":
        days_back_input = questionary.text(
            "¿Cuántos días de historial hacia atrás quieres generar? (Máximo 730 días / 2 años):",
            default="30"
        ).ask()
        if not days_back_input: return
        try:
            days = min(730, max(0, int(days_back_input)))
        except ValueError:
            days = 30
    else:
        days = 0
        
    q_orders = int(questionary.text("¿Cuántas Órdenes (usando esos productos)?", "10").ask() or 0)
    q_po = int(questionary.text("¿Cuántas POs (usando esos productos)?", "5").ask() or 0)
    
    cat_choice = questionary.select(
        "¿Qué categoría de productos deseas generar?",
        choices=[
            "🎲 Aleatorio (Todas las categorías)",
            "🔌 Electrónica (Electronics)",
            "👕 Ropa y Calzado (Clothing)",
            "🍎 Alimentos (Food)",
            "📚 Libros (Books)",
            "🏡 Hogar y Jardín (Home & Garden)",
            "⚽ Deportes (Sports)",
            "🧸 Juguetes (Toys)",
            "🩺 Salud (Health)",
            "💄 Belleza (Beauty)",
            "🚗 Automotriz (Automotive)",
            "💎 Joyería y Accesorios (Jewelry & Accessories)",
            "🛠️ Herramientas y Ferretería (Tools & Hardware)"
        ]
    ).ask()
    if not cat_choice: return
    
    cat_map = {
        "🎲 Aleatorio (Todas las categorías)": "all",
        "🔌 Electrónica (Electronics)": "Electronics",
        "👕 Ropa y Calzado (Clothing)": "Clothing",
        "🍎 Alimentos (Food)": "Food",
        "📚 Libros (Books)": "Books",
        "🏡 Hogar y Jardín (Home & Garden)": "Home & Garden",
        "⚽ Deportes (Sports)": "Sports",
        "🧸 Juguetes (Toys)": "Toys",
        "🩺 Salud (Health)": "Health",
        "💄 Belleza (Beauty)": "Beauty",
        "🚗 Automotriz (Automotive)": "Automotive",
        "💎 Joyería y Accesorios (Jewelry & Accessories)": "Jewelry & Accessories",
        "🛠️ Herramientas y Ferretería (Tools & Hardware)": "Tools & Hardware"
    }
    selected_cat = cat_map.get(cat_choice, "all")
    
    lang_choice = questionary.select(
        "¿Idioma de los productos?",
        choices=["Todos los idiomas (Multilingüe)", "Solo Español (es)", "Solo Inglés (en)"]
    ).ask()
    if not lang_choice: return
    
    lang_map = {"Todos los idiomas (Multilingüe)": "all", "Solo Español (es)": "es", "Solo Inglés (en)": "en"}
    selected_lang = lang_map.get(lang_choice, "all")
    
    upload_api = questionary.confirm("¿Deseas cargar las órdenes vía API al finalizar?", default=False).ask()
    
    skus = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    console.print("\n[bold cyan]🚀 Iniciando Flujo Sincronizado...[/bold cyan]")
    
    # 1. Productos
    data_p = []
    if q_products > 0:
        data_p = ProductGenerator(lang=selected_lang, category=selected_cat).generate_batch(q_products)
        
        # 1. Generación de SKUs Multilingües
        multilang_skus = {
            "ZH": ["zhong", "guo", "hua", "yu", "long", "feng", "ji", "xiang", "an", "kang", "ping", "sheng", "xian"],
            "GE": ["kart", "velo", "tbi", "lisi", "bat", "umi", "kuta", "isi", "mta", "vel"],
            "RU": ["rusk", "iy", "dmo", "gda", "mir", "svt", "vok", "zal", "rod", "ina"],
            "ES": ["esp", "ano", "lmu", "xal", "sol", "luz", "mar", "rio", "val", "oro"],
            "AR": ["abj", "dha", "wzh", "tyk", "lm", "nsq", "fkh", "nuj", "shm", "bhr"]
        }
        
        timestamp_random = datetime.now().strftime("%y%m%d")
        
        for idx, p in enumerate(data_p):
            lang_code = random.choice(list(multilang_skus.keys()))
            char_pool = multilang_skus[lang_code]
            words = "".join(random.sample(char_pool, k=min(2, len(char_pool))))
            cat_code = p.category[:3].upper()
            unique_suffix = f"{(idx + 1):03d}"
            random_tag = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=2))
            p.sku = f"SKU-{lang_code}-{cat_code}-{words}-{timestamp_random}-{unique_suffix}{random_tag}"
            
        skus = [p.sku for p in data_p]
        CSVExporter.export(data_p, f"products_{timestamp}.csv", config.output_dir)
        console.print(f"✅ {q_products} Productos generados ({selected_lang}, categoría: {selected_cat}).")

    # 2. Órdenes
    order_data = []
    if q_orders > 0 and skus:
        gen_o = OrderGenerator()
        gen_o.multi_sku = multiline_enabled
        
        # Copiar pool de SKUs para control de unicidad entre órdenes
        available_pool = list(skus)
        
        for _ in range(q_orders):
            num_items = random.randint(1, 5) if multiline_enabled else 1
            
            # Selección de SKUs para evitar duplicados en la misma orden
            if not sku_repetition:
                if len(available_pool) >= num_items:
                    order_skus = random.sample(available_pool, num_items)
                    for s in order_skus:
                        available_pool.remove(s)
                else:
                    needed = num_items - len(available_pool)
                    order_skus = list(available_pool)
                    available_pool.clear()
                    
                    # Rellenar con SKUs usados previamente asegurando no duplicarlos en la misma orden
                    remaining_pool = [s for s in skus if s not in order_skus]
                    if remaining_pool:
                        order_skus.extend(random.sample(remaining_pool, min(needed, len(remaining_pool))))
            else:
                order_skus = random.sample(skus, min(num_items, len(skus)))
            
            # Generar orden base con los SKUs elegidos
            gen_o.available_skus = order_skus
            order = gen_o.generate_single()
            
            # Aplicar temporalidad de 2026 (Año Actual)
            now = datetime.now()
            if days > 0:
                random_days = random.randint(0, days)
                order_date_base = now - timedelta(days=random_days)
            else:
                order_date_base = now
                
            # Randomizar la hora/minuto/segundo
            order_date = ISODatetime(
                order_date_base.year, order_date_base.month, order_date_base.day,
                random.randint(0, 23), random.randint(0, 59), random.randint(0, 59)
            )
            order.order_date = order_date
            
            # Formatear el número de orden con el nuevo prefijo
            order_prefix = order_date.strftime("%Y%m%d-%H%M%S")
            order.order_num = f"ORD-{order_prefix}-{random.randint(100, 999)}"
            
            order_data.append(order)
            
        CSVExporter.export(order_data, f"orders_{timestamp}.csv", config.output_dir)
        console.print(f"✅ {q_orders} Órdenes sincronizadas generadas.")

    # 3. POs
    if q_po > 0 and data_p:
        data_po = POGenerator().generate_batch(q_po, products=data_p)
        CSVExporter.export(data_po, f"po_{timestamp}.csv", config.output_dir)
        console.print(f"✅ {q_po} POs sincronizadas generadas.")

    if upload_api and order_data:
        console.print("\n[bold yellow]📡 Iniciando carga API multi-tenant...[/bold yellow]")
        valid_choices = get_valid_profiles()
        if not valid_choices:
            console.print("\n[bold yellow]⚠️ No tienes perfiles con credenciales reales configurados en credentials.yaml.[/bold yellow]")
            console.print("[dim]Usa la opción 'Importar desde archivo .txt' para autodetectar y guardar credenciales reales.[/dim]\n")
            return
            
        profs = questionary.checkbox(
            "Selecciona los perfiles para la carga masiva (Espacio para marcar):", 
            choices=valid_choices,
            validate=lambda secs: True if len(secs) > 0 else "Debes seleccionar al menos un perfil (usa Barra Espaciadora para marcar, luego Enter)"
        ).ask()
        if not profs:
            console.print("\n[bold yellow]⚠️ No seleccionaste ningún perfil. Operación cancelada.[/bold yellow]\n")
            return
            
        orders(count=0, format="api", profiles=profs, skus=[], multi_sku=True, _pregenerated_data=order_data)
        console.print("[bold green]✅ Carga API multi-tenant finalizada.[/bold green]")

    console.print("\n[bold green]🌟 Flujo completado con éxito.[/bold green]")

def generate_batch_interactive():
    console.print("[bold magenta]🚀 GENERACIÓN MASIVA (BATCH)[/bold magenta]\n")
    qty = int(questionary.text("¿Cuántos registros de CADA tipo deseas generar?", "20").ask() or 20)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # Generación simple independiente
    products(count=qty, output=f"batch_products_{timestamp}.csv")
    shopify(count=qty, output=f"batch_shopify_{timestamp}.csv")
    orders(count=qty, output=f"batch_orders_{timestamp}.csv")
    po(count=qty, output=f"batch_po_{timestamp}.csv")
    transfers(count=qty, output=f"batch_transfers_{timestamp}.csv")
    packages(count=qty, output=f"batch_packages_{timestamp}.csv")
    shipedge(count=qty, output=f"batch_shipedge_{timestamp}.csv")
    edi(count=5) # Default count for XML
    ch(count=5)
    pdf(count=3)
    
    console.print("\n[bold green]✅ Generación Batch completada.[/bold green]")

@app.command()
def shopify(count: int = 50, output: Optional[str] = None, lang: str = "all", category: str = "all", brand: str = "all"):
    """Genera productos en formato Shopify."""
    filename = output or get_timestamp_filename("shopify_products")
    console.print(f"[bold magenta]🛍️ OMNISYRAX: Generando {count} productos Shopify ({lang}, categoría: {category}, marca: {brand})...[/bold magenta]")
    data = ShopifyGenerator(lang=lang, category=category, brand=brand).generate_batch(count)
    CSVExporter.export(data, filename, config.output_dir)
    console.print(f"[bold green]✅ Shopify CSV listo en data/{filename}[/bold green]")

@app.command()
def inventory(count: int = 100, output: Optional[str] = None, skus: Optional[List[str]] = None):
    """Genera stock de inventario."""
    filename = output or get_timestamp_filename("inventory")
    console.print(f"[bold yellow]📦 OMNISYRAX: Generando {count} items de inventario...[/bold yellow]")
    data = InventoryGenerator().generate_batch(count, skus=skus)
    CSVExporter.export(data, filename, config.output_dir)
    console.print(f"[bold green]✅ Inventario CSV listo en data/{filename}[/bold green]")

@app.command()
def packages(count: int = 30, output: Optional[str] = None):
    """Genera paquetes y cajas."""
    filename = output or get_timestamp_filename("packages")
    console.print(f"[bold blue]📦 OMNISYRAX: Generando {count} paquetes...[/bold blue]")
    data = PackageGenerator().generate_batch(count)
    CSVExporter.export(data, filename, config.output_dir)
    console.print(f"[bold green]✅ Paquetes CSV listo en data/{filename}[/bold green]")

@app.command()
def generate_all(count: int = 20):
    """Genera todos los tipos de datos en un solo lote (No interactivo)."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    products(count=count, output=f"batch_products_{timestamp}.csv")
    shopify(count=count, output=f"batch_shopify_{timestamp}.csv")
    orders(count=count, output=f"batch_orders_{timestamp}.csv")
    po(count=count, output=f"batch_po_{timestamp}.csv")
    transfers(count=count, output=f"batch_transfers_{timestamp}.csv")
    packages(count=count, output=f"batch_packages_{timestamp}.csv")
    shipedge(count=count, output=f"batch_shipedge_{timestamp}.csv")
    edi(count=5)
    ch(count=5)
    pdf(count=3)
    console.print(f"\n[bold green]✅ Generación de {count} registros de cada tipo completada.[/bold green]")

# Comandos anteriores (reutilizados)
@app.command()
def products(count: int = 50, output: Optional[str] = None, lang: str = "all", category: str = "all", brand: str = "all"):
    """Genera productos estándar en formato CSV."""
    filename = output or get_timestamp_filename("products")
    data = ProductGenerator(lang=lang, category=category, brand=brand).generate_batch(count)
    CSVExporter.export(data, filename, config.output_dir)
    console.print(f"[bold green]✅ {count} Productos generados ({lang}, categoría: {category}, marca: {brand}) en data/{filename}[/bold green]")

@app.command()
def po(count: int = 10, output: Optional[str] = None, skus: Optional[List[str]] = None):
    """Genera órdenes de compra (Purchase Orders) en formato CSV."""
    filename = output or get_timestamp_filename("po")
    data = POGenerator().generate_batch(count, skus=skus)
    CSVExporter.export(data, filename, config.output_dir)
    console.print(f"[bold green]✅ {count} POs generadas en data/{filename}[/bold green]")

@app.command()
def transfers(count: int = 10, output: Optional[str] = None):
    """Genera transferencias de stock entre almacenes."""
    filename = output or get_timestamp_filename("transfers")
    data = TransferGenerator().generate_batch(count)
    CSVExporter.export(data, filename, config.output_dir)
    console.print(f"[bold green]✅ {count} Transferencias generadas en data/{filename}[/bold green]")

@app.command()
def shipedge(count: int = 50, output: Optional[str] = None, lang: str = "all", category: str = "all", brand: str = "all"):
    """Genera productos con formato específico de importación Shipedge."""
    filename = output or get_timestamp_filename("shipedge_products")
    console.print(f"[bold cyan]🚢 OMNISYRAX: Generando {count} productos Shipedge ({lang}, categoría: {category}, marca: {brand})...[/bold cyan]")
    data = ShipEdgeGenerator(lang=lang, category=category, brand=brand).generate_batch(count)
    CSVExporter.export(data, filename, config.output_dir)
    console.print(f"[bold green]✅ Shipedge CSV listo en data/{filename}[/bold green]")

@app.command()
def edi(
    count: int = 5,
    output_dir: str = "data/edi_xmls",
    items_mode: str = typer.Option("single", "--items-mode", help="Composición de la orden EDI: 'single' (un solo producto) o 'multi' (2-5 productos aleatorios)"),
    sku_choice: str = typer.Option("random", "--sku-choice", help="Origen del SKU: 'fixed' (990394169) o 'random' (nuevo aleatorio)")
):
    """Genera archivos XML en formato EDI Estándar."""
    console.print(f"[bold blue]📠 OMNISYRAX: Generando {count} archivos EDI XML...[/bold blue]")
    files = EDIGenerator().generate_batch(count, output_dir, items_mode=items_mode, sku_choice=sku_choice)
    for f in files:
        console.print(f"   📄 {f}")
    console.print(f"[bold green]✅ EDI XMLs listos en {output_dir}[/bold green]")

@app.command()
def ch(count: int = 5, output_dir: str = "data/ch_neworders"):
    """Genera archivos .neworders para Cargo Hub (Home Depot)."""
    console.print(f"[bold orange3]🏠 OMNISYRAX: Generando {count} archivos CH .neworders...[/bold orange3]")
    files = CHGenerator().generate_batch(count, output_dir)
    for f in files:
        console.print(f"   📄 {f}")
    console.print(f"[bold green]✅ CH .neworders listos en {output_dir}[/bold green]")

@app.command()
def pdf(count: int = 3, size_mb: float = 1.0, output_dir: str = "data/pdfs"):
    """Genera archivos PDF con un tamaño específico en MB."""
    console.print(f"[bold red]📄 OMNISYRAX: Generando {count} archivos PDF de {size_mb}MB...[/bold red]")
    files = PDFGenerator().generate_batch(count, size_mb, output_dir)
    for f in files:
        console.print(f"   📄 {f}")
    console.print(f"[bold green]✅ PDFs listos en {output_dir}[/bold green]")

@app.command()
def orders(
    count: int = 10,
    format: str = "csv",
    profiles: Optional[List[str]] = typer.Option(None, "--profile", help="Lista de perfiles para carga API"),
    token: Optional[str] = None,
    company_id: Optional[str] = None,
    process_id: Optional[str] = None,
    api_url: Optional[str] = None,
    multi_sku: bool = True,
    output: Optional[str] = None,
    skus: Optional[List[str]] = None,
    skus_file: Optional[str] = typer.Option(None, "--skus-file", help="Ruta a un archivo CSV para extraer SKUs"),
    days_back: int = 0,
    country: str = typer.Option("US", "--country", help="Ubicación de residencias: US, INT, MIXED"),
    _pregenerated_data: Optional[List[str]] = typer.Option(None, hidden=True)
):
    """Genera órdenes de venta (Sales Orders) en CSV o carga vía API con residencias reales garantizadas."""
    # Corregir parámetros de Typer si se llama como función normal
    if type(profiles).__name__ == "OptionInfo" or "OptionInfo" in str(type(profiles)):
        profiles = None
    if type(skus_file).__name__ == "OptionInfo" or "OptionInfo" in str(type(skus_file)):
        skus_file = None
    if type(country).__name__ == "OptionInfo" or "OptionInfo" in str(type(country)):
        country = "US"
    if type(_pregenerated_data).__name__ == "OptionInfo" or "OptionInfo" in str(type(_pregenerated_data)):
        _pregenerated_data = None

    if skus_file and not skus:
        extracted = extract_skus_from_csv(skus_file)
        if extracted:
            skus = extracted
            console.print(f"[bold green]✅ Se cargaron {len(skus)} SKUs únicos desde '{skus_file}'[/bold green]")

    if _pregenerated_data:
        data = _pregenerated_data
    else:
        gen = OrderGenerator(country_mode=country)
        data = gen.generate_batch(count, multi_sku=multi_sku, skus=skus, days_back=days_back, country_mode=country)
    if format == "csv":
        filename = output or get_timestamp_filename("orders")
        CSVExporter.export(data, filename, config.output_dir)
        console.print(f"[bold green]✅ {count} Órdenes generadas con residencias reales ({country}) en data/{filename}[/bold green]")
    elif format == "api":
        # Lógica de carga API (Soporta múltiples perfiles)
        target_profiles = []
        
        if profiles:
            for p_name in profiles:
                p_data = config.get_profile(p_name)
                if p_data:
                    target_profiles.append({
                        "name": p_name,
                        "token": p_data.get("token"),
                        "company_id": p_data.get("company_id"),
                        "process_id": p_data.get("process_id"),
                        "currency": p_data.get("currency"),
                        "api_url": p_data.get("api_base_url") or api_url
                    })
        elif token and company_id and process_id:
            target_profiles.append({
                "name": "Manual",
                "token": token,
                "company_id": company_id,
                "process_id": process_id,
                "currency": None,
                "api_url": api_url
            })

        if not target_profiles:
            console.print("[bold red]❌ No se especificaron perfiles válidos para la carga API.[/bold red]")
            return

        all_results = []
        for prof in target_profiles:
            console.print(f"\n[bold cyan]🚀 Subiendo a perfil: {prof['name']}...[/bold cyan]")
            
            # Validar si son placeholders
            if "AQUÍ" in str(prof['token']) or "REAL" in str(prof['token']) or str(prof['company_id']) in ["1", "2", "3"]:
                console.print(f"[bold yellow]⚠️ Saltando {prof['name']}: No tiene los datos reales configurados en credentials.yaml[/bold yellow]")
                continue

            base_url = prof.get("api_url") or config.get("api_base_url")
            exporter = APIExporter(base_url, prof['token'])
            
            # Intentar obtener SKUs reales del tenant para evitar errores 422
            tenant_skus = exporter.get_tenant_skus(prof['company_id'])
            if tenant_skus and not _pregenerated_data:
                console.print(f"   ℹ️ Detectados {len(tenant_skus)} SKUs activos en el tenant. Regenerando órdenes para este tenant con SKUs reales...")
                gen = OrderGenerator()
                tenant_data = gen.generate_batch(count, multi_sku=multi_sku, skus=tenant_skus, days_back=days_back)
            else:
                tenant_data = data
                
            results = exporter.upload_orders(
                tenant_data, 
                prof['company_id'], 
                prof['process_id'], 
                max_workers=5,
                forced_currency=prof.get('currency')
            )
            for r in results:
                r["tenant"] = prof["name"]
            all_results.extend(results)
            console.print(f"[bold green]✅ Carga para {prof['name']} finalizada.[/bold green]")

        # Imprimir tabla resumen
        print_summary_table(all_results)

@app.command()
def qa_api(
    profile: str = typer.Option("default", "--profile", help="Nombre del perfil en credentials.yaml para ejecutar QA")
):
    """Ejecuta la Suite de Pruebas de QA de APIs validando conectividad, idempotencia y respuestas HTTP."""
    prof = config.credentials.get(profile, {})
    url = prof.get("api_base_url") or config.get("api_base_url")
    token = prof.get("token")
    cid = prof.get("company_id")
    pid = prof.get("process_id")

    if not token or "AQUÍ" in str(token):
        console.print(f"[bold red]❌ El perfil '{profile}' no tiene credenciales configuradas.[/bold red]")
        return

    console.print(f"\n[bold cyan]🧪 Ejecutando Suite de QA de APIs para perfil '{profile}' ({url})...[/bold cyan]")
    exporter = APIExporter(url, token)
    res = exporter.run_qa_api_suite(cid, pid)

    table = Table(title=f"Resultados de QA API - Perfil {profile}")
    table.add_column("Prueba", style="cyan")
    table.add_column("Código HTTP", justify="center")
    table.add_column("Resultado", justify="center")

    for d in res["details"]:
        status_str = "[bold green]✅ PASS[/bold green]" if d["passed"] else "[bold red]❌ FAIL[/bold red]"
        table.add_row(d["test"], str(d["code"]), status_str)

    console.print(table)
    console.print(f"[bold green]Pruebas Exitosas: {res['passed']}[/bold green] | [bold red]Fallidas: {res['failed']}[/bold red]\n")

@app.command()
def stress_test(
    profile: str = typer.Option("default", "--profile", help="Nombre del perfil en credentials.yaml"),
    requests_count: int = typer.Option(50, "--requests", "-n", help="Número total de peticiones HTTP a enviar"),
    concurrency: int = typer.Option(10, "--concurrency", "-c", help="Número de hilos/peticiones concurrentes"),
    target_path: str = typer.Option("/api/1.0/tenants/{tenant_id}/orders", "--path", help="Endpoint a auditar")
):
    """Fase 1: Ejecuta una prueba de estrés y carga sobre la API de Condor reportando latencias y RPS."""
    if type(profile).__name__ == "OptionInfo" or "OptionInfo" in str(type(profile)):
        profile = "default"
    if type(requests_count).__name__ == "OptionInfo" or "OptionInfo" in str(type(requests_count)):
        requests_count = 50
    if type(concurrency).__name__ == "OptionInfo" or "OptionInfo" in str(type(concurrency)):
        concurrency = 10
    if type(target_path).__name__ == "OptionInfo" or "OptionInfo" in str(type(target_path)):
        target_path = "/api/1.0/tenants/{tenant_id}/orders"

    prof = config.credentials.get(profile, {})
    url = prof.get("api_base_url") or config.get("api_base_url")
    token = prof.get("token")
    cid = prof.get("company_id")

    if not token or "AQUÍ" in str(token):
        console.print(f"[bold red]❌ El perfil '{profile}' no tiene credenciales válidas configuradas.[/bold red]")
        return

    console.print(f"\n[bold magenta]⚡ FASE 1: STRESS & PERFORMANCE DASHBOARD[/bold magenta]")
    console.print(f"[cyan]Target: {url} | Tenant CID: {cid} | Peticiones: {requests_count} | Concurrencia: {concurrency}[/cyan]\n")

    exporter = APIExporter(url, token)
    metrics = exporter.run_stress_test(cid, total_requests=requests_count, concurrency=concurrency, target_path=target_path)

    # Mostrar Dashboard en Consola
    dashboard = Table(title=f"🚀 Performance Dashboard - {profile}", show_header=True, header_style="bold green")
    dashboard.add_column("Métrica", style="cyan")
    dashboard.add_column("Valor", style="bold white", justify="right")

    dashboard.add_row("Peticiones Totales", str(metrics["total_requests"]))
    dashboard.add_row("Nivel de Concurrencia", f"{metrics['concurrency']} hilos")
    dashboard.add_row("Tiempo Total Ejecució", f"{metrics['total_duration_sec']} s")
    dashboard.add_row("Throughput (RPS)", f"[bold green]{metrics['rps']} req/sec[/bold green]")
    dashboard.add_row("Latencia Mínima", f"{metrics['latency_ms']['min']} ms")
    dashboard.add_row("Latencia Promedio", f"{metrics['latency_ms']['avg']} ms")
    dashboard.add_row("Latencia Max (p95)", f"{metrics['latency_ms']['p95']} ms")
    dashboard.add_row("Latencia Máxima Peak", f"{metrics['latency_ms']['max']} ms")
    dashboard.add_row("Errores / Timeouts", f"[red]{metrics['errors']}[/red]" if metrics['errors'] > 0 else "[green]0[/green]")

    console.print(dashboard)

    # Desglose de Códigos HTTP
    status_table = Table(title="📊 Desglose de Respuestas HTTP", show_header=True, header_style="bold yellow")
    status_table.add_column("Código HTTP", justify="center")
    status_table.add_column("Cantidad", justify="right")
    status_table.add_column("Estado", justify="center")

    for code, count in metrics["status_counts"].items():
        if code in [200, 201, 204]:
            st_text = "[bold green]✅ 200 OK[/bold green]"
        elif code == 429:
            st_text = "[bold yellow]⏳ 429 Rate Limit[/bold yellow]"
        elif code == 401:
            st_text = "[bold red]🔑 401 Unauthorized[/bold red]"
        else:
            st_text = f"[bold red]❌ HTTP {code}[/bold red]"
        status_table.add_row(str(code), str(count), st_text)

    console.print(status_table)
    console.print("\n")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    try:
        if ctx.invoked_subcommand is None:
            interactive_menu(ctx)
    except Exception as e:
        logger.error(f"💥 Error fatal detectado: {e}", exc_info=True)
        log_file = save_error_log()
        console.print(f"\n[bold red]❌ Ocurrió un error inesperado.[/bold red]")
        console.print(f"[yellow]📂 Se ha generado un reporte de error en: [bold]{log_file}[/bold][/yellow]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
