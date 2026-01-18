import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
class LauncherView:
    def __init__(self, root):
        self.root = root
        self.root.resizable(False, False)
        self.root.title("Minecito v1.5.6")
        self.root.geometry("305x160")
        try:
            self.root.iconbitmap("icons/minecito_launcher.ico")
        except:
            pass
        self.on_username_change = None
        self.on_username_typed = None
        self.on_filter_callback = None
        self.frame = None
        self.label_username = None
        self.username_entry = None                             
        self.btn_random_user = None                                             
        self.label_version = None
        self.version_combo = None                                
        self.label_uuid = None
        self.uuid_val_label = None                                 
        self.entry_uuid = None
        self.chk_snapshot_var = tk.BooleanVar()
        self.chk_alpha_var = tk.BooleanVar()
        self.chk_beta_var = tk.BooleanVar()
        self.chk_special_var = tk.BooleanVar()
        self.btn_launch = None
        self.btn_close_game = None
        self.btn_advanced = None
        self.log_frame = None
        self.log_text = None
        self.log_frame = None
        self.log_text = None
        self.setup_ui()
        self.center_window(305, 160)
    def setup_ui(self):
        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        self.label_username = ttk.Label(self.frame, text="Nombre de Usuario:")
        self.username_entry = ttk.Combobox(self.frame, width=20)
        self.username_entry.bind("<<ComboboxSelected>>", self.on_combo_select)
        self.username_entry.bind('<KeyRelease>', self.on_key_release)
        self.username_entry.bind("<FocusOut>", lambda e: None)                                                            
        self.label_username.place(x=5, y=5)
        self.username_entry.place(x=120, y=5)
        self.btn_random_user = ttk.Button(self.frame, text="R", width=3)
        self.btn_random_user.place(x=270, y=3)
        self.label_version = ttk.Label(self.frame, text="Versión:")
        self.version_combo = ttk.Combobox(self.frame, state="readonly", width=20)
        self.label_version.place(x=35, y=35)
        self.version_combo.place(x=120, y=35)
        checkbox_frame = ttk.Frame(self.frame)
        checkbox_frame.place(x=25, y=65)
        self.chk_snap = ttk.Checkbutton(checkbox_frame, text="Snapshot", variable=self.chk_snapshot_var)
        self.chk_snap.grid(row=0, column=0, padx=2)
        self.chk_beta = ttk.Checkbutton(checkbox_frame, text="Beta", variable=self.chk_beta_var)
        self.chk_beta.grid(row=0, column=1, padx=2)
        self.chk_alpha = ttk.Checkbutton(checkbox_frame, text="Alpha", variable=self.chk_alpha_var)
        self.chk_alpha.grid(row=0, column=2, padx=2)
        self.chk_special = ttk.Checkbutton(checkbox_frame, text="Especial", variable=self.chk_special_var)
        self.chk_special.grid(row=0, column=3, padx=2)
        self.label_uuid = ttk.Label(self.frame, text="UUID:")
        self.uuid_val_label = ttk.Entry(self.frame, width=23, state="normal")                                                             
        self.label_uuid.place(x=40, y=95)
        self.uuid_val_label.place(x=120, y=95)
        self.label_uuid.place_forget()
        self.uuid_val_label.place_forget()
        self.btn_launch = ttk.Button(self.frame, text="¡Iniciar Minecraft!")
        self.btn_launch.place(x=45, y=96)
        self.btn_close_game = ttk.Button(self.frame, text="¡Cerrar Minecraft!", state="disabled")
        self.btn_close_game.place(x=155, y=96)
        self.btn_advanced = ttk.Button(self.frame, text="Opciones Avanzadas")
        self.btn_advanced.place(x=90, y=130)
        self.log_frame = ttk.Frame(self.frame)
        self.log_frame.place(x=305, y=5, width=520, height=150)                 
        self.log_text = tk.Text(self.log_frame, height=9, width=63, state=tk.DISABLED, wrap="none")
        scrollbar = ttk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log_frame.place_forget()
    def on_key_release(self, event):
        if self.on_username_typed:
            self.on_username_typed(event)
    def on_combo_select(self, event):
        if self.on_username_change:
            self.on_username_change(self.username_var_getter())                     
    def username_var_getter(self):
        return self.username_entry.get()
    def set_filter_callbacks(self, callback):
        self.chk_snap.config(command=lambda: callback("snapshot"))
        self.chk_alpha.config(command=lambda: callback("alpha"))
        self.chk_beta.config(command=lambda: callback("beta"))
        self.chk_special.config(command=lambda: callback("special"))
    def set_username_list(self, users):
        self.username_entry['values'] = users
    def set_username(self, name):
        self.username_entry.set(name)
    def get_username(self):
        return self.username_entry.get()
    def get_selected_version(self):
        return self.version_combo.get()
    def set_version_list(self, ids):
        self.version_combo['values'] = ids
        if ids:
            self.version_combo.current(0)
        else:
            self.version_combo.set("")
    def show_error(self, title, msg):
        messagebox.showerror(title, msg)
    def ask_yes_no(self, title, msg):
        return messagebox.askyesno(title, msg)
    def toggle_controls(self, state):
        s = "normal" if state else "disabled"
        self.username_entry.config(state=s)
        self.btn_launch.config(state=s)
        self.version_combo.config(state="readonly" if state else "disabled")
        self.btn_random_user.config(state=s)
    def log_message(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
    def show_log_window_if_hidden(self):
        if not self.log_frame.winfo_ismapped():
             self.log_frame.place(x=305, y=5, width=520, height=self._get_log_frame_height(True))                                   
             self.adjust_window_size_internal(log_visible=True, uuid_visible=self.uuid_val_label.winfo_ismapped())
    def set_layout(self, show_uuid, show_log):
        if show_uuid:
            self.label_uuid.place(x=40, y=95)
            self.uuid_val_label.place(x=120, y=95)
            self.move_buttons_for_uuid_visible()
        else:
            self.label_uuid.place_forget()
            self.uuid_val_label.place_forget()
            self.restore_buttons_original_position()
        if show_log:
            h = self._get_log_frame_height(show_uuid)
            self.log_frame.place(x=305, y=5, width=520, height=h)
        else:
            self.log_frame.place_forget()
        self.adjust_window_size_internal(show_log, show_uuid)
    def set_uuid(self, val):
        self.uuid_val_label.delete(0, tk.END)
        self.uuid_val_label.insert(0, val)
    def set_uuid_color(self, color):
        self.uuid_val_label.config(foreground=color)
    def set_username_color(self, color):
        self.username_entry.config(foreground=color)
    def move_buttons_for_uuid_visible(self):
        self.btn_launch.place(x=45, y=127)
        self.btn_close_game.place(x=155, y=127)
        self.btn_advanced.place(x=90, y=161)
    def restore_buttons_original_position(self):
        self.btn_launch.place(x=45, y=96)
        self.btn_close_game.place(x=155, y=96)
        self.btn_advanced.place(x=90, y=130)
    def _get_log_frame_height(self, uuid_visible):
        return 182 if uuid_visible else 150
    def adjust_window_size_internal(self, log_visible, uuid_visible):
        base_width = 830 if log_visible else 305
        base_height = 192 if uuid_visible else 160
        self.root.geometry(f"{base_width}x{base_height}")
        self.root.update_idletasks()
        self.root.after(10, lambda w=base_width, h=base_height: self.center_window(w, h))
    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    def create_advanced_options_window(self, current_jvm, current_java, current_dir, close_launcher, hide_log, enable_uuid, on_apply, on_cancel, on_delete_user, allow_delete):
        self.adv_window = tk.Toplevel(self.root)
        self.adv_window.title("Opciones Avanzadas")
        window_width = 340
        window_height = 246
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.adv_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.adv_window.resizable(False, False)
        try:
           self.adv_window.iconbitmap("icons/crafting_table.ico")
        except:
           pass
        self.adv_window.transient(self.root)
        self.adv_window.grab_set()
        main_frame = ttk.Frame(self.adv_window)
        main_frame.place(x=5, y=2, width=330, height=246)
        ttk.Label(main_frame, text="Argumentos JVM:", foreground="dark red").place(x=0, y=0)
        jvm_var = tk.StringVar(value=current_jvm)
        ttk.Entry(main_frame, textvariable=jvm_var, width=54).place(x=0, y=20)
        ttk.Label(main_frame, text="Ejecutable de Java:", foreground="dark red").place(x=0, y=42)
        java_var = tk.StringVar(value=current_java)
        ttk.Entry(main_frame, textvariable=java_var, width=41, state="readonly").place(x=0, y=62)
        ttk.Button(main_frame, text="Seleccionar", command=lambda: java_var.set(filedialog.askopenfilename(filetypes=[("Executables", "*.exe"), ("All Files", "*.*")]))).place(x=255, y=60)
        ttk.Label(main_frame, text="Directorio de Minecraft:", foreground="dark red").place(x=0, y=84)
        dir_var = tk.StringVar(value=current_dir)
        ttk.Entry(main_frame, textvariable=dir_var, width=41, state="readonly").place(x=0, y=104)
        ttk.Button(main_frame, text="Seleccionar", command=lambda: dir_var.set(filedialog.askdirectory())).place(x=255, y=102)
        close_var = tk.BooleanVar(value=close_launcher)
        ttk.Checkbutton(main_frame, text="Cerrar Minecito cuando inicie Minecraft.", variable=close_var).place(x=0, y=128)
        log_var = tk.BooleanVar(value=hide_log)
        ttk.Checkbutton(main_frame, text="Habilitar el registro.", variable=log_var).place(x=0, y=148)
        uuid_var = tk.BooleanVar(value=enable_uuid)
        ttk.Checkbutton(main_frame, text="Habilitar UUID.", variable=uuid_var).place(x=0, y=168)
        del_var = tk.BooleanVar(value=False)
        btn_del = ttk.Checkbutton(main_frame, text="Eliminar usuario actual.", variable=del_var)
        btn_del.place(x=0, y=188)
        if not allow_delete:
            btn_del.config(state="disabled")
        def apply():
            if del_var.get():
                on_delete_user({'del_user': True})
            else:
                on_apply({
                    'jvm': jvm_var.get(),
                    'java': java_var.get(),
                    'dir': dir_var.get(),
                    'close': close_var.get(),
                    'log_visible': log_var.get(),
                    'uuid_visible': uuid_var.get(),
                    'del_user': False
                })
        ttk.Button(main_frame, text="Aplicar", command=apply).place(x=85, y=210)
        ttk.Button(main_frame, text="Cancelar", command=self.close_adv_window).place(x=185, y=210)
    def close_adv_window(self):
        if hasattr(self, 'adv_window') and self.adv_window.winfo_exists():
            self.adv_window.destroy()
