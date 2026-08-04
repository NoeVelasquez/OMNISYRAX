import json
import os
from typing import Dict, Any

class ResourceLoader:
    """Carga recursos estáticos desde archivos JSON"""
    
    def __init__(self, resources_path: str = None):
        if resources_path is None:
            # Por defecto busca en la carpeta resources relativa a la raíz del proyecto
            self.base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'data_lists')
        else:
            self.base_path = resources_path
            
        self.cache = {}

    def load(self, resource_name: str) -> Dict[str, Any]:
        """Carga un recurso JSON y lo guarda en caché"""
        if resource_name in self.cache:
            return self.cache[resource_name]
            
        file_path = os.path.join(self.base_path, f"{resource_name}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cache[resource_name] = data
                return data
        except Exception as e:
            print(f"Error cargando recurso {resource_name}: {e}")
            return {}

# Instancia global para ser usada por los generadores
loader = ResourceLoader()
