"""
Gestor de archivos y configuración
"""
import json
import os
import uuid
from typing import Any, Dict, List, Optional
import minecraft_launcher_lib


class FileManager:
    """Gestor de archivos y configuración del launcher"""
    
    def __init__(self, minecraft_directory: str, config_file: str):
        self.minecraft_directory = minecraft_directory
        self.config_file = config_file
    
    def ensure_launcher_profiles_exists(self) -> None:
        """Asegura que el archivo launcher_profiles.json exista"""
        profiles_path = os.path.join(self.minecraft_directory, "launcher_profiles.json")
        
        try:
            if not os.path.exists(profiles_path):
                default_profiles: Dict[str, Any] = {
                    "profiles": {},
                    "clientToken": str(uuid.uuid4()),
                    "settings": {"crashAssistance": True, "enableAnalytics": False},
                    "launcherVersion": {"name": "Minecito-1.5", "format": 21},
                }
                os.makedirs(os.path.dirname(profiles_path), exist_ok=True)
                with open(profiles_path, "w", encoding="utf-8") as f:
                    json.dump(default_profiles, f, indent=4)
        except (OSError, Exception) as e:
            raise Exception(f"Error creando launcher_profiles.json: {e}")
    
    def read_config_file(self, config_path: str) -> List[Dict[str, Any]]:
        """Lee el archivo de configuración"""
        try:
            with open(config_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                if not isinstance(data, list):
                    return [data]
                return data
        except (json.JSONDecodeError, FileNotFoundError, IOError):
            return []
        except Exception:
            return []
    
    def write_config_file(self, config_file_path: str, user_data_list: List[Dict[str, Any]]) -> None:
        """Escribe el archivo de configuración"""
        with open(config_file_path, "w", encoding="utf-8") as json_file:
            json.dump(user_data_list, json_file, indent=2)
    
    def get_config_file_path(self, directory: str) -> str:
        """Obtiene la ruta del archivo de configuración"""
        return os.path.join(directory, self.config_file)
    
    def initialize_minecraft_directory(self) -> str:
        """Inicializa el directorio de Minecraft"""
        default_minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
        
        if not os.access(default_minecraft_directory, os.W_OK):
            local_appdata_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), ".minecito")
            
            if not os.path.exists(local_appdata_path):
                os.makedirs(local_appdata_path)
            
            return local_appdata_path
        
        return default_minecraft_directory
    
    def extract_base_version(self, version_name: str) -> Optional[str]:
        """Extrae la versión base de un nombre de versión con modloader"""
        parts = version_name.split("-")
        for part in reversed(parts):
            if part.count(".") == 2 and part.replace(".", "").isdigit():
                return part
        return None