import unittest
from unittest.mock import MagicMock
from datetime import date

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    confirmed_email,
    update_token,
    update_avatar
    )


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.user_test = User(
            id=1,
            username='username',
            password='password',
            email='test2@gmail.com',

        )

    async def test_get_contact_by_email(self):
        expected_contact = self.user_test

        query_mock = self.session.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = expected_contact

        user = await get_user_by_email('test2@gmail.com', self.session)

        self.assertEqual(user, expected_contact)

    async def test_create(self):
        expected_contact = self.user_test

        add_mock = self.session.add
        commit_mock = self.session.commit
        refresh_mock = self.session.refresh

        contact = await create_user(UserModel(**expected_contact.__dict__), self.session)

        self.assertIsInstance(contact, User)
        self.assertEqual(contact.username, self.user.username)
        self.assertEqual(contact.email, self.user.email)
        self.assertEqual(contact.password, self.user.password)
        self.assertEqual(contact.avatar, None)
        self.assertEqual(contact.refresh_token, None)
        self.assertEqual(contact.confirmed, False)

        self.session.add.assert_called_once_with(contact)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        add_mock.assert_called_once_with(contact)
        commit_mock.assert_called_once()
        refresh_mock.assert_called_once()
