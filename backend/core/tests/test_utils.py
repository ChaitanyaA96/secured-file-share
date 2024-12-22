from django.core import mail
from django.test import TestCase

from core.utils import send_email


class UtilsTestCase(TestCase):
    def test_send_email(self):
        send_email(
            to=["recipient@example.com"],
            subject="Test Subject",
            message="Test Message",
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Subject")
        self.assertEqual(mail.outbox[0].body, "Test Message")
        self.assertIn("recipient@example.com", mail.outbox[0].to)
