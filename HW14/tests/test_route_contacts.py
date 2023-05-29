# from unittest.mock import MagicMock, patch, AsyncMock
#
# import pytest
#
# from src.database.models import User
# from src.services.auth import auth_service
#
#
# CONTACT = {
#               "first_name": "FirstName",
#               "last_name": "LastName",
#               "email": "test_user123@gmail.com",
#               "phone_number": "0999999999",
#               "birthday": "2023-05-28",
#               "other_data": "test_data"
#             }
#
#
# @pytest.fixture()
# def token(client, user, session, monkeypatch):
#     mock_send_email = MagicMock()
#     monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
#     client.post("/api/auth/signup", json=user)
#     current_user: User = session.query(User).filter(User.email == user.get('email')).first()
#     current_user.confirmed = True
#     session.commit()
#     response = client.post(
#         "/api/auth/login",
#         data={"username": user.get('email'), "password": user.get('password')},
#     )
#     data = response.json()
#     return data["access_token"]
#
#
# def test_create_contact(client, token):
#     with patch.object(auth_service, 'r') as r_mock:
#         r_mock.get.return_value = None
#         response = client.post("/api/contacts", json=CONTACT, headers={"Authorization": f"Bearer {token}"})
#         assert response.status_code == 201, response.text
#         data = response.json()
#         assert 'id' in data
#         assert data['first_name'] == CONTACT['first_name']
#         assert data['last_name'] == CONTACT['last_name']
#         assert data['email'] == CONTACT['email']
#         assert data['phone_number'] == CONTACT['phone_number']
#         assert data['birthday'] == CONTACT['birthday']
#         assert data['other_data'] == CONTACT['other_data']
#
#
# def test_get_contact(client, token, monkeypatch):
#     with patch.object(auth_service, "r") as redis_mock:
#         redis_mock.get.return_value = None
#         monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
#         monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
#         monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
#         response = client.get("/api/contacts", headers={"Authorization": f"Bearer {token}"})
#         assert response.status_code == 200, response.text
#         data = response.json()
#         assert type(data) == list
#         assert "id" in data[0]
#         assert CONTACT["first_name"] == data[0]["first_name"]
