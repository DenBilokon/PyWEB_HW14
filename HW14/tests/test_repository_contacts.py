import datetime
import unittest
from unittest.mock import MagicMock
from datetime import date

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_contacts,
    search_contact,
    get_contact_by_email,
    get_contact_by_id,
    get_contact_by_phone,
    upcoming_birthdays, remove, update, create
)


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.contact_test = Contact(
            id=1,
            first_name='Test',
            last_name='Testenko',
            email='Testenko@gmail.com',
            phone_number='0988888877',
            birthday=datetime.date(year=1991, month=1, day=23),
            other_data=None
        )

    async def test_get_contacts(self):
        user = User(id=1)
        session = MagicMock(spec=Session)

        expected_contacts = [
            Contact(id=1, user_id=1, first_name='Test1', last_name='Test1', email='test1@example.com',
                    birthday=date.today()),
            Contact(id=2, user_id=1, first_name='Test2', last_name='Test2', email='test2@example.com',
                    birthday=date.today())
        ]

        query_mock = MagicMock()
        session.query.return_value = query_mock

        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock

        filter_mock.all.return_value = expected_contacts

        contacts = await get_contacts(user, session)

        self.assertEqual(contacts, expected_contacts)

    async def test_get_contact_by_id(self):
        expected_contact = self.contact_test

        query_mock = self.session.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = expected_contact

        contact = await get_contact_by_id(self.user, 1, self.session)

        self.assertEqual(contact, expected_contact)

    async def test_get_contact_by_email(self):
        expected_contact = self.contact_test

        query_mock = self.session.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = expected_contact

        contact = await get_contact_by_email(self.user, 'test1@example.com', self.session)

        self.assertEqual(contact, expected_contact)

    async def test_get_contact_by_phone(self):
        expected_contact = self.contact_test

        query_mock = self.session.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = expected_contact

        contact = await get_contact_by_phone(self.user, '0988888877', self.session)

        self.assertEqual(contact, expected_contact)

    async def test_create(self):
        expected_contact = self.contact_test

        add_mock = self.session.add
        commit_mock = self.session.commit

        contact = await create(self.user, ContactModel(**expected_contact.__dict__), self.session)

        self.assertEqual(contact.first_name, expected_contact.first_name)
        self.assertEqual(contact.last_name, expected_contact.last_name)
        self.assertEqual(contact.email, expected_contact.email)
        self.assertEqual(contact.phone_number, expected_contact.phone_number)
        self.assertEqual(str(contact.birthday), str(expected_contact.birthday))
        self.assertEqual(contact.other_data, expected_contact.other_data)
        add_mock.assert_called_once_with(contact)
        commit_mock.assert_called_once()

    async def test_update(self):
        expected_contact = self.contact_test

        query_mock = self.session.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = self.contact_test

        commit_mock = self.session.commit

        contact = await update(self.user, 1, expected_contact, self.session)

        self.assertEqual(contact, self.contact_test)
        self.assertEqual(contact.first_name, expected_contact.first_name)
        self.assertEqual(contact.last_name, expected_contact.last_name)
        self.assertEqual(contact.email, expected_contact.email)
        self.assertEqual(contact.phone_number, expected_contact.phone_number)
        self.assertEqual(contact.birthday, expected_contact.birthday)
        self.assertEqual(contact.other_data, expected_contact.other_data)
        commit_mock.assert_called_once()

    async def test_remove(self):
        query_mock = self.session.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = self.contact_test

        delete_mock = self.session.delete
        commit_mock = self.session.commit

        contact = await remove(self.user, 1, self.session)

        self.assertEqual(contact, self.contact_test)
        delete_mock.assert_called_once_with(contact)
        commit_mock.assert_called_once()

    async def test_search_contact(self):
        keyword = 'test'

        query_mock = self.session.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.all.return_value = [self.contact_test]

        contacts = await search_contact(self.user, keyword, self.session)

        self.assertEqual(contacts, [self.contact_test])

    async def test_get_contacts_birthdays(self):
        days = 7
        today = date.today()
        contacts = [
            Contact(id=1, first_name='John', last_name='Doe', email='john@example.com', birthday=today),
            Contact(id=2, first_name='Jane', last_name='Smith', email='jane@example.com', birthday=today),
        ]
        self.session.query.return_value.filter.return_value.all.return_value = contacts

        result = await upcoming_birthdays(self.user, days, self.session)

        self.assertEqual(len(result), len(contacts))

        for i in range(len(result)):
            self.assertEqual(result[i].id, contacts[i].id)
            self.assertEqual(result[i].first_name, contacts[i].first_name)
            self.assertEqual(result[i].last_name, contacts[i].last_name)
            self.assertEqual(result[i].email, contacts[i].email)
            self.assertEqual(result[i].birthday, contacts[i].birthday)
