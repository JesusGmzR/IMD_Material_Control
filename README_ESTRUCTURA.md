# IMD Material Control - Aplicación Integrada

## Estructura Simplificada

Esta aplicación ahora está completamente integrada en un solo archivo principal para mayor simplicidad y facilidad de distribución.

### Archivos Principales

- **`imd_desktop_main.py`** - Script principal que contiene:
  - Configuración de la aplicación (anteriormente `config.py`)
  - Backend Flask con todas las APIs
  - Frontend completo (HTML, CSS, JavaScript embebido)
  - Lógica de ventana PyWebView
  - Conexión a base de datos MySQL

- **`icono_app.png`** - Icono de la aplicación
- **`ImagenLogo1.png`** - Logo adicional de la aplicación
- **`compile_app.bat`** - Script para compilar a ejecutable
- **`imd_app.spec`** - Especificación para PyInstaller
- **`version_info.txt`** - Información de versión

### Archivos de Desarrollo

- **`.venv/`** - Entorno virtual de Python
- **`build/`** y **`dist/`** - Directorios de compilación
- **`.gitignore`** - Archivos ignorados por Git
- **`README.md`** - Documentación principal

### Carpeta Backup

- **`backup/`** - Contiene todos los archivos anteriores separados:
  - `config.py` - Configuración antigua (ahora integrada)
  - `app.py` - Backend Flask separado (ahora integrado)
  - `app.js` - JavaScript separado (ahora embebido)
  - `*.html` - Archivos HTML separados (ahora embebido)
  - `*.css` - Estilos separados (ahora embebidos)
  - Otros archivos de desarrollo y pruebas

## Ventajas de la Nueva Estructura

1. **Simplicidad**: Todo en un solo archivo principal
2. **Facilidad de distribución**: Solo necesitas `imd_desktop_main.py` e imágenes
3. **Menos dependencias**: No hay archivos externos que puedan perderse
4. **Mantenimiento**: Más fácil de mantener y actualizar
5. **Compilación**: Proceso de compilación más limpio

## Cómo Ejecutar

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Ejecutar aplicación
python imd_desktop_main.py
```

## Cómo Compilar

```bash
# Ejecutar script de compilación
.\compile_app.bat
```

El ejecutable se generará en `dist/IMD_MaterialControl.exe`

## Notas Técnicas

- La aplicación ahora usa Edge Chromium como motor de renderizado por defecto
- Toda la configuración está embebida en el script principal
- El frontend (HTML/CSS/JS) está completamente integrado
- La base de datos MySQL en la nube se mantiene igual
- Los logs se siguen generando en `~/IMD_Logs/`

## Historial de Archivos

Todos los archivos anteriores se mantienen en `backup/` para referencia histórica y pueden ser restaurados si es necesario.