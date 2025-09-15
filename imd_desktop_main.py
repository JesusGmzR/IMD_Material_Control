#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IMD Material Control Desktop Application
Aplicación de escritorio que combina Flask backend con pywebview frontend
Versión de producción optimizada para múltiples PCs
"""

import os
import sys
import threading
import time
import webview
import socket
import logging
import signal
import multiprocessing
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from datetime import datetime
from config import ProductionConfig

# Configurar logging
def setup_logging():
    """Configura el sistema de logging"""
    log_dir = os.path.dirname(ProductionConfig.LOG_CONFIG['file_path'])
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, ProductionConfig.LOG_CONFIG['level']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(ProductionConfig.LOG_CONFIG['file_path']),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

# Inicializar logging
logger = setup_logging()

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)

# Configuración de la aplicación desde config.py
# Usar configuración de base de datos en la nube para distribución
db_config = {
    'host': 'up-de-fra1-mysql-1.db.run-on-seenode.com',
    'port': 11550,
    'database': 'db_rrpq0erbdujn',
    'user': 'db_rrpq0erbdujn',
    'password': '5fUNbSRcPP3LN9K2I33Pr0ge',
    'charset': 'utf8mb4',
    'use_unicode': True
}

# Función para obtener conexión a la base de datos
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        logger.error(f"Error conectando a la base de datos: {err}")
        return None

# Función para crear tabla de historial si no existe
def create_history_table():
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS material_change_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                posicion_de_feeder VARCHAR(50) NOT NULL,
                qr_almacen VARCHAR(200) NOT NULL,
                numero_de_parte VARCHAR(100) NOT NULL,
                spec VARCHAR(100),
                qr_de_proveedor VARCHAR(200),
                numero_de_lote_proveedor VARCHAR(100),
                polaridad VARCHAR(10),
                persona VARCHAR(100),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_part_number (numero_de_parte),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            cursor.execute(create_table_query)
            connection.commit()
            cursor.close()
            connection.close()
            logger.info("Tabla de historial creada/verificada exitosamente")
    except Exception as e:
        logger.error(f"Error creando tabla de historial: {e}")

# Ruta principal que sirve la aplicación
@app.route('/')
def index():
    try:
        # HTML embebido con diseño original restaurado
        html_content = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>IMD Material Control - Desktop App</title>
  <!-- Bootstrap 5 -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  
  <!-- CSS Embebido -->
  <style>
/* Versión Bootstrap de los estilos personalizados (ReferenciaCSS_bootstrap.css)
   Mantiene la identidad de colores y un tema oscuro ligero sobre Bootstrap 5 */

:root {
  --axial-primary: #3b82f6;
  --axial-primary-hover: #2563eb;
  --radial-primary: #f97316;
  --radial-primary-hover: #ea580c;
  --bg-dark: #32323E;
  --card-dark: #2d2d2d;
  --border-dark: #404040;
  /* Tipografía base */
  --font-base: 'LG EI', 'LG Regular', system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,'Noto Sans',sans-serif;
  /* Escala tipográfica (1rem = 25px) */
  --fs-2xs: 0.52rem; /* ~13px */
  --fs-xs: 0.6rem;   /* 15px */
  --fs-sm: 0.68rem;  /* 17px */
  --fs-base: 0.75rem;/* 18.75px */
  --fs-md: 0.85rem;  /* 21.25px */
  --fs-lg: 0.95rem;  /* 23.75px */
  --fs-xl: 1.1rem;   /* 27.5px */
  --fs-2xl: 1.25rem; /* 31.25px */
}

html { font-size: 25px; }
body.app-bg {
  background: var(--bg-dark);
  color: #d7d7d7;
  min-height: 100vh;
  font-family: var(--font-base);
  line-height:1.35;
}

h1,h2,h3,h4,h5,h6 { color: #fff; font-family: var(--font-base); font-weight:600; }

/* Tarjetas oscuras */
.card-dark { background: var(--card-dark); border: 1px solid var(--border-dark); }
.card-dark .card-header { border-bottom: 1px solid var(--border-dark); }

/* Encabezados de máquina */
.axial-primary { background: var(--axial-primary) !important; color:#fff; }
.axial-primary.hover-able:hover { background: var(--axial-primary-hover)!important; }
.radial-primary { background: var(--radial-primary)!important; color:#fff; }
.radial-primary.hover-able:hover { background: var(--radial-primary-hover)!important; }

/* Etiquetas laterales de los campos de escaneo */
.scan-pair { display:flex; gap:.5rem; }
.scan-label { width:7.6rem; min-width:7.6rem; background:#475569; color:#f3f4f6; font-size:var(--fs-xs); border-radius:.45rem; display:flex; align-items:center; padding:0 .9rem; font-weight:600; font-family: var(--font-base); }
.scan-input { flex:1; height: 1.8rem; }
.scan-input .form-control { background:#111827; border:1px solid var(--border-dark); color:#fff; font-size: var(--fs-xs); height:1.8rem; padding:.55rem .9rem; font-family: var(--font-base); }
.scan-input .form-control:focus { border-color: var(--axial-primary); box-shadow:0 0 0 .2rem rgba(59,130,246,.25); }
.machine-radial .scan-input .form-control:focus { border-color: var(--radial-primary); box-shadow:0 0 0 .2rem rgba(249,115,22,.25); }

/* Bloques de visualización (Polaridad / Resultado) */
.display-block-title { background:#4b5563; color:#d1d5db; text-align:center; padding: .25rem .45rem .25rem .45rem; border-radius:.375rem .375rem 0 0 ; font-size:var(--fs-xl); font-weight:600; font-family: var(--font-base); }
.display-block { background:#111827; height: 6.56rem; border-radius: 0 0 .65rem .65rem; display:flex; align-items:center; justify-content:center; position:relative; }
.display-block .result-ok { position:absolute; right:.75rem; bottom:.55rem; color:#22c55e; font-size:var(--fs-xl); font-weight:700; }

/* Botón CAMBIAR (ampliado) */
.btn-change { background:#3B7D23; color:#d1d5db; border:1px solid #6b7280; font-weight:600; font-size:var(--fs-xl); padding: .25rem 1.1rem 0.25rem 1.1rem; letter-spacing:.5px; border-radius:.65rem; transition:background .18s ease, transform .15s ease; font-family: var(--font-base); }
.btn-change:hover { background:#499C2C; color:#fff; transform:translateY(-2px); }
.btn-change:active { transform:translateY(0); }

/* Utilidades pequeñas */
.small-title { font-size: var(--fs-xl); font-weight:600; margin-bottom:1rem; font-family: var(--font-base); }
.spacing-y > * + * { margin-top:.75rem; }

/* Aumento de tamaño de fuente dentro del bloque de datos escaneados */
.card .row.flex-grow-1 { font-size: var(--fs-xl); }
/* Ajuste específico de etiquetas e inputs dentro del aumento general */
.card .row.flex-grow-1 .scan-label { font-size: var(--fs-xs); }
.card .row.flex-grow-1 .scan-input .form-control { font-size:var(--fs-sm); }

/* Cards de máquina */
.card-body.d-flex.flex-column { min-height: 20rem;}

/* Responsivo */
@media (max-width: 576px) {
  html { font-size:25px; }
  .scan-label { width:5.6rem; min-width:5.6rem; font-size:var(--fs-2xs); padding:0 .65rem; }
  .scan-input .form-control { height:1.76rem; font-size:var(--fs-md); }
  .display-block { height:5.2rem; }
  .btn-change { font-size:var(--fs-lg); padding:.85rem 1.5rem; }
}
::placeholder {
  color: #9ca3af !important;
  opacity: .55 !important; /* Mejor legibilidad */
  font-size: var(--fs-xs);
  font-family: var(--font-base);
}
.font-lg-ei { font-family: var(--font-base) !important; }
.instructions { font-size: var(--fs-base); font-weight:500; margin: .5rem 0 1rem; color:#e2e8f0; }

/* Enlace de salto (skip link) */
.skip-link { position:absolute; left:-999px; top:auto; width:1px; height:1px; overflow:hidden; }
.skip-link:focus { position:static; width:auto; height:auto; padding:.5rem 1rem; background:#111827; color:#fff; z-index:1000; border:2px solid var(--axial-primary); border-radius:.5rem; }

/* Focus visible accesible */
:focus-visible { outline:2px solid var(--radial-primary); outline-offset:2px; }

/* Estados ARIA utilitarios */
[role="status"], [aria-live] { font-family: var(--font-base); }
.visually-hidden { position:absolute !important; width:1px !important; height:1px !important; padding:0 !important; margin:-1px !important; overflow:hidden !important; clip:rect(0 0 0 0) !important; white-space:nowrap !important; border:0 !important; }

/* Validación de errores - hover rojo para inputs con errores */
.validation-error:hover {
  border-color: #ef4444 !important;
  box-shadow: 0 0 0 .2rem rgba(239, 68, 68, .25) !important;
}

/* Estilos del modal */
.modal-body {
  font-size: var(--fs-sm) !important; /* Reducir tamaño de fuente */
  line-height: 1.4 !important;
}

.modal-title {
  font-size: var(--fs-md) !important; /* Reducir tamaño del título */
}

.card-header.axial-primary.text-center.py-3 {margin-bottom: 0; font-weight: 600; max-height: 3rem;}
.card-header.radial-primary.text-center.py-3 {margin-bottom: 0; font-weight: 600; max-height: 3rem;}
  </style>
</head>
<body class="app-bg py-4">
  <header class="mb-4">
    <div class="container">
      <h1 class="display-6 text-center fw-bold">Control de cambios de material IMD</h1>
    </div>
  </header>
  <!-- Cambiado a container-fluid para ancho completo -->
  <main class="container-fluid pb-4 px-4">
    <!-- La fila ahora ocupa 100% del viewport -->
    <div class="row g-4 px-4">
      <!-- Máquina AXIAL -->
      <div class="col-12 col-lg-6 px-4">
        <div class="card card-dark h-100 machine-axial">
          <div class="card-header axial-primary text-center py-3">
            <h2 class="h5 fw-semibold">Máquina AXIAL</h2>
          </div>
          <div class="card-body d-flex flex-column">
            <h6 class="" style="height: 30px; margin-top: 20px;">Escanea los datos correspondientes en cada campo</h6>
            <div class="row g-4 flex-grow-1">
              <div class="col-12 col-md-8 spacing-y">
                <!-- Pares de etiqueta / input -->
                <div class="scan-pair">
                  <div class="scan-label">QR almacén</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Escanear..." id="axial-qr-almacen"></div>
                </div>
                <div class="scan-pair">
                  <div class="scan-label">QR de proveedor</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Escanear..." id="axial-qr-proveedor"></div>
                </div>
                <div class="scan-pair">
                  <div class="scan-label">Lote de proveedor</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Escanear..." id="axial-lote-proveedor"></div>
                </div>
                <div class="scan-pair">
                  <div class="scan-label">Feeder</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Escanear..." id="axial-feeder"></div>
                </div>
                <div class="scan-pair">
                  <div class="scan-label">Polaridad</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Escanear..." id="axial-polaridad"></div>
                </div>
                <div class="scan-pair">
                  <div class="scan-label">Persona</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Escanear..." id="axial-persona"></div>
                </div>
                <div class="scan-pair">
                  <div class="scan-label">Spec</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Cargando..." id="axial-spec" readonly></div>
                </div>
              </div>
              <div class="col-12 col-md-4 d-flex flex-column gap-3">
                <div>
                  <div class="display-block-title">Polaridad</div>
                  <div class="display-block mt-0" id="axial-polaridad-display">
                  </div>
                </div>
                <div>
                  <div class="display-block-title">Resultado</div>
                  <div class="display-block mt-0" id="axial-resultado-display">
                  </div>
                </div>
              </div>
            </div>
            <!-- Centrado del botón -->
            <div class="mt-4 d-flex justify-content-center">
              <button class="btn btn-change w-75" id="axial-cambiar">CAMBIAR</button>
            </div>
          </div>
        </div>
      </div>
      <!-- Máquina RADIAL -->
      <div class="col-12 col-lg-6 px-4">
        <div class="card card-dark h-100 machine-radial">
          <div class="card-header radial-primary text-center py-3">
            <h2 class="h5 mb-0 fw-semibold">Máquina RADIAL</h2>
          </div>
          <div class="card-body d-flex flex-column">
            <h6 class="" style="height: 30px; margin-top: 20px;">Escanea los datos correspondientes en cada campo</h6>
            <div class="row g-4 flex-grow-1">
              <div class="col-12 col-md-8 spacing-y">
                <!-- Pares de etiqueta / input -->
                <div class="scan-pair">
                  <div class="scan-label">QR almacén</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Escanear..." id="radial-qr-almacen"></div>
                </div>
                <div class="scan-pair">
                  <div class="scan-label">QR de proveedor</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Escanear..." id="radial-qr-proveedor"></div>
                </div>
                <div class="scan-pair">
                  <div class="scan-label">Lote de proveedor</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Escanear..." id="radial-lote-proveedor"></div>
                </div>
                <div class="scan-pair">
                  <div class="scan-label">Feeder</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Escanear..." id="radial-feeder"></div>
                </div>
                <div class="scan-pair">
                  <div class="scan-label">Polaridad</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Escanear..." id="radial-polaridad"></div>
                </div>
                <div class="scan-pair">
                  <div class="scan-label">Persona</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Escanear..." id="radial-persona"></div>
                </div>
                <div class="scan-pair">
                  <div class="scan-label">Spec</div>
                  <div class="scan-input"><input type="text" class="form-control" placeholder="Cargando..." id="radial-spec" readonly></div>
                </div>
              </div>
              <div class="col-12 col-md-4 d-flex flex-column gap-3">
                <div>
                  <div class="display-block-title" >Polaridad</div>
                  <div class="display-block mt-0" id="radial-polaridad-display">
                  </div>
                </div>
                <div>
                  <div class="display-block-title">Resultado</div>
                  <div class="display-block mt-0" id="radial-resultado-display">
                  </div>
                </div>
              </div>
            </div>
            <!-- Centrado del botón -->
            <div class="mt-4 d-flex justify-content-center">
              <button class="btn btn-change w-75" id="radial-cambiar">CAMBIAR</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- Modal para errores y mensajes -->
  <div class="modal fade" id="messageModal" tabindex="-1" aria-labelledby="messageModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content bg-dark border-secondary">
        <div class="modal-header border-secondary">
          <h5 class="modal-title text-white" id="messageModalLabel">Mensaje</h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body text-white" id="messageModalBody">
          <!-- El contenido se llenará dinámicamente -->
        </div>
        <div class="modal-footer border-secondary">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Bootstrap JS -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  
  <!-- JavaScript Embebido con URL dinámica -->
  <script>
// app.js - Lógica para el control de cambios de material IMD con URL dinámica
const API_BASE_URL = window.location.origin + '/api';

// Variables globales para cada máquina
const machineStates = {
    axial: {
        machine: 'AXIAL',
        qrAlmacen: '',
        qrProveedor: '',
        loteProveedor: '',
        feeder: '',
        polaridad: '',
        persona: '',
        partNumber: '',
        spec: '',
        dbPolarity: '',
        feederValid: false,
        polarityValid: false,
        allDataReady: false
    },
    radial: {
        machine: 'RADIAL',
        qrAlmacen: '',
        qrProveedor: '',
        loteProveedor: '',
        feeder: '',
        polaridad: '',
        persona: '',
        partNumber: '',
        spec: '',
        dbPolarity: '',
        feederValid: false,
        polarityValid: false,
        allDataReady: false
    }
};

// Función para mostrar modal con mensaje
function showModal(title, message, isError = false, autoClose = false) {
    const modal = new bootstrap.Modal(document.getElementById('messageModal'));
    const titleElement = document.getElementById('messageModalLabel');
    const bodyElement = document.getElementById('messageModalBody');
    const closeButton = document.querySelector('#messageModal .btn-close');
    const footerButton = document.querySelector('#messageModal .modal-footer .btn');
    
    titleElement.textContent = title;
    bodyElement.innerHTML = message;
    
    // Cambiar color según el tipo de mensaje
    const modalContent = document.querySelector('#messageModal .modal-content');
    if (isError) {
        modalContent.style.borderColor = '#dc3545';
        titleElement.style.color = '#ff6b6b';
    } else {
        modalContent.style.borderColor = '#28a745';
        titleElement.style.color = '#51cf66';
    }
    
    // Controlar visibilidad de botones según autoClose
    if (autoClose) {
        closeButton.style.display = 'none';
        footerButton.style.display = 'none';
    } else {
        closeButton.style.display = 'block';
        footerButton.style.display = 'block';
    }
    
    modal.show();
    
    // Auto cerrar después de 2 segundos si autoClose es true
    if (autoClose) {
        setTimeout(() => {
            modal.hide();
        }, 2000);
    }
}

// Función para extraer número de parte del QR almacén
function extractPartNumber(qrAlmacen) {
    if (!qrAlmacen) return null;
    
    // Buscar el primer separador y tomar todo lo anterior
    const separators = [',', "'", '_', '-'];
    for (const sep of separators) {
        const index = qrAlmacen.indexOf(sep);
        if (index !== -1) {
            return qrAlmacen.substring(0, index);
        }
    }
    
    // Si no hay separadores, retornar el string completo
    return qrAlmacen;
}

// Función para hacer peticiones a la API
async function apiRequest(endpoint, data = null) {
    try {
        const options = {
            method: data ? 'POST' : 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error en API request:', error);
        throw error;
    }
}

// Función para buscar información de parte
async function searchPart(machineType, qrAlmacen) {
    const state = machineStates[machineType];
    
    try {
        // Extraer número de parte
        const partNumber = extractPartNumber(qrAlmacen);
        if (!partNumber) {
            showModal('Error', 'No se pudo extraer el número de parte del QR almacén', true);
            return;
        }
        
        // Buscar en base de datos
        const result = await apiRequest('/search-part', {
            qr_almacen: qrAlmacen,
            machine: state.machine
        });
        
        if (result.success) {
            // Actualizar estado
            state.partNumber = result.part_number;
            state.spec = result.data.spec;
            state.dbPolarity = result.data.polarity;
            
            // Actualizar UI - Spec
            const specInput = document.getElementById(`${machineType}-spec`);
            specInput.value = result.data.spec;
            specInput.style.backgroundColor = '#1a472a'; // Verde oscuro
            
            // Actualizar UI - Polaridad en bloque de visualización
            const polarityDisplayDiv = document.getElementById(`${machineType}-polaridad-display`);
            if (polarityDisplayDiv) {
                polarityDisplayDiv.innerHTML = `<h1 style="color: white; margin: 0; text-align: center; line-height: 1.2; padding: 20px 0;">${result.data.polarity || 'N/A'}</h1>`;
            }
            
            console.log(`✅ Datos encontrados para ${state.machine}:`, result.data);
        } else {
            showModal('Error', `No se encontraron datos para el número de parte: ${partNumber}`, true);
        }
        
    } catch (error) {
        showModal('Error', 'Error conectando con el servidor. Verifique que el servidor esté ejecutándose.', true);
        console.error('Error buscando parte:', error);
    }
}

// Función para validar feeder
async function validateFeeder(machineType, feederScanned) {
    const state = machineStates[machineType];
    
    if (!state.partNumber) {
        showModal('Error', 'Primero debe escanear el QR almacén', true);
        return;
    }
    
    try {
        const result = await apiRequest('/validate-feeder', {
            part_number: state.partNumber,
            feeder_scanned: feederScanned,
            machine: state.machine
        });
        
        if (result.success) {
            state.feederValid = result.is_valid;
            
            // Actualizar color del input según validación
            const feederInput = document.getElementById(`${machineType}-feeder`);
            if (feederInput) {
                if (result.is_valid) {
                    feederInput.style.backgroundColor = '#1a472a'; // Verde oscuro
                    feederInput.classList.remove('validation-error');
                } else {
                    feederInput.style.backgroundColor = '#7f1d1d'; // Rojo oscuro
                    feederInput.classList.add('validation-error');
                }
            }
            
            // Actualizar bloque de resultado
            updateResultDisplay(machineType);
            
            console.log(`Validación feeder ${state.machine}:`, result.is_valid ? 'OK' : 'NG');
        } else {
            showModal('Error', 'Error validando feeder', true);
        }
        
    } catch (error) {
        showModal('Error', 'Error conectando con el servidor para validar feeder', true);
        console.error('Error validando feeder:', error);
    }
}

// Función para validar polaridad
async function validatePolarity(machineType, polarityScanned) {
    const state = machineStates[machineType];
    
    if (!state.partNumber) {
        showModal('Error', 'Primero debe escanear el QR almacén', true);
        return;
    }
    
    try {
        const result = await apiRequest('/validate-polarity', {
            part_number: state.partNumber,
            polarity_scanned: polarityScanned,
            machine: state.machine
        });
        
        if (result.success) {
            state.polarityValid = result.is_valid;
            
            // Actualizar color de la polaridad en el display del lado derecho
            updatePolarityDisplayColor(machineType, result.is_valid);
            
            // Actualizar color del input según validación
            const polarityInput = document.getElementById(`${machineType}-polaridad`);
            if (polarityInput) {
                if (result.is_valid) {
                    polarityInput.style.backgroundColor = '#1a472a'; // Verde oscuro
                    polarityInput.classList.remove('validation-error');
                } else {
                    polarityInput.style.backgroundColor = '#7f1d1d'; // Rojo oscuro
                    polarityInput.classList.add('validation-error');
                }
            }
            
            // Actualizar color del resultado según validación de polaridad
            updateResultDisplay(machineType, true);
            
            console.log(`Validación polaridad ${state.machine}:`, result.is_valid ? 'OK' : 'NG');
        } else {
            showModal('Error', 'Error validando polaridad', true);
        }
        
    } catch (error) {
        showModal('Error', 'Error conectando con el servidor para validar polaridad', true);
        console.error('Error validando polaridad:', error);
    }
}

// Función para actualizar el color del display de polaridad
function updatePolarityDisplayColor(machineType, isValid) {
    const polarityDisplayDiv = document.getElementById(`${machineType}-polaridad-display`);
    if (polarityDisplayDiv) {
        const currentText = polarityDisplayDiv.querySelector('h1')?.textContent || '';
        if (currentText && currentText !== 'N/A') {
            const color = isValid ? '#22c55e' : '#ef4444'; // Verde si es válido, rojo si no
            polarityDisplayDiv.innerHTML = `<h1 style="color: ${color}; margin: 0; text-align: center; line-height: 1.2; padding: 20px 0;">${currentText}</h1>`;
            console.log(`🎨 Color de polaridad actualizado para ${machineType}: ${isValid ? 'VERDE (válida)' : 'ROJO (inválida)'}`);
        }
    }
}

// Función para actualizar el display de resultado
function updateResultDisplay(machineType, includePolarityValidation = false) {
    const state = machineStates[machineType];
    const resultElement = document.getElementById(`${machineType}-resultado-display`);
    
    if (!resultElement) return;
    
    let resultText = '';
    let resultColor = '';
    
    // Determinar resultado basado en validación de feeder
    if (state.feederValid) {
        resultText = 'OK';
        resultColor = '#22c55e'; // Verde
    } else {
        resultText = 'NG';
        resultColor = '#ef4444'; // Rojo
    }
    
    // Si se incluye validación de polaridad, ajustar color
    if (includePolarityValidation) {
        if (!state.polarityValid) {
            resultText = 'NG';
            resultColor = '#ef4444'; // Rojo si la polaridad no es válida
        }
    }
    
    resultElement.innerHTML = `<h1 style="color: ${resultColor}; margin: 0; text-align: center; line-height: 1.2; padding: 20px 0;">${resultText}</h1>`;
}

// Función para verificar si todos los datos están listos
function checkAllDataReady(machineType) {
    const state = machineStates[machineType];
    
    state.allDataReady = (
        state.qrAlmacen &&
        state.qrProveedor &&
        state.loteProveedor &&
        state.feeder &&
        state.polaridad &&
        state.persona &&
        state.partNumber
    );
    
    return state.allDataReady;
}

// Función para guardar en historial
async function saveToHistory(machineType) {
    const state = machineStates[machineType];
    
    // Verificar si hay errores
    if (!state.feederValid || !state.polarityValid) {
        let errorMessage = 'Se encontraron los siguientes errores:<br><br>';
        
        if (!state.feederValid) {
            errorMessage += '• El feeder escaneado no coincide con el esperado<br>';
        }
        
        if (!state.polarityValid) {
            errorMessage += '• La polaridad escaneada no coincide con la esperada<br>';
        }
        
        showModal('Errores de Validación', errorMessage, true);
        return;
    }
    
    // Verificar que todos los campos estén completos
    if (!checkAllDataReady(machineType)) {
        showModal('Error', 'Todos los campos deben estar completos antes de guardar', true);
        return;
    }
    
    try {
        const historyData = {
            posicion_de_feeder: `${state.machine}_${state.feeder}`,
            qr_almacen: state.qrAlmacen,
            numero_de_parte: state.partNumber,
            spec: state.spec,
            qr_de_proveedor: state.qrProveedor,
            numero_de_lote_proveedor: state.loteProveedor,
            polaridad: state.polaridad,
            persona: state.persona
        };
        
        const result = await apiRequest('/save-history', historyData);
        
        if (result.success) {
            showModal('Éxito', '✅ Cambio de material registrado exitosamente', false, true);
            
            // Limpiar formulario
            clearMachineForm(machineType);
        } else {
            showModal('Error', 'Error guardando el registro', true);
        }
        
    } catch (error) {
        showModal('Error', 'Error conectando con el servidor para guardar', true);
        console.error('Error guardando historial:', error);
    }
}

// Función para limpiar formulario
function clearMachineForm(machineType) {
    const state = machineStates[machineType];
    
    console.log(`🧹 Limpiando formulario para máquina ${machineType.toUpperCase()}`);
    
    // Resetear estado
    Object.assign(state, {
        qrAlmacen: '',
        qrProveedor: '',
        loteProveedor: '',
        feeder: '',
        polaridad: '',
        persona: '',
        partNumber: '',
        spec: '',
        dbPolarity: '',
        feederValid: false,
        polarityValid: false,
        allDataReady: false
    });
    
    // Limpiar inputs
    const inputs = [
        'qr-almacen', 'qr-proveedor', 'lote-proveedor', 
        'feeder', 'polaridad', 'persona', 'spec'
    ];
    
    inputs.forEach(inputName => {
        const input = document.getElementById(`${machineType}-${inputName}`);
        if (input) {
            input.value = '';
            input.style.backgroundColor = ''; // Resetear color
            input.classList.remove('validation-error'); // Remover clase de error
            console.log(`✅ Limpiado input: ${machineType}-${inputName}`);
        }
    });
    
    // Limpiar displays de visualización
    const polarityDisplay = document.getElementById(`${machineType}-polaridad-display`);
    if (polarityDisplay) {
        polarityDisplay.innerHTML = '';
        console.log(`✅ Limpiado display de polaridad: ${machineType}-polaridad-display`);
    } else {
        console.warn(`⚠️ No se encontró elemento: ${machineType}-polaridad-display`);
    }
    
    const resultDisplay = document.getElementById(`${machineType}-resultado-display`);
    if (resultDisplay) {
        resultDisplay.innerHTML = '';
        console.log(`✅ Limpiado display de resultado: ${machineType}-resultado-display`);
    } else {
        console.warn(`⚠️ No se encontró elemento: ${machineType}-resultado-display`);
    }
    
    console.log(`✨ Formulario ${machineType.toUpperCase()} completamente limpiado`);
}

// Event listeners para inputs
function setupEventListeners() {
    ['axial', 'radial'].forEach(machineType => {
        const state = machineStates[machineType];
        
        // QR Almacén - Trigger búsqueda cuando se termine de escribir
        const qrAlmacenInput = document.getElementById(`${machineType}-qr-almacen`);
        qrAlmacenInput.addEventListener('input', function(e) {
            state.qrAlmacen = e.target.value;
        });
        qrAlmacenInput.addEventListener('blur', function(e) {
            if (e.target.value.length > 5) { // Búsqueda cuando hay suficientes caracteres
                searchPart(machineType, e.target.value);
            }
        });
        
        // QR Proveedor
        document.getElementById(`${machineType}-qr-proveedor`).addEventListener('input', function(e) {
            state.qrProveedor = e.target.value;
        });
        
        // Lote Proveedor
        document.getElementById(`${machineType}-lote-proveedor`).addEventListener('input', function(e) {
            state.loteProveedor = e.target.value;
        });
        
        // Feeder - Trigger validación cuando se termine de escribir
        const feederInput = document.getElementById(`${machineType}-feeder`);
        feederInput.addEventListener('input', function(e) {
            state.feeder = e.target.value;
        });
        feederInput.addEventListener('blur', function(e) {
            if (e.target.value && state.partNumber) {
                validateFeeder(machineType, e.target.value);
            }
        });
        
        // Polaridad - Trigger validación cuando se termine de escribir
        const polaridadInput = document.getElementById(`${machineType}-polaridad`);
        polaridadInput.addEventListener('input', function(e) {
            state.polaridad = e.target.value;
        });
        polaridadInput.addEventListener('blur', function(e) {
            if (e.target.value && state.partNumber) {
                validatePolarity(machineType, e.target.value);
            }
        });
        
        // Persona
        document.getElementById(`${machineType}-persona`).addEventListener('input', function(e) {
            state.persona = e.target.value;
        });
        
        // Botón CAMBIAR
        document.getElementById(`${machineType}-cambiar`).addEventListener('click', function() {
            saveToHistory(machineType);
        });
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Aplicación IMD Control iniciada');
    setupEventListeners();
    
    // Verificar conexión con el servidor usando la URL dinámica
    fetch(`${API_BASE_URL}/health`)
        .then(response => response.json())
        .then(data => {
            console.log('✅ Servidor conectado:', data);
        })
        .catch(error => {
            console.error('❌ Error conectando con servidor:', error);
            showModal('Error de Conexión', 
                'No se pudo conectar con el servidor. Verifique que esté ejecutándose.', 
                true);
        });
});
  </script>
</body>
</html>"""
        return html_content
    except Exception as e:
        return f"Error cargando la aplicación: {e}", 500

