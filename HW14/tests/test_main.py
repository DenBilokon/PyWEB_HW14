from fastapi.testclient import TestClient

from src.database.db import get_db
from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_healthchecker():
    response = client.get("/api/healthchecker")
    assert response.status_code == 200
    assert response.json() == {'message': 'Welcome to FastAPI'}


def test_healthchecker_database_error():
    # Мокування з'єднання з базою даних, щоб спричинити помилку
    app.dependency_overrides[get_db] = lambda: None

    response = client.get("/api/healthchecker")
    assert response.status_code == 500
    assert response.json() == {'detail': 'Error connecting to the database'}

    # Відновлення оригінальної залежності після тесту
    app.dependency_overrides.pop(get_db)


