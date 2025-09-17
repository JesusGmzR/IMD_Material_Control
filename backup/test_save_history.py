#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para el endpoint save-history
"""

import requests
import json

# URL del servidor local
BASE_URL = "http://127.0.0.1:5000"

def test_save_history():
    """Prueba el endpoint save-history con datos de ejemplo"""
    
    # Datos de prueba con el esquema actualizado
    test_data = {
        "posicion_de_feeder": "RADIAL_1",
        "qr_almacen": "TEST123,456,789",
        "numero_de_parte": "TEST123",
        "spec": "Test Specification",
        "qr_de_proveedor": "PROV_QR_TEST",
        "numero_de_lote_proveedor": "LOTE_TEST_001",
        "polaridad": "POS",
        "persona": "TEST_USER",
        "line": "PANA_A"
    }
    
    try:
        print("🧪 Probando endpoint /api/save-history...")
        print("📋 Esquema esperado: fecha, hora, posicion_de_feeder, qr_almacen,")
        print("   numero_de_parte, spec, qr_de_proveedor, numero_de_lote_proveedor,")
        print("   polaridad, persona, created_at")
        print(f"📊 Datos de prueba: {json.dumps(test_data, indent=2)}")
        
        # Hacer petición POST
        response = requests.post(
            f"{BASE_URL}/api/save-history",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📨 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Prueba EXITOSA - Datos guardados correctamente")
                print(f"🆔 Record ID: {result.get('record_id')}")
                print("📅 Se almacenaron: fecha, hora y created_at automáticamente")
            else:
                print("❌ Prueba FALLIDA - Error en respuesta")
                print(f"🚫 Error: {result.get('error')}")
        else:
            print(f"❌ Prueba FALLIDA - HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_save_history()