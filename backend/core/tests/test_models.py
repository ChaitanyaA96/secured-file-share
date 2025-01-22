# test_models.py
import os
import uuid

from django.test import TestCase
from django.utils import timezone
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import File, FileShare, User, file_upload_path


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
            first_name="Test",
            last_name="User",
            role="user",
            mfa_enabled=False,
            email_verified=False,
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.last_name, "User")
        self.assertFalse(self.user.is_active)

    def test_superuser_creation(self):
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword",
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)


class FileModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword'
        )
        # Create a file instance
        self.file = File.objects.create(
            name='test_file.txt',
            owner=self.user,
            file=SimpleUploadedFile(
                name='test_file.txt',
                content=b'This is a test file content.',
                content_type='text/plain'
            ),
        )

    def test_file_creation(self):
        self.assertEqual(self.file.name, "test_file.txt")
        self.assertEqual(self.file.owner, self.user)

    def test_file_encryption(self):
        self.file.encrypt_file()
        self.assertIsNotNone(self.file.encrypted_key)

    def test_file_decryption(self):
        self.file.encrypt_file()
        decrypted_content = self.file.decrypt_file()
        self.assertIsNotNone(decrypted_content)


class FileShareModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password"
        )
        self.file = File.objects.create(
            name="testfile.txt",
            owner=self.user,
            file="path/to/testfile.txt",
            encrypted_key=os.urandom(32),
        )
        self.share = FileShare.objects.create(
            file=self.file,
            shared_by=self.user,
            shared_with="recipient@example.com",
            share_type="view",
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )

    def test_fileshare_creation(self):
        self.assertEqual(self.share.file, self.file)
        self.assertEqual(self.share.shared_by, self.user)
        self.assertEqual(self.share.shared_with, "recipient@example.com")

    def test_fileshare_expiry(self):
        self.assertFalse(self.share.is_expired())
        self.share.expires_at = timezone.now() - timezone.timedelta(hours=1)
        self.share.save()
        self.assertTrue(self.share.is_expired())
