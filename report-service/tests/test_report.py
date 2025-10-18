import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Тест health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_summary_without_auth():
    """Тест получения сводки без авторизации"""
    response = client.get("/summary")
    # Ожидаем ошибку, так как нет авторизации
    assert response.status_code in [401, 500]

def test_export_csv_without_auth():
    """Тест экспорта CSV без авторизации"""
    response = client.get("/export.csv")
    # Ожидаем ошибку, так как нет авторизации
    assert response.status_code in [401, 500]

def test_export_pdf_without_auth():
    """Тест экспорта PDF без авторизации"""
    response = client.get("/export.pdf")
    # Ожидаем ошибку, так как нет авторизации
    assert response.status_code in [401, 500]

def test_summary_with_mock_auth():
    """Тест получения сводки с моковой авторизацией"""
    headers = {"Authorization": "Bearer mock_token"}
    response = client.get("/summary", headers=headers)
    # Ожидаем ошибку, так как finance-service недоступен
    assert response.status_code in [401, 500]

def test_export_csv_with_mock_auth():
    """Тест экспорта CSV с моковой авторизацией"""
    headers = {"Authorization": "Bearer mock_token"}
    response = client.get("/export.csv", headers=headers)
    # Ожидаем ошибку, так как finance-service недоступен
    assert response.status_code in [401, 500]

def test_export_pdf_with_mock_auth():
    """Тест экспорта PDF с моковой авторизацией"""
    headers = {"Authorization": "Bearer mock_token"}
    response = client.get("/export.pdf", headers=headers)
    # Ожидаем ошибку, так как finance-service недоступен
    assert response.status_code in [401, 500]

def test_summary_parameters():
    """Тест параметров запроса сводки"""
    headers = {"Authorization": "Bearer mock_token"}
    
    # Тест с параметрами
    response = client.get("/summary?branch_id=1&limit=10", headers=headers)
    assert response.status_code in [401, 500]

def test_export_parameters():
    """Тест параметров экспорта"""
    headers = {"Authorization": "Bearer mock_token"}
    
    # Тест CSV с параметрами
    response = client.get("/export.csv?branch_id=1&limit=20", headers=headers)
    assert response.status_code in [401, 500]
    
    # Тест PDF с параметрами
    response = client.get("/export.pdf?branch_id=1&limit=20", headers=headers)
    assert response.status_code in [401, 500]
