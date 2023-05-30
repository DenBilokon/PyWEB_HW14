from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from src.database.models import User
from src.services.auth import auth_service

CONTACT = {
    "id": 1,
    "first_name": "FirstName",
    "last_name": "LastName",
    "email": "test_user123@gmail.com",
    "phone_number": "0999999999",
    "birthday": "2023-06-15",
    "other_data": "test_data"
}

CONTACT_2 = {
    "id": 2,
    "first_name": "FirstName",
    "last_name": "LastName",
    "email": "test_user123@gmail.com",
    "phone_number": "0999999998",
    "birthday": "2023-06-01",
    "other_data": "test_data"
}

CONTACT_3 = {
    "id": 3,
    "first_name": "FirstName",
    "last_name": "LastName",
    "email": "user_user@gmail.com",
    "phone_number": "0999999999",
    "birthday": "2023-04-28",
    "other_data": "test_data"
}


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


def test_create_contact_success(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        response = client.post("/api/contacts", json=CONTACT, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201, response.text
        data = response.json()
        assert 'id' in data
        assert data['first_name'] == CONTACT['first_name']
        assert data['last_name'] == CONTACT['last_name']
        assert data['email'] == CONTACT['email']
        assert data['phone_number'] == CONTACT['phone_number']
        assert data['birthday'] == CONTACT['birthday']
        assert data['other_data'] == CONTACT['other_data']


def test_create_contact_email_exist(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        response = client.post("/api/contacts", json=CONTACT_2, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 409, response.text
        data = response.json()
        assert data["detail"] == "Email is exists"


def test_update_contact_success(client, token, monkeypatch):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        put_response = client.put(f"/api/contacts/{CONTACT['id']}",
                                  json=CONTACT,
                                  headers={"Authorization": f"Bearer {token}"})
        assert put_response.status_code == 200, put_response.text
        data = put_response.json()
        assert 'id' in data


def test_update_contact_not_found(client, token, monkeypatch):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        put_response = client.put(f"/api/contacts/{CONTACT_2['id']}",
                                  json=CONTACT_2,
                                  headers={"Authorization": f"Bearer {token}"})
        assert put_response.status_code == 404, put_response.text
        data = put_response.json()
        assert data["detail"] == "Contact not found!"


def test_get_contacts(client, token, monkeypatch):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        response = client.get("/api/contacts", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) == list
        assert "id" in data[0]
        assert CONTACT["first_name"] == data[0]["first_name"]


def test_get_contact_success(client, token, monkeypatch):
    contact_id = 1
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        get_response = client.get(f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {token}"})
        assert get_response.status_code == 200, get_response.text
        data = get_response.json()
        assert "id" in data
        assert data["id"] == CONTACT.get('id')
        assert CONTACT["first_name"] == data["first_name"]


def test_get_contact_not_found(client, token, monkeypatch):
    contact_id = 2
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        response = client.get(f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Contact not found!"


def test_search_success(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        keyword = 'Name'
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        response = client.get(f"/api/contacts/search/keyword={keyword}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) == list
        assert "id" in data[0]


def test_search_not_found(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        keyword = 'Ararat'
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        response = client.get(f"/api/contacts/search/keyword={keyword}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == f'Contacts with keyword: {keyword} not found!'


def test_upcoming_birthdays_list_success(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        days = 30
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        response = client.get(f"/api/contacts/birthdays/{int(days)}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) == list
        assert "id" in data[0]


def test_upcoming_birthdays_list_not_found(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        days = 1
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        response = client.get(f"/api/contacts/birthdays/{int(days)}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == f"There are no birthdays for {days} days"


def test_delete_contact_success(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        response = client.delete(f"/api/contacts/{CONTACT['id']}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text


def test_delete_contact_not_found(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        contact_id = 3
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        response = client.delete(f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Contact not found!"
