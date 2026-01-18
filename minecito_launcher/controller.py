import threading
import tkinter as tk
from typing import Optional, Dict, Any
import uuid
from .model import LauncherModel
from .view import LauncherView
from .config_manager import UserData
import minecraft_launcher_lib
class LauncherController:
    def __init__(self, model: LauncherModel, view: LauncherView):
        self.model = model
        self.view = view
        self.view.btn_launch.config(command=self.on_launch_clicked)
        self.view.btn_close_game.config(command=self.on_close_game_clicked)
        self.view.btn_random_user.config(command=self.on_random_user_clicked)
        self.view.btn_advanced.config(command=self.open_advanced_options)
        self.view.on_username_change = self.on_username_changed
        self.view.on_username_typed = self.on_username_typed
        self.view.set_filter_callbacks(self.on_filter_command)
        self.ignore_filter_change = False
        self._init_data()
    def start(self):
        self.view.root.mainloop()
    def _init_data(self):
        self.model.config_manager.load_config()
        users = self.model.config_manager.get_all_usernames()
        self.view.set_username_list(users)
        current_user = self.model.config_manager.current_user
        if current_user:
            self.view.set_username(current_user.username)
            self._apply_user_settings(current_user)
        else:
            nm = self.model.generate_random_username()
            self.view.set_username(nm)
            self.on_username_changed(nm) 
            self.view.set_layout(show_uuid=False, show_log=False)
        self.refresh_versions()
    def _apply_user_settings(self, user: UserData):
        self.view.set_layout(show_uuid=user.enable_uuid, show_log=user.hide_log)
    def on_filter_command(self, filter_type: str):
        if self.ignore_filter_change: return
        self.ignore_filter_change = True
        if filter_type == "snapshot":
            current = self.view.chk_snapshot_var.get()
            if current:
                 self.view.chk_alpha_var.set(False)
                 self.view.chk_beta_var.set(False)
                 self.view.chk_special_var.set(False)
        elif filter_type == "alpha":
            if self.view.chk_alpha_var.get():
                 self.view.chk_snapshot_var.set(False)
                 self.view.chk_beta_var.set(False)
                 self.view.chk_special_var.set(False)
        elif filter_type == "beta":
             if self.view.chk_beta_var.get():
                 self.view.chk_snapshot_var.set(False)
                 self.view.chk_alpha_var.set(False)
                 self.view.chk_special_var.set(False)
        elif filter_type == "special":
             if self.view.chk_special_var.get():
                 self.view.chk_snapshot_var.set(False)
                 self.view.chk_alpha_var.set(False)
                 self.view.chk_beta_var.set(False)
        self.ignore_filter_change = False
        self.view.root.update_idletasks()
        self.refresh_versions()
    def refresh_versions(self):
        try:
            versions = self.model.get_available_versions()
            show_snap = self.view.chk_snapshot_var.get()
            show_alpha = self.view.chk_alpha_var.get()
            show_beta = self.view.chk_beta_var.get()
            show_special = self.view.chk_special_var.get()
            modloaders = ["forge", "fabric", "quilt"]
            is_modloader = lambda vid: any(ml in vid.lower() for ml in modloaders)
            filtered_ids = []
            if show_special:
                 filtered_ids = [v['id'] for v in versions if is_modloader(v['id'])]
            elif show_snap:
                 filtered_ids = [v['id'] for v in versions if v['type'] == 'snapshot' and not is_modloader(v['id'])]
            elif show_alpha:
                 filtered_ids = [v['id'] for v in versions if v['type'] == 'old_alpha' and not is_modloader(v['id'])]
            elif show_beta:
                 filtered_ids = [v['id'] for v in versions if v['type'] == 'old_beta' and not is_modloader(v['id'])]
            else:
                 filtered_ids = [v['id'] for v in versions if v['type'] == 'release' and not is_modloader(v['id'])]
            self.view.set_version_list(filtered_ids)
            current = self.model.config_manager.current_user
            if current and current.selected_version in filtered_ids:
                 self.view.version_combo.set(current.selected_version)
        except Exception as e:
            print(f"Error fetching versions: {e}")
    def on_launch_clicked(self):
        username = self.view.get_username().strip()
        version = self.view.get_selected_version()
        if not username:
            self.view.show_error("Error", "Debes ingresar un nombre de usuario.")
            return
        if not version:
            self.view.show_error("Error", "Debes seleccionar una versión.")
            return
        if len(username) < 3:
             if not self.view.ask_yes_no("¡ADVERTENCIA!", "No podrás jugar en modo online con un nombre tan corto.\n¿Continuar de todos modos?"):
                 return
        if len(username) > 16:
             if not self.view.ask_yes_no("¡ADVERTENCIA!", "No podrás jugar en modo online con un nombre mayor a 15 caracteres.\n¿Continuar de todos modos?"):
                 return
        is_random = self.model.is_random_username(username)
        if not username or username.lower() == "random": is_random = True
        if not is_random:
            curr = self.model.config_manager.current_user
            if curr and curr.username.strip().lower() == username.lower():
                print(f"[DEBUG] Launch: Using In-Memory User '{curr.username}'")
                user_data = curr
                user_data.selected_version = version
            else:
                existing = self.model.config_manager.get_user(username)
                if existing:
                    print(f"[DEBUG] Launch: Using Saved Disk User '{existing.username}'")
                    user_data = existing
                    user_data.selected_version = version 
                else:
                    print(f"[DEBUG] Launch: Creating NEW User '{username}' (Reset/Default)")
                    user_data = UserData(username=username, selected_version=version)
                    user_data.uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, username))
            self.model.config_manager.add_or_update_user(user_data)
        else:
            if self.model.config_manager.current_user and self.model.config_manager.current_user.username == username:
                 user_data = self.model.config_manager.current_user
                 user_data.selected_version = version
            else:
                 user_data = UserData(username=username, selected_version=version)
                 user_data.uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, username))
            self.model.config_manager.current_user = user_data
        self.view.toggle_controls(False)
        show_log = user_data.hide_log
        show_uuid = user_data.enable_uuid
        self.view.set_layout(show_uuid=show_uuid, show_log=show_log)
        self.view.btn_close_game.config(state="disabled") 
        if not self.model.is_version_installed(version):
            threading.Thread(target=self._install_and_launch, args=(version,), daemon=True).start()
        else:
            threading.Thread(target=self._launch_task, args=(version,), daemon=True).start()
    def _install_and_launch(self, version):
        callback = {
            "setStatus": lambda s: self._log_safe(f"Estado: {s}"),
            "setProgress": lambda p: None, 
            "setMax": lambda m: None
        }
        try:
            self._log_safe(f"Iniciando la instalación de '{version}'...")
            self.model.install_version(version, callback)
            self._log_safe(f"La versión '{version}' se instaló correctamente.")
            self._launch_task(version)
        except Exception as e:
            self._log_safe(f"Error: {e}")
            self._run_on_main(lambda: self.view.toggle_controls(True))
    def _launch_task(self, version):
        def log_callback(msg):
            if "Comando de Minecraft ejecutado:" in msg:
                formatted = self._format_log_message(msg)
                self._log_safe(formatted)
            else:
                self._log_safe(msg)
        try:
             self._log_safe("Iniciando Minecraft...")
             self._run_on_main(lambda: self.view.btn_close_game.config(state="normal"))
             self.model.launch_minecraft(version, log_callback)
             if self.model.config_manager.current_user and self.model.config_manager.current_user.advanced_options_close_launcher:
                 self._run_on_main(self.view.root.destroy)
             if self.model.process:
                 ret = self.model.process.wait()
                 if ret == 0:
                     self._log_safe("Minecraft cerrado correctamente.")
                 else:
                     self._log_safe(f"Minecraft cerrado con ERROR (Código de salida: {ret})")
                     self._run_on_main(lambda: self.view.show_log_window_if_hidden())
        except Exception as e:
             self._log_safe(f"Error: {e}")
        finally:
             if self.view.root.winfo_exists():
                 self._run_on_main(lambda: self.view.toggle_controls(True))
                 self._run_on_main(lambda: self.view.btn_close_game.config(state="disabled"))
    def on_close_game_clicked(self):
        self.model.close_minecraft()
        self.view.btn_close_game.config(state="disabled")
    def on_random_user_clicked(self):
        name = self.model.generate_random_username()
        self.view.set_username(name)
        self.on_username_changed(name)
    def on_username_typed(self, event=None):
        name = self.view.get_username()
        self.on_username_changed(name)
    def on_username_changed(self, new_username):
        user = self.model.config_manager.get_user(new_username)
        color = "black"
        is_short = len(new_username) < 3
        is_long = len(new_username) > 15
        is_random = self.model.is_random_username(new_username)
        if is_short or is_long:
            color = "red"
        elif is_random:
            color = "gray"
        self.view.set_username_color(color)
        uuid_val = ""
        if user:
            uuid_val = user.uuid
            self.model.config_manager.current_user = user
            self._apply_user_settings(user)
        else:
             clean_name = new_username.strip()
             ephemeral_user = UserData(username=clean_name)
             if not clean_name:
                 uuid_val = "Random"
                 ephemeral_user.uuid = str(uuid.uuid4())
             else:
                 uuid_val = str(uuid.uuid5(uuid.NAMESPACE_DNS, clean_name))
                 ephemeral_user.uuid = uuid_val
             self.model.config_manager.current_user = ephemeral_user
        self.view.set_uuid(uuid_val)
        self.view.set_uuid_color(color)
    def open_advanced_options(self):
        current_username = self.view.get_username()
        if self.model.config_manager.current_user and self.model.config_manager.current_user.username == current_username:
            user = self.model.config_manager.current_user
        else:
            user = self.model.config_manager.get_user(current_username)
        def_jvm = "-Xmx2G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M"
        def_java = minecraft_launcher_lib.utils.get_java_executable() or "javaw"
        def_dir = self.model.minecraft_directory
        def_close = False
        def_log = False
        def_uuid = False
        if user:
             jvm_args = user.jvm_args or def_jvm
             java_path = user.java_executable or def_java
             directory = user.advanced_options_directory or def_dir
             close = user.advanced_options_close_launcher
             log_vis = user.hide_log
             uuid_vis = user.enable_uuid
             allow_del = self.model.config_manager.get_user(current_username) is not None
        else:
             jvm_args = def_jvm
             java_path = def_java
             directory = def_dir
             close = def_close
             log_vis = def_log
             uuid_vis = def_uuid
             allow_del = False
        self.view.create_advanced_options_window(
            current_jvm=jvm_args,
            current_java=java_path,
            current_dir=directory,
            close_launcher=close,
            hide_log=log_vis, 
            enable_uuid=uuid_vis,
            on_apply=self.on_apply_advanced,
            on_cancel=lambda: None,
            on_delete_user=lambda: None,
            allow_delete=allow_del
        )
    def on_apply_advanced(self, data: Dict[str, Any]):
        user = self.model.config_manager.current_user
        if not user:
             current_username = self.view.get_username()
             user = UserData(username=current_username, uuid=str(uuid.uuid5(uuid.NAMESPACE_DNS, current_username)))
             self.model.config_manager.current_user = user 
        if data['del_user']:
            username = user.username
            if self.view.ask_yes_no("Confirmar Eliminación", f"¿Estás seguro de que quieres eliminar el usuario '{username}'?\nSe borrarán todas sus configuraciones."):
                self.model.config_manager.remove_user(username)
                nm = self.model.generate_random_username()
                self.view.set_username(nm)
                self.on_username_changed(nm)
                self.view.close_adv_window()
                return
        user.jvm_args = data['jvm']
        user.java_executable = data['java']
        user.advanced_options_directory = data['dir']
        user.advanced_options_close_launcher = data['close']
        user.hide_log = data['log_visible'] 
        user.enable_uuid = data['uuid_visible']
        if not self.model.is_random_username(user.username):
             self.model.config_manager.add_or_update_user(user)
        else:
             pass
        self.view.set_layout(show_uuid=user.enable_uuid, show_log=user.hide_log)
        self.view.close_adv_window()
    def _log_safe(self, message):
        self._run_on_main(lambda: self.view.log_message(message))
    def _run_on_main(self, func):
        if self.view.root.winfo_exists():
            self.view.root.after(0, func)
    def _format_log_message(self, message: str) -> str:
        try:
            cmd = message.split(": ", 1)[1]
            parts = cmd.split()
            formatted = ["INFORMACIÓN DE LA SESIÓN:\n"]
            formatted.append("=== Java ===\n")
            formatted.append(f"{parts[0]}\n")
            formatted.append("=== Usuario ===\n")
            if "--username" in parts:
                idx = parts.index("--username")
                if idx + 1 < len(parts):
                    formatted.append(f"{parts[idx+1]}\n")
            return "".join(formatted)
        except:
             return message
