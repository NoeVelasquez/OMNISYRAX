import csv
import os
import logging
from typing import List, Dict, Any

class Exporter:
    """Maneja la exportación de datos generados a archivos"""
    
    def __init__(self, output_dir: str = "data"):
        # Asegurar que el directorio sea absoluto respecto a la raíz del proyecto
        self.output_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), output_dir))
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)

    def to_csv(self, data: List[Dict[str, Any]], filename: str) -> str:
        """Exporta una lista de diccionarios a CSV"""
        if not data:
            self.logger.warning("No hay datos para exportar.")
            return ""
            
        file_path = os.path.join(self.output_dir, filename)
        if not file_path.endswith('.csv'):
            file_path += '.csv'
            
        try:
            keys = data[0].keys()
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            
            self.logger.info(f"Datos exportados exitosamente a: {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Error exportando a CSV {filename}: {e}")
            return ""

    def to_json(self, data: List[Dict[str, Any]], filename: str) -> str:
        """Exporta una lista de diccionarios a JSON (para futura expansión)"""
        import json
        file_path = os.path.join(self.output_dir, filename)
        if not file_path.endswith('.json'):
            file_path += '.json'
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return file_path
        except Exception as e:
            self.logger.error(f"Error exportando a JSON {filename}: {e}")
            return ""
