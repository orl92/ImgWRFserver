# generate_secret.py
from cryptography.fernet import Fernet
from django.core.management.utils import get_random_secret_key

# Generar ENCRYPTION_KEY
encryption_key = Fernet.generate_key()
print("Guarda esto en tu .env como ENCRYPTION_KEY:")
print(encryption_key.decode())

# Generar SECRET_KEY de Django
raw_secret_key = get_random_secret_key()
print("\nSECRET_KEY en texto plano (NO la guardes así):")
print(raw_secret_key)

# Cifrar la SECRET_KEY
fernet = Fernet(encryption_key)
encrypted = fernet.encrypt(raw_secret_key.encode())
print("\nGuarda esto en tu .env como SECRET_KEY (valor cifrado):")
print(encrypted.decode())
