"""
Gestor de versiones de Minecraft
"""
import os
import shutil
from typing import List, Optional
import minecraft_launcher_lib
from minecraft_launcher_lib.types import MinecraftVersionInfo
from config import VERSION_TYPES, MODLOADERS


class VersionManager:
    """Gestor de versiones de Minecraft"""
    
    def __init__(self, minecraft_directory: str):
        self.minecraft_directory = minecraft_directory
    
    def get_available_versions(self) -> List[MinecraftVersionInfo]:
        """Obtiene todas las versiones disponibles"""
        return minecraft_launcher_lib.utils.get_available_versions(self.minecraft_directory)
    
    def filter_versions_by_type(self, all_versions: List[MinecraftVersionInfo], 
                               selected_types: List[str]) -> List[MinecraftVersionInfo]:
        """Filtra versiones por tipo"""
        if "especial" in selected_types:
            return self._filter_special_versions(all_versions)
        
        if selected_types:
            return self._filter_by_selected_types(all_versions, selected_types)
        
        return self._filter_release_versions(all_versions)
    
    def _filter_special_versions(self, all_versions: List[MinecraftVersionInfo]) -> List[MinecraftVersionInfo]:
        """Filtra versiones especiales (con modloaders)"""
        return [v for v in all_versions if any(ml in v["id"] for ml in MODLOADERS)]
    
    def _filter_by_selected_types(self, all_versions: List[MinecraftVersionInfo], 
                                 selected_types: List[str]) -> List[MinecraftVersionInfo]:
        """Filtra por tipos seleccionados"""
        return [
            v for v in all_versions
            if v["type"] in selected_types
            and not any(ml in v["id"] for ml in MODLOADERS)
        ]
    
    def _filter_release_versions(self, all_versions: List[MinecraftVersionInfo]) -> List[MinecraftVersionInfo]:
        """Filtra solo versiones release"""
        return [
            v for v in all_versions
            if v["type"] == "release" 
            and not any(ml in v["id"] for ml in MODLOADERS)
        ]
    
    def is_valid_version(self, version: str) -> bool:
        """Verifica si una versión es válida"""
        return minecraft_launcher_lib.utils.is_version_valid(version, self.minecraft_directory)
    
    def version_directory_exists(self, version: str) -> bool:
        """Verifica si el directorio de la versión existe"""
        version_directory = os.path.join(self.minecraft_directory, "versions", version)
        return os.path.exists(version_directory)
    
    def copy_jar_for_modloader(self, selected_version: str, base_version: Optional[str]) -> None:
        """Copia el JAR para versiones con modloader"""
        if not base_version:
            return
        
        vanilla_jar_path = self._build_vanilla_jar_path(base_version)
        modloader_jar_path = self._build_modloader_jar_path(selected_version)
        
        if not os.path.exists(vanilla_jar_path):
            return
        
        self._prepare_modloader_directory(modloader_jar_path)
        
        if not os.path.exists(modloader_jar_path):
            shutil.copy2(vanilla_jar_path, modloader_jar_path)
    
    def _build_vanilla_jar_path(self, base_version: str) -> str:
        """Construye la ruta del JAR vanilla"""
        return os.path.join(
            self.minecraft_directory, "versions", base_version, f"{base_version}.jar"
        )
    
    def _build_modloader_jar_path(self, selected_version: str) -> str:
        """Construye la ruta del JAR del modloader"""
        modloader_folder = os.path.join(
            self.minecraft_directory, "versions", selected_version
        )
        return os.path.join(modloader_folder, f"{selected_version}.jar")
    
    def _prepare_modloader_directory(self, modloader_jar_path: str) -> None:
        """Prepara el directorio del modloader"""
        modloader_folder = os.path.dirname(modloader_jar_path)
        if not os.path.exists(modloader_folder):
            os.makedirs(modloader_folder)
    
    def has_modloader(self, version: str) -> bool:
        """Verifica si la versión tiene modloader"""
        return any(modloader in version.lower() for modloader in MODLOADERS)