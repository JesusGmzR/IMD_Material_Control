# 🏭 IMD Material Change Control System

Sistema de control de cambios de material para máquinas AXIAL y RADIAL en procesos de manufactura IMD (In-Mold Decoration).

## 📋 Descripción

Aplicación full-stack que permite gestionar y validar cambios de material en líneas de producción mediante escaneo de códigos QR, con validación en tiempo real de feeders y polaridad de componentes.

## 🚀 Características Principales

- ✅ **Interfaz dual** para máquinas AXIAL y RADIAL
- ✅ **Escaneo QR** para almacén, proveedor, lote, feeder, polaridad y persona
- ✅ **Validación en tiempo real** de feeders y polaridad contra base de datos
- ✅ **Feedback visual** con colores (verde/rojo) según validación
- ✅ **Historial completo** de cambios de material
- ✅ **UI responsiva** con tema oscuro y tipografía LG EI
- ✅ **Modal automático** con cierre temporizado para confirmaciones

## 🛠️ Tecnologías

### Frontend
- **HTML5** + **Bootstrap 5**
- **JavaScript ES6** para lógica de interfaz
- **CSS3** con variables personalizadas y tema oscuro
- **Responsive Design** para dispositivos móviles y desktop

### Backend
- **Python 3.8+**
- **Flask** como servidor web
- **MySQL** para base de datos
- **CORS** habilitado para desarrollo

### Base de Datos
- **MySQL** con 483 registros de ubicaciones de feeders
- **Tabla de historial** para seguimiento de cambios
- **Validación cruzada** entre números de parte y configuraciones

## 📦 Instalación

### Prerrequisitos
- Python 3.8 o superior
- MySQL Server
- Git

### 1. Clonar el repositorio
```bash
git clone https://github.com/[tu-usuario]/imd-material-control.git
cd imd-material-control
```

### 2. Crear entorno virtual
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install flask flask-cors mysql-connector-python pandas openpyxl
```

### 4. Configurar base de datos
- Crear base de datos MySQL
- Actualizar credenciales en `app.py`:
```python
'host': 'tu-host-mysql',
'user': 'tu-usuario',
'password': 'tu-password',
'database': 'tu-base-datos'
```

### 5. Cargar datos iniciales (opcional)
```bash
python load_excel_to_mysql.py
```

## 🚀 Uso

### 1. Iniciar el servidor
```bash
python app.py
```
El servidor estará disponible en `http://localhost:5000`

### 2. Abrir la interfaz
```bash
# Servidor HTTP para archivos estáticos
python -m http.server 8000
```
Abrir en navegador: `http://localhost:8000/IMD_Control%20Cambio%20Material.html`

### 3. Flujo de trabajo
1. **Escanear QR almacén** → Se carga automáticamente la polaridad esperada
2. **Escanear QR proveedor** → Información del proveedor
3. **Escanear lote proveedor** → Número de lote
4. **Escanear feeder** → Validación automática contra base de datos
5. **Escanear polaridad** → Validación y cambio de color según coincidencia
6. **Escanear persona** → Operador responsable
7. **Clic en CAMBIAR** → Guarda el registro y limpia los campos

## 📁 Estructura del Proyecto

```
imd-material-control/
├── .venv/                          # Entorno virtual (ignorado)
├── .gitignore                      # Archivos excluidos de Git
├── app.py                          # Servidor Flask (backend)
├── app.js                          # Lógica frontend
├── IMD_Control Cambio Material.html # Interfaz principal
├── ReferenciaCSS_bootstrap.css     # Estilos personalizados
├── load_excel_to_mysql.py          # Script de carga de datos
├── imd_feeders_location_data_spec.xlsx # Datos de feeders (si existe)
└── README.md                       # Este archivo
```

## 🔧 API Endpoints

### GET `/api/health`
Verificación de estado del servidor

### POST `/api/search-part`
Busca información de parte por QR almacén
```json
{
  "qr_almacen": "ABC123",
  "machine": "AXIAL"
}
```

### POST `/api/validate-feeder`
Valida feeder escaneado
```json
{
  "part_number": "ABC123",
  "feeder_scanned": "A1",
  "machine": "AXIAL"
}
```

### POST `/api/validate-polarity`
Valida polaridad escaneada
```json
{
  "part_number": "ABC123",
  "polarity_scanned": "+",
  "machine": "AXIAL"
}
```

### POST `/api/save-history`
Guarda registro en historial
```json
{
  "posicion_de_feeder": "AXIAL_A1",
  "qr_almacen": "ABC123",
  "numero_de_parte": "ABC123",
  "spec": "SPEC001",
  "qr_de_proveedor": "PRV456",
  "numero_de_lote_proveedor": "LOT789",
  "polaridad": "+",
  "persona": "OPERATOR1"
}
```

## 🎨 Características de UI

- **Tema oscuro** con colores corporativos
- **Tipografía LG EI** con escalado rem
- **Feedback visual**: Verde para validaciones correctas, rojo para errores
- **Hover persistente** en campos con errores
- **Modal automático** que se cierra en 2 segundos
- **Diseño responsivo** para móvil y desktop

## 🔐 Seguridad

- Validación en servidor para todos los datos
- Conexión segura a base de datos
- Manejo de errores robusto
- CORS configurado para desarrollo

## 📊 Base de Datos

### Tabla: `imd_feeders_location_data`
- `numero_de_parte`: Número de parte del componente
- `spec`: Especificación técnica
- `posicion_de_feeder`: Ubicación del feeder (AXIAL/RADIAL_XX)
- `polarity`: Polaridad esperada del componente

### Tabla: `material_change_history`
- Registro completo de todos los cambios de material
- Timestamp automático de cada operación
- Trazabilidad completa del proceso

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es propiedad de ILSAN MES y está destinado para uso interno.

## 📞 Contacto

- **Desarrollador**: ILSAN MES Admin
- **Email**: admin@ilsan.mes
- **Proyecto**: Sistema de Control IMD

---

⚡ **Desarrollado con Flask + Bootstrap para ILSAN MES** ⚡