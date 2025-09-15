from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import re
from datetime import datetime
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permite peticiones desde el frontend

# Configuración de base de datos
DB_CONFIG = {
    'host': 'up-de-fra1-mysql-1.db.run-on-seenode.com',
    'port': 11550,
    'database': 'db_rrpq0erbdujn',
    'user': 'db_rrpq0erbdujn',
    'password': '5fUNbSRcPP3LN9K2I33Pr0ge',
    'charset': 'utf8mb4',
    'use_unicode': True
}

def get_db_connection():
    """Crear conexión a MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Error conectando a MySQL: {e}")
        return None

def extract_part_number(qr_almacen):
    """Extraer número de parte del QR almacén (antes de ',', "'", '_', '-')"""
    if not qr_almacen:
        return None
    
    # Buscar el primer separador y tomar todo lo anterior
    separators = [',', "'", '_', '-']
    for sep in separators:
        if sep in qr_almacen:
            return qr_almacen.split(sep)[0]
    
    # Si no hay separadores, retornar el string completo
    return qr_almacen

@app.route('/api/search-part', methods=['POST'])
def search_part():
    """Buscar información de parte por número de parte"""
    try:
        data = request.get_json()
        qr_almacen = data.get('qr_almacen')
        machine = data.get('machine', '').upper()  # AXIAL o RADIAL
        
        if not qr_almacen:
            return jsonify({'error': 'QR almacén requerido'}), 400
        
        # Extraer número de parte
        part_number = extract_part_number(qr_almacen)
        if not part_number:
            return jsonify({'error': 'No se pudo extraer número de parte'}), 400
        
        logger.info(f"🔍 Buscando: no_part='{part_number}', machine='{machine}'")
        
        # Buscar en base de datos
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Error de conexión a base de datos'}), 500
        
        cursor = connection.cursor(dictionary=True, buffered=True)
        
        # Buscar por no_part y machine
        query = """
        SELECT location_code, line, feeder, machine, no_part, spec, polarity
        FROM imd_feeders_location_data 
        WHERE no_part = %s AND machine = %s
        """
        
        cursor.execute(query, (part_number, machine))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result:
            return jsonify({
                'success': True,
                'part_number': part_number,
                'data': {
                    'location_code': result['location_code'],
                    'line': result['line'], 
                    'feeder': result['feeder'],
                    'machine': result['machine'],
                    'no_part': result['no_part'],
                    'spec': result['spec'],
                    'polarity': result['polarity']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Número de parte {part_number} no encontrado para máquina {machine}'
            })
            
    except Exception as e:
        logger.error(f"Error en search-part: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/validate-feeder', methods=['POST'])
def validate_feeder():
    """Validar feeder escaneado contra base de datos"""
    try:
        data = request.get_json()
        part_number = data.get('part_number')
        feeder_scanned = data.get('feeder_scanned')
        machine = data.get('machine', '').upper()
        
        if not all([part_number, feeder_scanned, machine]):
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Error de conexión a base de datos'}), 500
        
        cursor = connection.cursor(dictionary=True, buffered=True)
        
        query = """
        SELECT feeder FROM imd_feeders_location_data 
        WHERE no_part = %s AND machine = %s
        """
        
        cursor.execute(query, (part_number, machine))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result:
            is_valid = result['feeder'].upper() == feeder_scanned.upper()
            return jsonify({
                'success': True,
                'is_valid': is_valid,
                'expected_feeder': result['feeder'],
                'scanned_feeder': feeder_scanned
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Número de parte no encontrado'
            })
            
    except Exception as e:
        logger.error(f"Error en validate-feeder: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/validate-polarity', methods=['POST'])
def validate_polarity():
    """Validar polaridad escaneada contra base de datos"""
    try:
        data = request.get_json()
        part_number = data.get('part_number')
        polarity_scanned = data.get('polarity_scanned')
        machine = data.get('machine', '').upper()
        
        if not all([part_number, polarity_scanned, machine]):
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Error de conexión a base de datos'}), 500
        
        cursor = connection.cursor(dictionary=True, buffered=True)
        
        query = """
        SELECT polarity FROM imd_feeders_location_data 
        WHERE no_part = %s AND machine = %s
        """
        
        cursor.execute(query, (part_number, machine))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result:
            db_polarity = result['polarity']
            # Si la polaridad en BD es None/NULL, considerarla válida
            if db_polarity is None:
                is_valid = True
            else:
                is_valid = db_polarity.upper() == polarity_scanned.upper()
            
            return jsonify({
                'success': True,
                'is_valid': is_valid,
                'expected_polarity': db_polarity,
                'scanned_polarity': polarity_scanned
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Número de parte no encontrado'
            })
            
    except Exception as e:
        logger.error(f"Error en validate-polarity: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/create-history-table', methods=['POST'])
def create_history_table():
    """Crear tabla de historial si no existe"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Error de conexión a base de datos'}), 500
        
        cursor = connection.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS historial_cambios_material_imd (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha DATE,
            hora TIME,
            posicion_de_feeder VARCHAR(100),
            qr_almacen VARCHAR(255),
            numero_de_parte VARCHAR(100),
            spec VARCHAR(200),
            qr_de_proveedor VARCHAR(255),
            numero_de_lote_proveedor VARCHAR(100),
            polaridad VARCHAR(50),
            persona VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_query)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Tabla de historial creada/verificada'})
        
    except Exception as e:
        logger.error(f"Error creando tabla historial: {e}")
        return jsonify({'error': 'Error creando tabla de historial'}), 500

