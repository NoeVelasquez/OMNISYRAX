# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Any, Dict
import yaml

class ConfigManager:
    """
    Gestiona la configuración del proyecto, cargando desde archivos YAML,
    variables de entorno o valores por defecto.
    """
    
    def __init__(self, config_file: str = None):
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.config_dir = self.base_dir / "config"
        
        # Valores por defecto
        self.settings = {
            "default_num_orders": 100,
            "default_num_products": 1000,
            "output_encoding": "utf-8",
            "log_level": "INFO",
            "api_base_url": "https://qa5-condor.omniorders.com/",
        }
        
        if config_file and os.path.exists(config_file):
            self.load_from_yaml(config_file)
        
        # Cargar credenciales si existen
        self.credentials = {}
        credentials_path = self.config_dir / "credentials.yaml"
        if credentials_path.exists():
            self.load_credentials(str(credentials_path))
        
        # Asegurar directorios
        self.data_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)

    def load_from_yaml(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                loaded_settings = yaml.safe_load(f)
                if loaded_settings:
                    self.settings.update(loaded_settings)
        except Exception as e:
            print(f"Error cargando configuración desde {path}: {e}")

    def load_credentials(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and "profiles" in data:
                    self.credentials = data["profiles"]
        except Exception as e:
            print(f"Error cargando credenciales desde {path}: {e}")

    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        return self.credentials.get(profile_name, {})

    def save_profile(self, name: str, token: str, company_id: str, process_id: str, api_base_url: str = None, currency: str = None) -> bool:
        """Guarda o actualiza un perfil de tenant en el archivo credentials.yaml."""
        credentials_path = self.config_dir / "credentials.yaml"
        
        # Cargar archivo crudo actual o crear uno nuevo si no existe
        data = {"profiles": {}}
        if credentials_path.exists():
            try:
                with open(credentials_path, 'r', encoding='utf-8') as f:
                    loaded_data = yaml.safe_load(f)
                    if isinstance(loaded_data, dict):
                        data = loaded_data
            except Exception as e:
                print(f"Error leyendo credentials para guardar: {e}")
        
        if "profiles" not in data or not isinstance(data["profiles"], dict):
            data["profiles"] = {}
            
        profile_data = {
            "api_base_url": api_base_url or self.get("api_base_url"),
            "token": token,
            "company_id": company_id,
            "process_id": process_id
        }
        if currency:
            profile_data["currency"] = currency
            
        data["profiles"][name] = profile_data
        
        try:
            with open(credentials_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
            # Recargar credenciales en memoria
            self.credentials = data["profiles"]
            return True
        except Exception as e:
            print(f"Error guardando credentials: {e}")
            return False

    def delete_profile(self, name: str) -> bool:
        """Elimina un perfil del archivo credentials.yaml."""
        credentials_path = self.config_dir / "credentials.yaml"
        if not credentials_path.exists():
            return False
            
        try:
            with open(credentials_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                
            if "profiles" in data and name in data["profiles"]:
                del data["profiles"][name]
                
                with open(credentials_path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
                
                self.credentials = data.get("profiles", {})
                return True
        except Exception as e:
            print(f"Error eliminando perfil: {e}")
        return False

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    @property
    def output_dir(self) -> Path:
        return self.data_dir

# Instancia global para uso sencillo
config = ConfigManager()
