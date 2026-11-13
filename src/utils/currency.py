# -*- coding: utf-8 -*-
"""Configuración central de monedas para órdenes (CSV y carga API a OMNIO)."""
import re
from typing import Optional

DEFAULT_CURRENCY = "USD"
AUTO_CURRENCY = "AUTO"  # Usa la moneda según el país de la dirección de envío

COMMON_CURRENCIES = {
    "USD": "Dólar estadounidense",
    "MXN": "Peso mexicano",
    "EUR": "Euro",
    "CAD": "Dólar canadiense",
    "GBP": "Libra esterlina",
    "BRL": "Real brasileño",
}


def normalize_currency(code: Optional[str], default: Optional[str] = DEFAULT_CURRENCY) -> Optional[str]:
    """Devuelve el código ISO 4217 en mayúsculas, 'AUTO', o `default` si viene vacío.

    Lanza ValueError si el código no tiene el formato de 3 letras.
    """
    if code is None or not str(code).strip():
        return default
    value = str(code).strip().upper()
    if value == AUTO_CURRENCY:
        return AUTO_CURRENCY
    if not re.fullmatch(r"[A-Z]{3}", value):
        raise ValueError(f"Moneda inválida '{code}'. Usa un código ISO de 3 letras (ej. USD, EUR) o AUTO.")
    return value


def resolve_currency(address_currency: Optional[str], selected: Optional[str]) -> str:
    """Moneda final de una orden: la elegida, o la del país si se eligió AUTO."""
    if selected and selected != AUTO_CURRENCY:
        return selected
    if selected == AUTO_CURRENCY and address_currency:
        return address_currency
    return DEFAULT_CURRENCY