@app.route('/api/save-history', methods=['POST'])
def save_history():
    """Guardar registro en historial de cambios"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = [
            'posicion_de_feeder', 'qr_almacen', 'numero_de_parte', 'spec',
            'qr_de_proveedor', 'numero_de_lote_proveedor', 'polaridad', 'persona'
        ]
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Error de conexión a base de datos'}), 500
        
        cursor = connection.cursor()
        
        # Obtener fecha y hora actuales
        now = datetime.now()
        fecha = now.date()
        hora = now.time()
        
        insert_query = """
        INSERT INTO historial_cambios_material_imd 
        (fecha, hora, posicion_de_feeder, qr_almacen, numero_de_parte, spec, 
         qr_de_proveedor, numero_de_lote_proveedor, polaridad, persona)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            fecha, hora,
            data['posicion_de_feeder'],
            data['qr_almacen'],
            data['numero_de_parte'],
            data['spec'],
            data['qr_de_proveedor'],
            data['numero_de_lote_proveedor'],
            data['polaridad'],
            data['persona']
        )
        
        cursor.execute(insert_query, values)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True, 
            'message': 'Historial guardado exitosamente',
            'id': cursor.lastrowid
        })
        
    except Exception as e:
        logger.error(f"Error guardando historial: {e}")
        return jsonify({'error': 'Error guardando en historial'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar el estado del servidor"""
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()})

def init_database():
    """Inicializar base de datos y crear tablas necesarias"""
    try:
        connection = get_db_connection()
        if not connection:
            print("❌ Error de conexión a base de datos")
            return False
        
        cursor = connection.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS historial_cambios_material_imd (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha DATE,
            hora TIME,
            posicion_de_feeder VARCHAR(100),
            qr_almacen VARCHAR(255),
            numero_de_parte VARCHAR(100),
            spec VARCHAR(200),
            qr_de_proveedor VARCHAR(255),
            numero_de_lote_proveedor VARCHAR(100),
            polaridad VARCHAR(50),
            persona VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_query)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        print("✅ Tabla de historial creada/verificada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    print("📋 Verificando tabla de historial...")
    
    # Inicializar base de datos
    if init_database():
        print("🌐 Servidor disponible en: http://localhost:5000")
        app.run(debug=True, host='localhost', port=5000, threaded=True)
    else:
        print("❌ No se pudo inicializar la base de datos")