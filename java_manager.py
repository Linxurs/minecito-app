"""
Gestor de Java y ejecutables
"""
import os
import subprocess
from typing import Optional
from config import JAVA_RUNTIME_PATHS


class JavaManager:
    """Gestor de Java y ejecutables"""
    
    def __init__(self, minecraft_directory: str):
        self.minecraft_directory = minecraft_directory
        self.java_executable = ""
    
    def get_java_executable_path(self, selected_version: str = "", is_alpha_beta: bool = False) -> str:
        """Obtiene la ruta del ejecutable de Java"""
        if self.java_executable and os.path.isfile(self.java_executable):
            return self.java_executable
        
        if not selected_version:
            return "javaw"
        
        if self._is_alpha_or_beta_version(selected_version, is_alpha_beta):
            return self._get_minecraft_jre_path(JAVA_RUNTIME_PATHS["legacy"])
        
        return self._get_minecraft_jre_path(JAVA_RUNTIME_PATHS["modern"])
    
    def _is_alpha_or_beta_version(self, version_id: str, is_alpha_beta: bool) -> bool:
        """Verifica si es una versión alpha o beta"""
        return (
            version_id.startswith(("a1.", "b1.", "infdev"))
            or is_alpha_beta
        )
    
    def _get_minecraft_jre_path(self, runtime_name: str) -> str:
        """Obtiene la ruta del JRE de Minecraft"""
        runtime_path = os.path.join(
            self.minecraft_directory,
            "runtime",
            runtime_name,
            "windows-x64",
            runtime_name,
            "bin",
            "javaw.exe",
        )
        return runtime_path
    
    def validate_java_executable(self, java_path: str) -> bool:
        """Valida si el ejecutable de Java es válido"""
        if not java_path or not os.path.isfile(java_path):
            return False
        
        return os.path.basename(java_path).lower() in ("java.exe", "javaw.exe")
    
    def get_java_version(self, java_executable: str) -> Optional[str]:
        """Obtiene la versión de Java"""
        if not java_executable:
            return None
        
        java_version_command = [java_executable, "-version"]
        try:
            java_version_output = subprocess.check_output(
                java_version_command, stderr=subprocess.STDOUT, text=True
            )
            return java_version_output.splitlines()[0]
        except (FileNotFoundError, subprocess.CalledProcessError, OSError):
            return None
    
    def set_java_executable(self, java_path: str) -> None:
        """Establece el ejecutable de Java"""
        self.java_executable = java_path