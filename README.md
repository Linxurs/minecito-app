# Minecito App

## Descripción
Minecito App es un lanzador de Minecraft simple, diseñado para proporcionar una interfaz básica para iniciar diferentes versiones de Minecraft. Este lanzador permite a los usuarios seleccionar un nombre de usuario, elegir una versión de Minecraft y configurar opciones básicas de lanzamiento.

## Características
*   Selección de nombre de usuario.
*   Selección de versiones de Minecraft (release, snapshot, alpha, beta, especial).
*   Configuración de argumentos JVM.
*   Selección del ejecutable de Java.
*   Gestión de perfiles de usuario.
*   Registro de eventos del lanzamiento.

## Instalación

### Requisitos
*   Python 3.x
*   pip (gestor de paquetes de Python)

### Pasos de Instalación

1.  **Clonar el repositorio (o descargar el código):**
    ```bash
    git clone https://github.com/Linxurs/minecito-app.git
    cd minecito-app
    ```
    *Nota: Si descargaste un archivo ZIP, descomprímelo y navega hasta la carpeta raíz del proyecto.*

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Cómo Ejecutar
Para iniciar el lanzador, ejecuta el siguiente comando desde la carpeta raíz del proyecto:

```bash
python mc_main.py
```

## Dependencias
Las principales dependencias del proyecto están listadas en `requirements.txt`:
*   `minecraft_launcher_lib`: Biblioteca para interactuar con las funciones de lanzamiento de Minecraft.

## Actualización (si aplica)
Este proyecto puede incluir un script `update.bat` para actualizarse a sí mismo. Ejecútalo si necesitas la versión más reciente:

```bash
update.bat
```

## Contribución
Las contribuciones son bienvenidas. Por favor, crea un "issue" para discutir los cambios propuestos.

## Licencia
[Pendiente: Especificar licencia, por ejemplo, MIT, GPL, etc.]
