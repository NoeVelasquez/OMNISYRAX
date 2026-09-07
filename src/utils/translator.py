# -*- coding: utf-8 -*-
"""
Módulo de traducción y localización para OMNISYRAX.
Permite traducir descripciones y textos a español (u otros idiomas soportados)
utilizando caché local, APIs de traducción rápida y fallback inteligente offline.
"""

import os
import json
import re
import urllib.request
import urllib.parse
from typing import Optional, Dict

class TextTranslator:
    _cache: Dict[str, str] = {}
    _cache_file = os.path.join("data", ".translation_cache.json")
    _loaded = False

    @classmethod
    def _load_cache(cls):
        if cls._loaded:
            return
        cls._loaded = True
        if os.path.exists(cls._cache_file):
            try:
                with open(cls._cache_file, "r", encoding="utf-8") as f:
                    cls._cache = json.load(f)
            except Exception:
                cls._cache = {}

    @classmethod
    def _save_cache(cls):
        try:
            os.makedirs("data", exist_ok=True)
            # Limitar tamaño de caché para evitar consumo excesivo
            if len(cls._cache) > 2000:
                keys = list(cls._cache.keys())[-1500:]
                cls._cache = {k: cls._cache[k] for k in keys}
            with open(cls._cache_file, "w", encoding="utf-8") as f:
                json.dump(cls._cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @classmethod
    def translate(cls, text: str, target_lang: str = "es", source_lang: str = "en") -> str:
        """
        Traduce un texto al idioma objetivo.
        Si target_lang == source_lang o target_lang in ("all", ""), retorna el texto original.
        """
        if not text or not isinstance(text, str):
            return text or ""

        text = text.strip()
        if not text:
            return ""

        target_lang = target_lang.lower().strip()
        if target_lang in ("all", "") or target_lang == source_lang:
            return text

        cls._load_cache()
        cache_key = f"{source_lang}->{target_lang}:{text}"
        if cache_key in cls._cache:
            return cls._clean_result(cls._cache[cache_key], target_lang)

        # Intentar traducción online vía MyMemory API con timeout corto
        translated = cls._translate_mymemory(text, target_lang, source_lang)
        if translated and translated.lower() != text.lower():
            cleaned = cls._clean_result(translated, target_lang)
            cls._cache[cache_key] = cleaned
            cls._save_cache()
            return cleaned

        # Fallback de traducción por reglas / plantillas offline para español
        if target_lang == "es":
            translated = cls._offline_spanish_fallback(text)
            cleaned = cls._clean_result(translated, target_lang)
            cls._cache[cache_key] = cleaned
            cls._save_cache()
            return cleaned

        return cls._clean_result(text, target_lang)

    @classmethod
    def _clean_result(cls, text: str, target_lang: str) -> str:
        """Limpia y pule residuos de traducción."""
        if not text:
            return ""
        if target_lang == "es":
            text = re.sub(r'\bby Various\b', 'por Varios autores', text, flags=re.IGNORECASE)
            text = re.sub(r'\bby Famous Author\b', 'por Autor Destacado', text, flags=re.IGNORECASE)
            text = re.sub(r'\bby\b', 'por', text, flags=re.IGNORECASE)
            text = re.sub(r'\bClassic edition of\b', 'Edición clásica de', text, flags=re.IGNORECASE)
            text = re.sub(r'\bEdición clásica de (.*?) by (.*?)\.?', r'Edición clásica de \1 por \2.', text, flags=re.IGNORECASE)
            text = re.sub(r'\bEdición clásica de (.*?) de (.*?)\.?', r'Edición clásica de \1 por \2.', text, flags=re.IGNORECASE)
            text = re.sub(r'\bpor\s*\.+', 'por ', text, flags=re.IGNORECASE)
            text = re.sub(r'\s{2,}', ' ', text)
        elif target_lang == "en":
            text = re.sub(r'\bLibro:\b', 'Book:', text, flags=re.IGNORECASE)
            text = re.sub(r'\bEdición clásica de (.*?) por (.*?)\.?', r'Classic edition of \1 by \2.', text, flags=re.IGNORECASE)
            text = re.sub(r'\bEdición clásica de (.*?) de (.*?)\.?', r'Classic edition of \1 by \2.', text, flags=re.IGNORECASE)
            text = re.sub(r'\bFigura Coleccionable\b', 'Collectible Figure', text, flags=re.IGNORECASE)
            text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()

    @classmethod
    def localize_name(cls, name: str, category: str = "", brand: str = "", lang: str = "all") -> str:
        """Localiza y limpia el nombre del producto según el idioma y categoría seleccionados."""
        if not name:
            return ""
        
        name = name.strip()
        lang = (lang or "all").lower().strip()

        # Categoría Libros
        if category and category.lower() == "books":
            # Extraer título real eliminando prefijos previos
            clean_title = re.sub(r'^(?:[A-Za-z0-9\s\-]+)?(?:Book|Libro)\s*:\s*', '', name, flags=re.IGNORECASE).strip()
            if not clean_title:
                clean_title = name
            if lang == "es":
                return f"Libro: {clean_title}"
            elif lang == "en":
                return f"Book: {clean_title}"
            else:
                return f"Libro: {clean_title}" if lang == "es" else f"Book: {clean_title}"

        # Categoría Juguetes
        if category and category.lower() == "toys":
            clean_toy = re.sub(r'^(?:Figura Coleccionable|Collectible Figure|Collectable Figure)\s*', '', name, flags=re.IGNORECASE).strip()
            if not clean_toy:
                clean_toy = name
            if lang == "es":
                return f"Figura Coleccionable {clean_toy}"
            elif lang == "en":
                return f"Collectible Figure {clean_toy}"
            else:
                return f"Figura Coleccionable {clean_toy}" if lang == "es" else f"Collectible Figure {clean_toy}"

        if lang == "es":
            replacements = {
                r'\bLaptop\b': 'Portátil',
                r'\bWireless Earbuds\b': 'Auriculares Inalámbricos',
                r'\bEarbuds\b': 'Auriculares',
                r'\bHeadphones\b': 'Audífonos',
                r'\bSmartwatch\b': 'Reloj Inteligente',
                r'\bBackpack\b': 'Mochila',
                r'\bT-Shirt\b': 'Camiseta',
                r'\bHoodie\b': 'Sudadera',
                r'\bSweater\b': 'Suéter',
                r'\bShoes\b': 'Zapatos',
                r'\bDress\b': 'Vestido',
                r'\bJacket\b': 'Chaqueta',
                r'\bNecklace\b': 'Collar',
                r'\bBracelet\b': 'Pulsera',
                r'\bEarrings\b': 'Pendientes',
                r'\bRing\b': 'Anillo',
                r'\bSunglasses\b': 'Gafas de Sol',
                r'\bFace Serum\b': 'Suero Facial',
                r'\bLipstick\b': 'Lápiz Labial',
                r'\bMascara\b': 'Máscara de Pestañas',
                r'\bBlush\b': 'Colorete',
                r'\bWater Bottle\b': 'Botella de Agua',
                r'\bCleaning Cloth\b': 'Paño de Limpieza'
            }
            res = name
            for pat, rep in replacements.items():
                res = re.sub(pat, rep, res, flags=re.IGNORECASE)
            return res

        return name

    @staticmethod
    def _translate_mymemory(text: str, target_lang: str, source_lang: str) -> Optional[str]:
        try:
            encoded_text = urllib.parse.quote(text[:400])
            url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair={source_lang}|{target_lang}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                resp_data = data.get("responseData", {})
                trans = resp_data.get("translatedText")
                if trans and not trans.startswith("MYMEMORY WARNING:") and trans.strip():
                    import html
                    trans = html.unescape(trans)
                    return trans.strip()
        except Exception:
            pass
        return None

    @classmethod
    def _offline_spanish_fallback(cls, text: str) -> str:
        """Fallback heurístico para traducir frases y descripciones comunes de productos a español."""
        translations = {
            "Bold sound for every adventure": "Sonido potente para cada aventura",
            "delivers powerful": "ofrece una potente experiencia",
            "exceptional clarity": "claridad excepcional",
            "portable waterproof speaker": "altavoz portátil resistente al agua",
            "wireless on-ear headphones": "auriculares inalámbricos de diadema",
            "stream powerful": "transmite un sonido potente",
            "pure bass sound": "sonido de bajos puros",
            "easy to use": "fácil de usar",
            "high-performance": "alto rendimiento",
            "with dual screens": "con pantallas duales",
            "providing productivity and versatility": "proporcionando productividad y versatilidad",
            "for creative professionals": "para profesionales creativos",
            "Classic edition of": "Edición clásica de",
            "Limited edition collectible figure": "Figura coleccionable de edición limitada",
            "Limited edition figurine": "Figura de edición limitada",
            "High quality product": "Producto de alta calidad",
            "designed to meet the most demanding needs": "diseñado para satisfacer las necesidades más exigentes",
            "Take the party with you": "Lleva la fiesta contigo",
            "no matter what the weather": "sin importar el clima",
            "battery life": "duración de batería",
            "fast charging": "carga rápida",
            "noise cancellation": "cancelación de ruido",
            "built-in microphone": "micrófono integrado"
        }

        res = text
        for en_phrase, es_phrase in translations.items():
            pattern = re.compile(re.escape(en_phrase), re.IGNORECASE)
            res = pattern.sub(es_phrase, res)

        if " by " in res:
            res = re.sub(r'\bby\b', 'por', res, flags=re.IGNORECASE)

        return res
