# ✨ Minecito Launcher ✨

[![Python Version][python-badge]][python-link] [![License: MIT][license-badge]][license-link] [![Issues][issues-badge]][issues-link] [![Last Commit][last-commit-badge]][repo-link]

> La experiencia de Minecraft, redefinida. Minecito es un lanzador minimalista, ultrarrápido y extremadamente personalizable, diseñado para jugadores que valoran el rendimiento, el control y la eficiencia. Olvídate de los lanzadores pesados y restrictivos; Minecito te devuelve el poder.

![Minecito UI Screenshot](https://i.imgur.com/your-screenshot-placeholder.png)
*(Aquí iría una espectacular captura de pantalla de la interfaz de Minecito en acción)*

---

## 🚀 ¿Por Qué Minecito es Superior?

Minecito no es solo otro lanzador. Es una declaración de principios. Es la herramienta definitiva para el verdadero aficionado de Minecraft, creada con una filosofía de **rendimiento y control total**.

*   ⚡ **Velocidad Extrema:** Construido en Python con una ligera interfaz Tkinter, Minecito se inicia en un parpadeo y consume recursos mínimos. Más poder para tu juego, menos para el lanzador.
*   🔧 **Personalización sin Límites:**
    *   **Argumentos JVM a tu Medida:** Optimiza el rendimiento de Java con total libertad.
    *   **Control Total de Directorios:** Gestiona tus instalaciones de Minecraft donde quieras.
    *   **Selección de Java:** Elige manualmente tu ejecutable de Java o deja que Minecito lo haga por ti.
*   🧠 **Gestión Inteligente de Java:** Minecito detecta automáticamente la versión de Minecraft que quieres jugar y selecciona el runtime de Java adecuado (`jre-legacy`, `java-runtime-alpha`, `beta`, `delta`), basándose en las especificaciones oficiales de Mojang. ¡Se acabaron los errores de versión de Java!
*   🎮 **Compatibilidad Universal:**
    *   Lanza cualquier versión de Minecraft: desde las nostálgicas `Alpha` y `Beta` hasta las últimas `snapshots`.
    *   Soporte nativo para versiones con mods (`Fabric`, `Forge`, `Quilt`, `NeoForge`). Minecito extrae la versión base y utiliza el Java correcto.
*   👤 **Gestión de Perfiles Simplificada:** Guarda y carga tus configuraciones por usuario. Cada jugador tiene su propio entorno, sus propias reglas.
*   🕵️ **Modo Offline:** Juega con cualquier nombre de usuario y UUID, ideal para pruebas de desarrollo o para jugar sin conexión.

---

## 🛠️ Instalación y Puesta en Marcha

Poner en marcha esta maravilla es tan simple como un bloque de tierra.

**1. Prerrequisitos:**
Asegúrate de tener [Python 3.10+](https://www.python.org/downloads/) instalado.

**2. Clona el Repositorio:**
```bash
git clone https://github.com/Linxurs/minecito-app.git
cd minecito-app
```

**3. Instala las Dependencias:**
Minecito depende de la legendaria `minecraft-launcher-lib`. Instálala junto con otras necesidades:
```bash
pip install -r requirements.txt
```

**4. ¡Lanza la Magia!**
```bash
python mc_main.py
```
¡Y listo! La interfaz elegante y potente de Minecito aparecerá ante ti.

---

## 📖 Guía de Uso

La interfaz ha sido diseñada para ser intuitiva y poderosa:

1.  **Nombre de Usuario:** Escribe tu nombre de usuario o presiona el botón **"R"** para generar uno aleatorio y único.
2.  **Selección de Versión:** Elige tu versión de Minecraft. Usa los checkboxes (`Snapshot`, `Beta`, `Alpha`, `Especial`) para filtrar la lista a tu gusto.
3.  **¡A Jugar!:** Presiona **"¡Iniciar Minecraft!"**. Minecito se encargará de todo, desde instalar la versión si es necesario hasta configurar el entorno de Java correcto.
4.  **Opciones Avanzadas:** Aquí es donde reside el verdadero poder. Configura tus argumentos JVM, directorios y más.

---

## 🤝 Contribuye a la Leyenda

Minecito es un proyecto vivo que busca la perfección. Si tienes una idea, una mejora o una corrección, tu contribución es bienvenida.

1.  **Haz un Fork** del repositorio.
2.  Crea una nueva rama (`git checkout -b feature/nombre-de-tu-feature`).
3.  Realiza tus cambios y haz commit (`git commit -m 'feat: Añade una nueva característica increíble'`).
4.  Haz un Push a tu rama (`git push origin feature/nombre-de-tu-feature`).
5.  Abre un **Pull Request**.

---

## 🏗️ Construido Con

*   **[Python](https://www.python.org/)** - El motor de toda la operación.
*   **[Tkinter](https://docs.python.org/3/library/tkinter.html)** - Para una interfaz gráfica de usuario ligera y nativa.
*   **[minecraft-launcher-lib](https://github.com/minecraft-launcher-lib/minecraft-launcher-lib)** - La biblioteca que hace posible la magia de lanzar Minecraft.

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Eres libre de usarlo, modificarlo y distribuirlo. Consulta el archivo `LICENSE` para más detalles.

[python-badge]: https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python
[python-link]: https://www.python.org/
[license-badge]: https://img.shields.io/badge/License-MIT-green?style=for-the-badge
[license-link]: https://opensource.org/licenses/MIT
[issues-badge]: https://img.shields.io/github/issues/Linxurs/minecito-app?style=for-the-badge&logo=github
[issues-link]: https://github.com/Linxurs/minecito-app/issues
[last-commit-badge]: https://img.shields.io/github/last-commit/Linxurs/minecito-app?style=for-the-badge&logo=github
[repo-link]: https://github.com/Linxurs/minecito-app