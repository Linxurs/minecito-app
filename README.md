# ✨ Minecito Launcher (Tauri + Rust) ✨

[![Rust Version][rust-badge]][rust-link] [![Tauri Version][tauri-badge]][tauri-link] [![License: MIT][license-badge]][license-link] [![Issues][issues-badge]][issues-link]

> La experiencia de Minecraft, llevada al siguiente nivel. **Minecito** ha evolucionado de un script en Python a una **aplicación nativa ultrarrápida** construida con **Tauri y Rust**. Olvídate de los lanzadores pesados y las interfaces lentas; Minecito te ofrece rendimiento puro, control total y una experiencia de usuario instantánea.

---

## 🚀 ¿Por Qué la Nueva Versión en Rust?

Hemos reescrito Minecito desde cero utilizando **Tauri** (para la interfaz web ligera) y **Rust** (para el backend de alto rendimiento). Esto soluciona todos los problemas de latencia y consumo de recursos de los lanzadores tradicionales.

*   ⚡ **Arranque Instantáneo:** Carga de usuarios y perfiles en milisegundos gracias al procesamiento asíncrono y en paralelo.
*   🦀 **Librería Nativa `mcl_rs`:** Hemos traducido y adaptado la lógica de la famosa `minecraft_launcher_lib` directamente a Rust, creando un submódulo independiente y extremadamente rápido para la descarga de recursos y resolución de dependencias.
*   📝 **Logs en Tiempo Real:** El backend de Rust captura la salida `stdout` y `stderr` de Java a través de tuberías (pipes) y las retransmite en vivo a la interfaz, guardando simultáneamente una copia física en `launcher_debug.log`.
*   🔧 **Personalización sin Límites:** Argumentos JVM personalizados, gestión de directorios, asignación de UUID y selección manual/automática del runtime de Java óptimo para cada versión de Minecraft.
*   🎮 **Soporte Total:** Desde `Alpha` y `Beta` hasta `Snapshots` y versiones modificadas (como *Fabric*, *Forge* o *Quilt*).
*   🎲 **Generación de Nombres Inteligente:** Generación de nombres de usuario aleatorios únicos (ej. *HappyasCat42*) gestionada de forma inteligente sin saturar tu historial de perfiles guardados.

---

## 🏗️ Arquitectura

El proyecto se divide en tres piezas fundamentales:
1. **Frontend (Tauri/HTML/CSS/JS):** Interfaz limpia, minimalista y libre de frameworks pesados. Todo está diseñado con Vanilla JS y flexbox para garantizar el máximo rendimiento del WebView.
2. **Backend (Rust):** Administra la ejecución de procesos, eventos de IPC (Inter-Process Communication), creación de ventanas y llamadas del sistema operativo.
3. **mcl_rs (Submódulo):** Una [librería hermana en Rust](https://github.com/Linxurs/minecraft_launcher_lib_rs) que gestiona la estructura de directorios de Minecraft, descarga de *assets*, extracción de *Natives* y armado del comando final de ejecución de Java.

---

## 🛠️ Instalación y Compilación

Para compilar este proyecto desde el código fuente, necesitarás tener instalado el entorno de desarrollo de Rust y las herramientas de compilación de Tauri.

**1. Prerrequisitos:**
*   [Rust y Cargo](https://rustup.rs/) (Versión estable más reciente)
*   [Herramientas de compilación para Windows (C++)](https://visualstudio.microsoft.com/es/visual-cpp-build-tools/) o las equivalentes en tu sistema operativo para Tauri.

**2. Clonar el repositorio (con submódulos):**
Dado que usamos `mcl_rs` como submódulo, asegúrate de clonarlo con la bandera `--recursive`:
```bash
git clone --recursive https://github.com/Linxurs/minecito-app.git
cd minecito-app
```

**3. Compilar el ejecutable:**
Navega hasta la carpeta del proyecto Tauri y ejecuta el comando de construcción:
```bash
cd minecito-tauri/src-tauri
cargo tauri build
```
Una vez finalizado, encontrarás el ejecutable `.exe` nativo y ultra optimizado en la carpeta `target/release/`.

---

## 📖 Guía de Uso

1.  **Nombre de Usuario:** Selecciona tu perfil del menú desplegable o presiona el botón **"R"** para jugar como invitado con un nombre aleatorio.
2.  **Versión:** Elige tu versión de Minecraft. Activa las casillas `Snapshot`, `Beta`, `Alpha` o `Especial` para descubrir versiones ocultas o modloaders.
3.  **¡A Jugar!:** Haz clic en el botón principal. Minecito descargará cualquier archivo faltante y abrirá el juego. Podrás ver todo el proceso detallado en la ventana de logs.
4.  **Opciones Avanzadas:** Configura tus directorios alternativos de instalación o personaliza los argumentos de la JVM a tu gusto.

---

## 🤝 Contribuir

¡Toda ayuda es bienvenida! Si quieres mejorar el backend en Rust o pulir la interfaz, siéntete libre de abrir un *Pull Request*.

1.  Haz un Fork del repositorio.
2.  Crea una nueva rama (`git checkout -b feature/nueva-idea`).
3.  Haz tus cambios y commits (`git commit -m 'feat: Añade soporte para X'`).
4.  Sube la rama (`git push origin feature/nueva-idea`).
5.  Abre un **Pull Request**.

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Eres libre de usarlo, modificarlo y distribuirlo.

[rust-badge]: https://img.shields.io/badge/Rust-1.70%2B-orange?style=for-the-badge&logo=rust
[rust-link]: https://www.rust-lang.org/
[tauri-badge]: https://img.shields.io/badge/Tauri-2.0-FFC131?style=for-the-badge&logo=tauri&logoColor=white
[tauri-link]: https://tauri.app/
[license-badge]: https://img.shields.io/badge/License-MIT-green?style=for-the-badge
[license-link]: https://opensource.org/licenses/MIT
[issues-badge]: https://img.shields.io/github/issues/Linxurs/minecito-app?style=for-the-badge&logo=github
[issues-link]: https://github.com/Linxurs/minecito-app/issues