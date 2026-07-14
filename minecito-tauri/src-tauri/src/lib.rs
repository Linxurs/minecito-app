use rand::Rng;
use std::process::Command;
use std::sync::Mutex;
use tauri::Emitter;
use tauri::Manager;
use mcl_rs::types::{MinecraftOptions, ProgressCallback};
use serde::{Deserialize, Serialize};

lazy_static::lazy_static! {
    static ref GAME_PROCESS: Mutex<Option<std::process::Child>> = Mutex::new(None);
}

// Struct to handle progress callbacks and emit them to the frontend
struct TauriCallback<R: tauri::Runtime> {
    app: tauri::AppHandle<R>,
}

impl<R: tauri::Runtime> ProgressCallback for TauriCallback<R> {
    fn set_status(&self, status: &str) {
        let _ = self.app.emit("install-status", status);
    }
    
    fn set_progress(&self, progress: i64) {
        let _ = self.app.emit("install-progress", progress);
    }
    
    fn set_max(&self, max: i64) {
        let _ = self.app.emit("install-max", max);
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserConfig {
    pub username: String,
    pub uuid: String,
    pub selected_version: String,
    pub type_version: String,
    pub advanced_options_directory: String,
    pub advanced_options_close_launcher: bool,
    pub hide_log: bool,
    pub enable_uuid: bool,
    pub jvm_args: String,
    pub java_executable: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LaunchOptions {
    pub username: String,
    pub uuid: String,
    pub version: String,
    pub jvm_args: String,
    pub java_executable: String,
    pub close_launcher: bool,
    pub game_directory: String,
}

fn get_default_mc_dir() -> std::path::PathBuf {
    std::path::PathBuf::from(mcl_rs::utils::get_minecraft_directory())
}

fn get_config_path(dir: &str) -> std::path::PathBuf {
    let mut p = std::path::PathBuf::from(dir);
    if p.as_os_str().is_empty() {
        p = get_default_mc_dir();
    }
    p.push("minecito_config.json");
    p
}

fn load_config(dir: &str) -> Vec<UserConfig> {
    let path = get_config_path(dir);
    if let Ok(data) = std::fs::read_to_string(&path) {
        if let Ok(users) = serde_json::from_str::<Vec<UserConfig>>(&data) {
            return users;
        }
        if let Ok(user) = serde_json::from_str::<UserConfig>(&data) {
            return vec![user];
        }
    }
    vec![]
}

fn save_config(dir: &str, users: &Vec<UserConfig>) -> Result<(), String> {
    let path = get_config_path(dir);
    if let Some(parent) = path.parent() {
        let _ = std::fs::create_dir_all(parent);
    }
    let data = serde_json::to_string_pretty(users).map_err(|e| e.to_string())?;
    std::fs::write(path, data).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn get_default_directory() -> String {
    get_default_mc_dir().to_string_lossy().to_string()
}

#[tauri::command]
fn get_users(dir: String) -> Vec<UserConfig> {
    load_config(&dir)
}

#[tauri::command]
fn save_user(dir: String, user: UserConfig) -> Result<(), String> {
    let mut users = load_config(&dir);
    users.retain(|u| u.username != user.username);
    users.push(user);
    save_config(&dir, &users)
}

#[tauri::command]
fn delete_user(dir: String, username: String) -> Result<(), String> {
    let mut users = load_config(&dir);
    users.retain(|u| u.username != username);
    save_config(&dir, &users)
}

#[tauri::command]
async fn launch_minecraft(app: tauri::AppHandle, options: LaunchOptions) -> Result<(), String> {
    let mc_dir = if options.game_directory.is_empty() {
        mcl_rs::utils::get_minecraft_directory()
    } else {
        std::path::PathBuf::from(options.game_directory.clone())
    };
        
    let mut version_json = mc_dir.clone();
    version_json.push("versions");
    version_json.push(&options.version);
    version_json.push(format!("{}.json", options.version));
    
    if version_json.exists() {
        println!("La versión {} ya está instalada. Omitiendo verificación.", options.version);
        let _ = app.emit("install-status", format!("La versión '{}' ya está lista.", options.version));
        
        let natives_path = mc_dir.join("versions").join(&options.version).join("natives");
        let _ = mcl_rs::natives::extract_natives(&options.version, &mc_dir, &natives_path);
    } else {
        println!("Iniciando instalación/verificación de la versión {}...", options.version);
        let callback = TauriCallback { app: app.clone() };
        
        mcl_rs::install::install_minecraft_version(&options.version, &mc_dir, &callback)
            .await
            .map_err(|e| format!("Error al instalar: {}", e))?;
            
        let natives_path = mc_dir.join("versions").join(&options.version).join("natives");
        let _ = mcl_rs::natives::extract_natives(&options.version, &mc_dir, &natives_path);
    }
        
    let mut mc_options = MinecraftOptions::default();
    mc_options.username = Some(options.username.clone());
    mc_options.uuid = Some(options.uuid.clone());
    
    let jvm_args: Vec<String> = options.jvm_args.split_whitespace().map(|s| s.to_string()).collect();
    if !jvm_args.is_empty() {
        mc_options.jvm_arguments = Some(jvm_args);
    }
    
    println!("Generando comando de lanzamiento...");
    let mut args = mcl_rs::command::get_minecraft_command(&options.version, &mc_dir, &mc_options)
        .map_err(|e| format!("Error al generar comando: {}", e))?;
        
    if args.is_empty() {
        return Err("El comando generado está vacío".into());
    }

    if !options.java_executable.is_empty() {
        args[0] = options.java_executable;
    }

    println!("Lanzando Minecraft...");
    let java_executable = &args[0];
    let java_args = &args[1..];
    
    let mut cmd = Command::new(java_executable);
    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW
    }
    
    #[cfg(not(target_os = "windows"))]
    let mut cmd = Command::new(java_executable);

    let mut log_file_stdout = std::fs::File::create(mc_dir.join("launcher_debug.log")).unwrap();
    let mut log_file_stderr = log_file_stdout.try_clone().unwrap();

    use std::io::Write;
    let cmd_str = format!("Comando de Minecraft ejecutado:\n{} {}", java_executable, java_args.join(" "));
    let _ = writeln!(log_file_stdout, "EXEC: {}", cmd_str);
    let _ = app.emit("game-log", cmd_str);

    let mut child = cmd.args(java_args)
       .current_dir(&mc_dir)
       .stdout(std::process::Stdio::piped())
       .stderr(std::process::Stdio::piped())
       .spawn()
       .map_err(|e| format!("Error al ejecutar Minecraft: {}", e))?;

    if let Some(stdout) = child.stdout.take() {
        let app_clone = app.clone();
        std::thread::spawn(move || {
            use std::io::{BufRead, BufReader, Write};
            let reader = BufReader::new(stdout);
            for line in reader.lines() {
                if let Ok(l) = line {
                    let _ = app_clone.emit("game-log", &l);
                    let _ = writeln!(log_file_stdout, "{}", l);
                }
            }
        });
    }

    if let Some(stderr) = child.stderr.take() {
        let app_clone = app.clone();
        std::thread::spawn(move || {
            use std::io::{BufRead, BufReader, Write};
            let reader = BufReader::new(stderr);
            for line in reader.lines() {
                if let Ok(l) = line {
                    let _ = app_clone.emit("game-log", format!("WARNING: {}", &l));
                    let _ = writeln!(log_file_stderr, "{}", l);
                }
            }
        });
    }

    {
        let mut process_guard = GAME_PROCESS.lock().unwrap();
        *process_guard = Some(child);
    }
    
    let app_clone = app.clone();
    std::thread::spawn(move || {
        loop {
            std::thread::sleep(std::time::Duration::from_millis(500));
            let should_break = {
                let mut guard = GAME_PROCESS.lock().unwrap();
                if let Some(ref mut child) = *guard {
                    match child.try_wait() {
                        Ok(Some(_)) => { *guard = None; true }
                        Ok(None) => false,
                        Err(_) => { *guard = None; true }
                    }
                } else {
                    true // killed externally
                }
            };
            if should_break {
                let _ = app_clone.emit("game-exited", ());
                break;
            }
        }
    });
        
    if options.close_launcher {
        app.exit(0);
    }
        
    Ok(())
}

#[tauri::command]
fn kill_minecraft() {
    let mut guard = GAME_PROCESS.lock().unwrap();
    if let Some(ref mut process) = *guard {
        let _ = process.kill();
        let _ = process.wait();
    }
    *guard = None;
}

#[tauri::command]
async fn get_versions() -> Result<Vec<mcl_rs::types::MinecraftVersionInfo>, String> {
    let mc_dir = mcl_rs::utils::get_minecraft_directory();
    let client = reqwest::Client::new();
    let mojang_versions = mcl_rs::utils::get_available_versions(&client, &mc_dir)
        .await
        .map_err(|e| e.to_string())?;
    Ok(mojang_versions)
}

#[tauri::command]
fn generate_random_user() -> String {
    let adjectives = [
        "Bill", "Cal", "Dar", "Fun", "Gen", "Gol", "Happy", "Hol", "Krit",
        "Mig", "Nus", "Sad", "Ser", "Shy", "Sil", "Smad", "Swy", "Thom",
    ];
    let nouns = [
        "Bird", "Blast", "Cat", "Dog", "Dolly", "Don", "Elephy", "Fish",
        "Gra", "Lio", "Moo", "Nick", "Nill", "Phel", "Star", "Story",
        "Turly", "Vey", "White", "Win", "Znack",
    ];
    
    let mut rng = rand::thread_rng();
    let adj = adjectives[rng.gen_range(0..adjectives.len())];
    let noun = nouns[rng.gen_range(0..nouns.len())];
    let num = rng.gen_range(10..100);
    
    let name = format!("{}as{}{}", adj, noun, num);
    name.chars().take(15).collect()
}

#[tauri::command]
fn resize_window(app: tauri::AppHandle, width: f64, height: f64) {
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.set_size(tauri::Size::Logical(tauri::LogicalSize::new(width, height)));
        let _ = window.center();
    }
}

#[tauri::command]
async fn close_advanced_options(app: tauri::AppHandle) {
    if let Some(w) = app.get_webview_window("advanced") {
        let _ = w.close();
    }
}

#[tauri::command]
async fn open_advanced_options(app: tauri::AppHandle) -> Result<(), String> {
    if app.get_webview_window("advanced").is_none() {
        tauri::WebviewWindowBuilder::new(
            &app,
            "advanced",
            tauri::WebviewUrl::App("advanced.html".into())
        )
        .title("Opciones Avanzadas")
        .inner_size(340.0, 250.0)
        .resizable(false)
        .center()
        .icon({
            let icon_bytes = include_bytes!("../../../icons/crafting_table.ico");
            let img = image::load_from_memory_with_format(icon_bytes, image::ImageFormat::Ico).unwrap();
            let rgba = img.to_rgba8();
            let width = rgba.width();
            let height = rgba.height();
            tauri::image::Image::new_owned(rgba.into_raw(), width, height)
        }).unwrap()
        .build()
        .map_err(|e| e.to_string())?;
    } else {
        if let Some(w) = app.get_webview_window("advanced") {
            let _ = w.set_focus();
        }
    }
    Ok(())
}

#[tauri::command]
fn generate_uuid_for_username(username: String) -> String {
    let ns = uuid::Uuid::NAMESPACE_DNS;
    uuid::Uuid::new_v5(&ns, username.as_bytes()).to_string()
}

#[tauri::command]
fn ask_confirm(title: String, message: String) -> bool {
    rfd::MessageDialog::new()
        .set_title(&title)
        .set_description(&message)
        .set_buttons(rfd::MessageButtons::YesNo)
        .show() == rfd::MessageDialogResult::Yes
}

#[tauri::command]
fn select_java_file() -> Option<String> {
    rfd::FileDialog::new()
        .add_filter("Ejecutables Java", &["exe"])
        .pick_file()
        .map(|p| p.to_string_lossy().into_owned())
}

#[tauri::command]
fn force_close(app: tauri::AppHandle) {
    app.exit(0);
}

#[tauri::command]
fn select_minecraft_directory() -> Option<String> {
    rfd::FileDialog::new()
        .pick_folder()
        .map(|p| p.to_string_lossy().into_owned())
}

#[tauri::command]
fn resolve_java_path(version: String, game_dir: String) -> String {
    let mut parts: Vec<i32> = Vec::new();
    for p in version.split(&['.', '-'][..]) {
        if let Ok(n) = p.parse::<i32>() {
            parts.push(n);
        }
    }
    
    let runtime_name = if version.starts_with("a1.") || version.starts_with("b1.") || version.starts_with("infdev") || version.starts_with("c0.") {
        "jre-legacy"
    } else if version.contains("w") && parts.len() < 2 {
        let prefix = version.split("w").next().unwrap_or("");
        if let Ok(n) = prefix.parse::<i32>() {
            if n >= 21 { "java-runtime-alpha" } else { "jre-legacy" }
        } else {
            "jre-legacy"
        }
    } else if parts.is_empty() {
        "java-runtime-delta"
    } else {
        let major = parts[0];
        let minor = if parts.len() > 1 { parts[1] } else { 0 };
        if major == 1 {
            if minor <= 16 {
                "jre-legacy"
            } else if minor == 17 {
                "java-runtime-alpha"
            } else if minor >= 18 && minor <= 20 {
                if minor == 20 && parts.len() > 2 && parts[2] >= 5 {
                    "java-runtime-delta"
                } else {
                    "java-runtime-beta"
                }
            } else {
                "java-runtime-delta"
            }
        } else {
            "java-runtime-delta"
        }
    };
    
    let base_dir = if game_dir.is_empty() { get_default_mc_dir() } else { std::path::PathBuf::from(game_dir) };
    let mut path = base_dir;
    path.push("runtime");
    path.push(runtime_name);
    path.push("windows-x64");
    path.push(runtime_name);
    path.push("bin");
    path.push("javaw.exe");
    
    if path.exists() {
        path.to_string_lossy().into_owned()
    } else {
        "javaw.exe".to_string()
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .on_window_event(|window, event| match event {
            tauri::WindowEvent::CloseRequested { api, .. } => {
                if window.label() == "main" {
                    let _ = window.emit("save-and-close", ());
                    api.prevent_close();
                }
            }
            _ => {}
        })
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            force_close,
            ask_confirm,
            get_default_directory,
            get_users,
            save_user,
            delete_user,
            launch_minecraft,
            kill_minecraft,
            get_versions,
            generate_random_user,
            generate_uuid_for_username,
            select_java_file,
            select_minecraft_directory,
            resolve_java_path, resize_window, open_advanced_options, close_advanced_options])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");









}
