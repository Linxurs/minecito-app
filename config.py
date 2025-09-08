"""
Configuración del launcher de Minecraft
"""
import os
from typing import List

# Configuración de JVM por defecto
DEFAULT_JVM_ARGS = [
    "-Xmx2G",
    "-XX:+UnlockExperimentalVMOptions",
    "-XX:+UseG1GC",
    "-XX:G1NewSizePercent=20",
    "-XX:G1ReservePercent=20",
    "-XX:MaxGCPauseMillis=50",
    "-XX:G1HeapRegionSize=32M",
]

# Configuración de ventanas
MAIN_WINDOW_CONFIG = {
    "title": "Minecito v1.5",
    "geometry": "305x160",
    "resizable": False,
    "icon_path": "minecito-app/icons/minecito_launcher.ico"
}

ADVANCED_OPTIONS_WINDOW_CONFIG = {
    "title": "Opciones Avanzadas",
    "width": 340,
    "height": 224,
    "resizable": False,
    "icon_path": "minecito-app/icons/crafting_table.ico"
}

# Configuración de archivos
CONFIG_FILE_NAME = "minecito_config.json"
LAUNCHER_PROFILES_FILE = "launcher_profiles.json"

# Configuración de versiones
VERSION_TYPES = {
    "snapshot": "snapshot",
    "alpha": "old_alpha", 
    "beta": "old_beta",
    "especial": "especial",
    "release": "release"
}

MODLOADERS = ["forge", "fabric", "quilt"]

# Configuración de UI
UI_CONFIG = {
    "entry_width": 20,
    "uuid_entry_width": 23,
    "log_height_normal": 9,
    "log_height_with_uuid": 11,
    "log_width": 63,
    "log_frame_height_normal": 150,
    "log_frame_height_with_uuid": 182
}

# Configuración de Java
JAVA_RUNTIME_PATHS = {
    "modern": "java-runtime-gamma",
    "legacy": "jre-legacy"
}

# Límites de usuario
USERNAME_LIMITS = {
    "min_length": 2,
    "max_length": 15
}