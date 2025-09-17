"""Pruebas automatizadas para el endpoint `/api/save-history`."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

import pytest

try:  # pragma: no cover - dependencia opcional para entornos sin cliente HTTP
    import requests
except ImportError:  # pragma: no cover
    requests = None


BASE_URL = os.getenv("IMD_API_BASE_URL", "http://127.0.0.1:5000").rstrip("/")


def _build_payload() -> Dict[str, Any]:
    """Genera un payload válido para el historial de cambios de material."""

    return {
        "posicion_de_feeder": "RADIAL_1",
        "qr_almacen": "TEST123456",
        "numero_de_parte": "TEST-001",
        "spec": "Test Specification",
        "qr_de_proveedor": "PROV-QR-01",
        "numero_de_lote_proveedor": "LOTE-XYZ",
        "polaridad": "+",
        "persona": "TEST_USER",
        "line": "PANA_A",
    }


@pytest.mark.integration
def test_save_history_endpoint_accepts_valid_payload():
    """Verifica que el endpoint acepte datos válidos cuando el servicio está disponible."""

    if requests is None:
        pytest.skip("La librería requests no está disponible en el entorno de pruebas.")

    try:
        response = requests.post(
            f"{BASE_URL}/api/save-history",
            json=_build_payload(),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
    except requests.exceptions.ConnectTimeout:
        pytest.skip("El servicio /api/save-history excedió el tiempo de espera durante la prueba.")
    except requests.exceptions.ConnectionError:
        pytest.skip("El servicio /api/save-history no está disponible en el entorno de pruebas.")

    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload.get("success") is True, json.dumps(payload, ensure_ascii=False)
    assert "record_id" in payload, payload
    assert isinstance(payload["record_id"], int)
    assert payload.get("message")
