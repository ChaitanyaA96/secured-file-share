from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now, timedelta
import pyotp
import enum
import uuid
import os
from backend import settings
from django.utils import timezone
from django.conf import settings
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        
        email = self.normalize_email(email)
        extra_fields.setdefault("role", UserRole.USER.value)
        extra_fields.setdefault("mfa_enabled", False)
        extra_fields.setdefault("email_verified", False)
        extra_fields.setdefault("is_active", False)
        extra_fields.setdefault("is_staff", False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", UserRole.ADMIN.value)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("mfa_enabled", True)
        extra_fields.setdefault("email_verified", True)
        extra_fields.setdefault("mfa_secret", pyotp.random_base32())
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=10, choices=[(role.value, role.value) for role in UserRole], default=UserRole.GUEST.value)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=32, null=True, blank=True)
    email_verification_expiry = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
def file_upload_path(instance, filename):
    # Organize files by user ID and generate unique names
    return os.path.join('uploads', str(instance.owner.id), str(uuid.uuid4()), filename)

class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default="")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to=file_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    encrypted_key = models.BinaryField()

    def encrypt_file(self):
        # Generate a 256-bit encryption key
        print("encrypting file", self.file.name)
        key = os.urandom(32)
        iv = os.urandom(12)

        # Store the encryption key for later decryption
        self.encrypted_key = encrypt_key(key)

        # Perform AES encryption
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Read file content
        with self.file.open('rb') as f:
            file_data = f.read()

        # Encrypt the file data
        encrypted_data = iv + encryptor.update(file_data) + encryptor.finalize() + encryptor.tag

        # Overwrite the file with encrypted content
        with self.file.open('wb') as f:
            f.write(encrypted_data)

        print("encrypted file", self.file.name)
        self.save()

    def decrypt_file(self):
        # Retrieve the encryption key
        key = decrypt_key(self.encrypted_key)
        if not key:
            raise ValueError("Encryption key is missing")

        # Read the encrypted file data
        with self.file.open('rb') as f:
            encrypted_data = f.read()

        # Extract the IV from the encrypted data
        iv = encrypted_data[:12]
        tag = encrypted_data[-16:]
        encrypted_file_data = encrypted_data[12:-16]

        # Perform AES decryption
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_file_data) + decryptor.finalize()

        return decrypted_data

    def __str__(self):
        return self.file.name

# File Sharing Model
class FileShare(models.Model):
    SHARE_TYPE_CHOICES = (
        ("view", "View Only"),
        ("download", "Download"),
    )

    file = models.ForeignKey(File, on_delete=models.CASCADE)
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shared_with = models.EmailField(blank=True, null=True)  # Specific user for restricted access
    share_type = models.CharField(max_length=10, choices=SHARE_TYPE_CHOICES)
    shared_link = models.UUIDField(default=uuid.uuid4, editable=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    used = models.BooleanField(default=False)  # For one-time access
    public = models.BooleanField(default=False)  # Public access flag
    passphrase = models.CharField(max_length=255, blank=True, null=True)  # Optional passphrase for public links
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at if self.expires_at else False

    def __str__(self):
        return f"{self.file.name} shared with {self.shared_with or 'Link'}"


def encrypt_key(key: bytes) -> bytes:
    """
    Encrypts the given key using AES-GCM with a master key.
    Returns the encrypted key with IV and tag appended.
    """
    iv = os.urandom(12)  # Generate a random 96-bit IV
    cipher = Cipher(algorithms.AES(settings.MASTER_KEY), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_key = iv + encryptor.update(key) + encryptor.finalize() + encryptor.tag
    return encrypted_key

def decrypt_key(encrypted_key: bytes) -> bytes:
    """
    Decrypts the given key using AES-GCM with a master key.
    Extracts IV and tag from the encrypted key.
    """
    iv = encrypted_key[:12]
    tag = encrypted_key[-16:]
    key_data = encrypted_key[12:-16]
    cipher = Cipher(algorithms.AES(settings.MASTER_KEY), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(key_data) + decryptor.finalize()
