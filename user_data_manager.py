"""
Gestor de datos de usuario
"""
from typing import Any, Dict, List, Optional
from file_manager import FileManager
from username_generator import UsernameGenerator


class UserDataManager:
    """Gestor de datos de usuario"""
    
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.username_generator = UsernameGenerator()
    
    def create_user_data_dict(self, username: str, uuid_str: str, selected_version: str,
                             version_type: str, directory: str, close_launcher: bool,
                             hide_log: bool, enable_uuid: bool, jvm_args: str,
                             java_executable: str) -> Dict[str, Any]:
        """Crea un diccionario con los datos del usuario"""
        return {
            "index": self._generate_user_index(directory),
            "username": username,
            "uuid": uuid_str,
            "selected_version": selected_version,
            "type_version": version_type,
            "advanced_options_directory": directory,
            "advanced_options_close_launcher": close_launcher,
            "hide_log": hide_log,
            "enable_uuid": enable_uuid,
            "jvm_args": jvm_args,
            "java_executable": java_executable,
        }
    
    def save_user_data(self, user_data: Dict[str, Any]) -> None:
        """Guarda los datos del usuario"""
        if self.username_generator.is_randomly_generated(user_data.get("username", "")):
            return
        
        config_file_path = self.file_manager.get_config_file_path(
            user_data["advanced_options_directory"]
        )
        
        user_data_list = self.file_manager.read_config_file(config_file_path)
        user_data_list = self._remove_duplicate_user_data(user_data_list, user_data)
        user_data_list.append(user_data)
        
        self.file_manager.write_config_file(config_file_path, user_data_list)
    
    def load_user_data_from_directory(self, directory: str) -> List[Dict[str, Any]]:
        """Carga los datos de usuario desde un directorio"""
        config_file_path = self.file_manager.get_config_file_path(directory)
        return self.file_manager.read_config_file(config_file_path)
    
    def get_valid_usernames(self, user_data_list: List[Dict[str, Any]]) -> List[str]:
        """Obtiene los nombres de usuario válidos (no generados aleatoriamente)"""
        return [
            user["username"]
            for user in user_data_list
            if not self.username_generator.is_randomly_generated(user.get("username", ""))
        ]
    
    def find_user_by_username(self, user_data_list: List[Dict[str, Any]], 
                             username: str) -> Optional[Dict[str, Any]]:
        """Busca un usuario por nombre de usuario"""
        return next(
            (user for user in user_data_list if user.get("username") == username), 
            None
        )
    
    def _generate_user_index(self, directory: str) -> int:
        """Genera un índice único para el usuario"""
        config_file_path = self.file_manager.get_config_file_path(directory)
        user_data_list = self.file_manager.read_config_file(config_file_path)
        return len(user_data_list) + 1
    
    def _remove_duplicate_user_data(self, user_data_list: List[Dict[str, Any]], 
                                   user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Elimina datos de usuario duplicados"""
        return [
            data for data in user_data_list 
            if data["username"] != user_data["username"]
        ]