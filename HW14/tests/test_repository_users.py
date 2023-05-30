import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    confirmed_email,
    update_token
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
            confirmed='False',
            avatar='https://example.com/avatar.jpg'

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
        self.assertEqual(contact.username, self.user_test.username)
        self.assertEqual(contact.email, self.user_test.email)
        self.assertEqual(contact.password, self.user_test.password)
        self.assertNotEqual(contact.avatar, "gravatar")
        self.assertEqual(contact.refresh_token, None)

        self.session.add.assert_called_once_with(contact)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        add_mock.assert_called_once_with(contact)
        commit_mock.assert_called_once()
        refresh_mock.assert_called_once()

    async def test_update_token(self):
        expected_contact = self.user_test
        token = 'new token'

        self.session.commit = MagicMock()
        await update_token(expected_contact, token, self.session)

        self.assertEqual(expected_contact.refresh_token, token)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        email = 'test@example.com'

        user_mock = MagicMock(spec=User)
        user_mock.confirmed = True

        self.session.query().filter().one_or_none.return_value = user_mock
        self.session.commit = MagicMock()

        await confirmed_email(email, self.session)

        self.assertTrue(user_mock.confirmed)
        self.session.commit.assert_called_once()