# API Health check
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'OK',
        'message': 'Servidor IMD funcionando correctamente',
        'timestamp': datetime.now().isoformat()
    })

# API para buscar información de parte
@app.route('/api/search-part', methods=['POST'])
def search_part():
    try:
        data = request.get_json()
        qr_almacen = data.get('qr_almacen', '').strip()
        machine = data.get('machine', '').strip()
        
        if not qr_almacen:
            return jsonify({'success': False, 'error': 'QR almacén requerido'})
        
        # Extraer número de parte del QR almacén
        separators = [',', "'", '_', '-']
        part_number = qr_almacen
        for sep in separators:
            if sep in qr_almacen:
                part_number = qr_almacen.split(sep)[0]
                break
        
        # Buscar en base de datos
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': 'Error de conexión a base de datos'})
        
        cursor = connection.cursor(buffered=True)
        query = """
        SELECT numero_de_parte, spec, posicion_de_feeder, polarity 
        FROM imd_feeders_location_data 
        WHERE numero_de_parte = %s AND posicion_de_feeder LIKE %s
        LIMIT 1
        """
        cursor.execute(query, (part_number, f"{machine}_%"))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result:
            return jsonify({
                'success': True,
                'part_number': part_number,
                'data': {
                    'numero_de_parte': result[0],
                    'spec': result[1],
                    'posicion_de_feeder': result[2],
                    'polarity': result[3]
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Número de parte no encontrado'})
            
    except Exception as e:
        print(f"❌ Error en search-part: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API para validar feeder
@app.route('/api/validate-feeder', methods=['POST'])
def validate_feeder():
    try:
        data = request.get_json()
        part_number = data.get('part_number', '').strip()
        feeder_scanned = data.get('feeder_scanned', '').strip()
        machine = data.get('machine', '').strip()
        
        if not all([part_number, feeder_scanned, machine]):
            return jsonify({'success': False, 'error': 'Datos incompletos'})
        
        # Buscar feeder esperado
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': 'Error de conexión a base de datos'})
        
        cursor = connection.cursor(buffered=True)
        query = """
        SELECT posicion_de_feeder 
        FROM imd_feeders_location_data 
        WHERE numero_de_parte = %s AND posicion_de_feeder LIKE %s
        """
        cursor.execute(query, (part_number, f"{machine}_%"))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result:
            expected_feeder = result[0].split('_')[1]  # Extraer solo la parte del feeder
            is_valid = expected_feeder.upper() == feeder_scanned.upper()
            return jsonify({
                'success': True,
                'is_valid': is_valid,
                'expected_feeder': expected_feeder,
                'scanned_feeder': feeder_scanned
            })
        else:
            return jsonify({'success': False, 'error': 'Configuración de feeder no encontrada'})
            
    except Exception as e:
        print(f"❌ Error en validate-feeder: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API para validar polaridad
@app.route('/api/validate-polarity', methods=['POST'])
def validate_polarity():
    try:
        data = request.get_json()
        part_number = data.get('part_number', '').strip()
        polarity_scanned = data.get('polarity_scanned', '').strip()
        machine = data.get('machine', '').strip()
        
        if not all([part_number, polarity_scanned, machine]):
            return jsonify({'success': False, 'error': 'Datos incompletos'})
        
        # Buscar polaridad esperada
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': 'Error de conexión a base de datos'})
        
        cursor = connection.cursor(buffered=True)
        query = """
        SELECT polarity 
        FROM imd_feeders_location_data 
        WHERE numero_de_parte = %s AND posicion_de_feeder LIKE %s
        """
        cursor.execute(query, (part_number, f"{machine}_%"))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result:
            expected_polarity = result[0]
            is_valid = expected_polarity.upper() == polarity_scanned.upper()
            return jsonify({
                'success': True,
                'is_valid': is_valid,
                'expected_polarity': expected_polarity,
                'scanned_polarity': polarity_scanned
            })
        else:
            return jsonify({'success': False, 'error': 'Configuración de polaridad no encontrada'})
            
    except Exception as e:
        print(f"❌ Error en validate-polarity: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API para guardar en historial
@app.route('/api/save-history', methods=['POST'])
def save_history():
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = [
            'posicion_de_feeder', 'qr_almacen', 'numero_de_parte',
            'qr_de_proveedor', 'numero_de_lote_proveedor', 'polaridad', 'persona'
        ]
        
        for field in required_fields:
            if not data.get(field, '').strip():
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'})
        
        # Guardar en base de datos
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': 'Error de conexión a base de datos'})
        
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO material_change_history 
        (posicion_de_feeder, qr_almacen, numero_de_parte, spec, qr_de_proveedor, 
         numero_de_lote_proveedor, polaridad, persona, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            data['posicion_de_feeder'],
            data['qr_almacen'],
            data['numero_de_parte'],
            data.get('spec', ''),
            data['qr_de_proveedor'],
            data['numero_de_lote_proveedor'],
            data['polaridad'],
            data['persona'],
            datetime.now()
        )
        
        cursor.execute(insert_query, values)
        connection.commit()
        
        record_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'record_id': record_id,
            'message': 'Registro guardado exitosamente'
        })
        
    except Exception as e:
        print(f"❌ Error en save-history: {e}")
        return jsonify({'success': False, 'error': str(e)})

def find_free_port():
    """Encuentra un puerto libre para Flask"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def start_flask_server(port):
    """Inicia el servidor Flask en un thread separado"""
    try:
        logger.info(f"Iniciando servidor Flask en puerto {port}...")
        
        # Crear tabla de historial
        create_history_table()
        
        # Configurar Flask para modo de producción
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        app.config['ENV'] = 'production'
        
        # Deshabilitar logging de Flask en modo producción
        import logging as flask_logging
        flask_logging.getLogger('werkzeug').setLevel(flask_logging.ERROR)
        
        # Ejecutar servidor Flask
        logger.info(f"Servidor Flask iniciado en http://{ProductionConfig.FLASK_HOST}:{port}")
        app.run(
            host=ProductionConfig.FLASK_HOST, 
            port=port, 
            debug=False, 
            use_reloader=False, 
            threaded=True,
            processes=1
        )
    except Exception as e:
        logger.error(f"Error iniciando servidor Flask: {e}")
        raise

def wait_for_flask_server(url, max_attempts=15, delay=1):
    """Espera a que el servidor Flask esté disponible"""
    import requests
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{url}/api/health", timeout=2)
            if response.status_code == 200:
                logger.info(f"Servidor Flask disponible en intento {attempt + 1}")
                return True
        except:
            pass
        
        logger.info(f"Esperando servidor Flask... intento {attempt + 1}/{max_attempts}")
        time.sleep(delay)
    
    return False

def main():
    """Función principal de la aplicación"""
    try:
        logger.info(f"Iniciando {ProductionConfig.APP_NAME} v{ProductionConfig.APP_VERSION}...")
        logger.info(f"PC: {socket.gethostname()}")
        logger.info(f"Máquina por defecto: {db_config.get('machine_default', 'AXIAL')}")
        
        # Encontrar puerto libre
        port = find_free_port()
        flask_url = f"http://{ProductionConfig.FLASK_HOST}:{port}"
        
        # Iniciar Flask en thread separado con manejo de errores mejorado
        flask_thread = threading.Thread(
            target=start_flask_server, 
            args=(port,), 
            daemon=True,
            name="FlaskServerThread"
        )
        flask_thread.start()
        
        # Esperar a que Flask se inicie con verificación de salud
        logger.info("Esperando que el servidor Flask se inicie...")
        if not wait_for_flask_server(flask_url):
            logger.error("El servidor Flask no pudo iniciarse correctamente")
            return
        
        # Configurar ventana de webview
        logger.info("Iniciando interfaz de escritorio...")
        
        # Verificar si existe el icono personalizado
        icon_path = os.path.join(os.path.dirname(__file__), 'icono_app.png')
        if os.path.exists(icon_path):
            logger.info(f"Usando icono personalizado: {icon_path}")
        else:
            icon_path = None
            logger.warning("Icono personalizado no encontrado, usando icono por defecto")
        
        # Configuración de ventana
        window_config = ProductionConfig.WINDOW_CONFIG.copy()
        
        # Crear ventana de la aplicación maximizada y no redimensionable
        webview.create_window(
            title=f'{ProductionConfig.APP_NAME} v{ProductionConfig.APP_VERSION}',
            url=flask_url,
            width=window_config.get('width', 1920),
            height=window_config.get('height', 1080),
            min_size=window_config.get('min_size', (1200, 800)),
            resizable=window_config.get('resizable', False),
            maximized=window_config.get('maximized', True)
        )
        
        # Ejecutar aplicación
        logger.info("Aplicación iniciada exitosamente")
        webview.start(debug=False)
        
    except Exception as e:
        logger.error(f"Error iniciando la aplicación: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        logger.info("Aplicación finalizando...")

if __name__ == '__main__':
    main()