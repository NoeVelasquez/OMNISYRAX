"""Valores del modo Rápido: predeterminados fijos + memoria de la última configuración usada."""
import json
from pathlib import Path
from typing import Any, Dict, Iterable

SETTINGS_PATH = Path(__file__).resolve().parents[2] / "data" / ".quick_settings.json"

QUICK_DEFAULTS: Dict[str, Any] = {
    "order_multi_sku": False,     # 1 SKU por orden
    "order_days": 0,              # Solo el día de hoy
    "order_country": "US",        # Local EE.UU.
    "currency": "USD",
    "category": "all",            # Aleatoria
    "brand": "all",               # Aleatoria
    "lang": "es",                 # Solo Español
    "sku_mode": "single",         # 1 Producto = 1 SKU
    "sync_repeat_skus": True,     # Los SKUs pueden repetirse entre órdenes
    "upload_api": False,          # Sin usar API
    "edi_items_mode": "single",   # 1 producto por orden EDI
    "edi_sku_choice": "random",   # SKU generado al azar
}

_COUNTRY_LABELS = {"US": "Local EE.UU.", "INT": "Global / Internacional", "MIXED": "Mixto (EE.UU. + Internacional)"}
_LANG_LABELS = {"all": "Multilingüe", "es": "Español", "en": "Inglés"}
_SKU_MODE_LABELS = {"single": "Single-SKU (1 producto = 1 SKU)", "multi": "Multi-SKU (padre con 2-5 variantes)", "mixed": "Mixto (Single + Multi)"}

_LABELS = {
    "order_multi_sku": "Tipo de orden",
    "sku_source": "SKUs",
    "order_days": "Fechas",
    "order_country": "Alcance",
    "currency": "Moneda",
    "category": "Categoría",
    "brand": "Marca",
    "lang": "Idioma",
    "sku_mode": "Estructura de SKUs",
    "sync_repeat_skus": "Repetir SKUs entre órdenes",
    "upload_api": "Carga vía API",
    "edi_items_mode": "Composición EDI",
    "edi_sku_choice": "SKU EDI",
}


def load_quick_settings() -> Dict[str, Any]:
    """Predeterminados sobrescritos por lo último que se usó (si existe y es válido)."""
    settings = dict(QUICK_DEFAULTS)
    try:
        saved = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        if isinstance(saved, dict):
            settings.update({k: v for k, v in saved.items() if k in QUICK_DEFAULTS})
    except (OSError, ValueError):
        pass
    return settings


def save_quick_settings(values: Dict[str, Any]) -> None:
    """Guarda solo las claves conocidas, conservando las de otros flujos."""
    current = load_quick_settings()
    current.update({k: v for k, v in values.items() if k in QUICK_DEFAULTS})
    try:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(json.dumps(current, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def reset_quick_settings(keys: Iterable[str]) -> None:
    save_quick_settings({k: QUICK_DEFAULTS[k] for k in keys})


def describe(key: str, value: Any) -> str:
    if key == "order_multi_sku":
        text = "Multi-SKU (1-5 productos)" if value else "1 SKU por orden"
    elif key == "sku_source":
        text = "Generados al azar"
    elif key == "order_days":
        text = "Solo el día de hoy" if not value else f"Últimos {value} días"
    elif key == "order_country":
        text = _COUNTRY_LABELS.get(value, value)
    elif key == "currency":
        text = "Según el país de la dirección" if value == "AUTO" else value
    elif key in ("category", "brand"):
        text = "Aleatoria" if value == "all" else value
    elif key == "lang":
        text = _LANG_LABELS.get(value, value)
    elif key == "sku_mode":
        text = _SKU_MODE_LABELS.get(value, value)
    elif key in ("sync_repeat_skus",):
        text = "Sí" if value else "No"
    elif key == "upload_api":
        text = "Sí, al finalizar" if value else "Sin usar API"
    elif key == "edi_items_mode":
        text = "1 producto" if value == "single" else "Multi-línea (2-5 productos)"
    elif key == "edi_sku_choice":
        text = "Generado al azar" if value == "random" else "SKU específico (990394169)"
    else:
        text = str(value)
    return f"{_LABELS.get(key, key)}: {text}"
