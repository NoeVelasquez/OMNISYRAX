# -*- coding: utf-8 -*-
import os
import re

class TenantImporter:
    """Utilidad para importar tenants desde archivos de texto plano (formato Octane)."""
    
    @staticmethod
    def load_from_file(file_path: str) -> list[dict]:
        """
        Lee un archivo .txt y extrae nombres de tenant y tokens.
        Soporta tokens multilínea y limpieza de espacios.
        """
        if not os.path.exists(file_path):
            return []
            
        tenants = []
        current_name = None
        current_token_parts = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Lógica de detección de Octane:
                # Si contiene '.' o empieza con 'eyJ' o es muy largo y parece base64, es parte del token.
                is_token_part = (
                    '.' in line or 
                    line.startswith('eyJ') or 
                    (re.match(r'^[a-zA-Z0-9_-]+$', line) and len(line) > 50)
                )
                
                if not is_token_part:
                    # Es un nuevo nombre de tenant. Guardamos el anterior si existe.
                    if current_name and current_token_parts:
                        tenants.append({
                            "name": current_name,
                            "token": "".join(current_token_parts)
                        })
                    current_name = line
                    current_token_parts = []
                else:
                    if current_name:
                        current_token_parts.append(line)
            
            # Guardar el último tenant procesado
            if current_name and current_token_parts:
                tenants.append({
                    "name": current_name,
                    "token": "".join(current_token_parts)
                })
                
            return tenants
            
        except Exception as e:
            print(f"⚠️ Error al leer el archivo de importación: {e}")
            return []
