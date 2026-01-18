import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Any
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
@dataclass
class UserData:
    username: str
    uuid: str = ""
    selected_version: str = ""
    type_version: str = "release"
    advanced_options_directory: str = ""
    advanced_options_close_launcher: bool = False
    hide_log: bool = False
    enable_uuid: bool = False
    jvm_args: str = "-Xmx2G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M"
    java_executable: str = ""
    index: int = 0
    @classmethod
    def from_dict(cls, data: dict) -> 'UserData':
        valid_keys = cls.__annotations__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)
class ConfigManager:
    DEFAULT_CONFIG_FILENAME = "minecito_config.json"
    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        self.config_path = os.path.join(base_directory, self.DEFAULT_CONFIG_FILENAME)
        self.users: List[UserData] = []
        self.current_user: Optional[UserData] = None
    def load_config(self) -> None:
        if not os.path.exists(self.config_path):
            logger.info(f"Config file not found at {self.config_path}. Starting with empty config.")
            self.users = []
            return
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                self.users = [UserData.from_dict(user_data) for user_data in data]
            elif isinstance(data, dict):
                self.users = [UserData.from_dict(data)]
            else:
                logger.error("Invalid config format. Expected list or dict.")
                self.users = []
            if self.users:
                self.current_user = self.users[-1]
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON config: {e}")
            self.users = []
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}")
            self.users = []
    def save_config(self) -> None:
        try:
            data = [asdict(user) for user in self.users]
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Config saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise
    def add_or_update_user(self, user_data: UserData) -> None:
        self.users = [u for u in self.users if u.username.lower() != user_data.username.lower()]
        user_data.index = len(self.users) + 1
        self.users.append(user_data)
        self.current_user = user_data
        self.save_config()
    def remove_user(self, username: str) -> None:
        self.users = [u for u in self.users if u.username.lower() != username.lower()]
        if self.current_user and self.current_user.username.lower() == username.lower():
            self.current_user = self.users[-1] if self.users else None
        self.save_config()
    def get_user(self, username: str) -> Optional[UserData]:
        for user in self.users:
            if user.username.lower() == username.lower():
                return user
        return None
    def get_all_usernames(self) -> List[str]:
        return [u.username for u in self.users]
    def set_current_user_by_name(self, username: str) -> bool:
        user = self.get_user(username)
        if user:
            self.current_user = user
            return True
        return False
