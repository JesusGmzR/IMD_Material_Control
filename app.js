// app.js - Lógica para el control de cambios de material IMD
const API_BASE_URL = 'http://127.0.0.1:5000/api';

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
    
    // Verificar conexión con el servidor
    fetch(`${API_BASE_URL}/health`)
        .then(response => response.json())
        .then(data => {
            console.log('✅ Servidor conectado:', data);
        })
        .catch(error => {
            console.error('❌ Error conectando con servidor:', error);
            showModal('Error de Conexión', 
                'No se pudo conectar con el servidor. Verifique que esté ejecutándose en http://127.0.0.1:5000', 
                true);
        });
});