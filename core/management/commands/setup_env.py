import os
from django.core.management.base import BaseCommand, CommandError
from django.core.management.utils import get_random_secret_key
from cryptography.fernet import Fernet

class Command(BaseCommand):
    help = 'Genera un archivo .env completo con todas las variables necesarias para el proyecto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--env-file',
            type=str,
            default='.env',
            help='Ruta al archivo .env (por defecto: .env)',
        )
        parser.add_argument(
            '--non-interactive',
            action='store_true',
            help='Modo no interactivo: usa valores por defecto sin preguntar',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Sobrescribe el archivo .env si existe sin preguntar',
        )
        parser.add_argument(
            '--only-keys',
            action='store_true',
            help='Solo genera y muestra las claves (ENCRYPTION_KEY y SECRET_KEY cifrada), no crea .env',
        )

    def handle(self, *args, **options):
        env_file = options['env_file']
        non_interactive = options['non_interactive']
        force = options['force']
        only_keys = options['only_keys']

        # --- Generar claves (siempre las necesitamos) ---
        self.stdout.write("Generando claves de cifrado...")
        encryption_key = Fernet.generate_key().decode()
        raw_secret_key = get_random_secret_key()
        fernet = Fernet(encryption_key.encode())
        encrypted_secret_key = fernet.encrypt(raw_secret_key.encode()).decode()

        # Si solo queremos las claves, las mostramos y terminamos
        if only_keys:
            self.stdout.write(self.style.SUCCESS('\nClaves generadas:\n'))
            self.stdout.write(f'ENCRYPTION_KEY={encryption_key}')
            self.stdout.write(f'SECRET_KEY (cifrada)={encrypted_secret_key}')
            self.stdout.write(self.style.WARNING('\n(SECRET_KEY original en texto plano, NO la guardes):'))
            self.stdout.write(raw_secret_key)
            return

        # --- Verificar si el archivo existe (solo si vamos a escribir) ---
        if os.path.exists(env_file) and not force:
            answer = input(f"El archivo {env_file} ya existe. ¿Deseas sobrescribirlo? (s/N): ")
            if answer.lower() != 's':
                self.stdout.write(self.style.WARNING("Operación cancelada."))
                return

        # Diccionario para almacenar las variables
        env_vars = {}

        env_vars['ENCRYPTION_KEY'] = encryption_key
        env_vars['SECRET_KEY'] = encrypted_secret_key

        # --- Configuración básica de Django ---
        if non_interactive:
            debug = 'True'
            allowed_hosts = 'localhost,127.0.0.1'
            csrf_origins = ''
        else:
            debug = input("DEBUG (True/False) [True]: ") or 'True'
            default_hosts = 'localhost,127.0.0.1'
            allowed_hosts = input(f"ALLOWED_HOSTS (separados por coma) [{default_hosts}]: ") or default_hosts
            csrf_origins = input("CSRF_TRUSTED_ORIGINS (separados por coma, incluyendo esquema http:// o https://) [dejar vacío]: ") or ''

        env_vars['DEBUG'] = debug
        env_vars['ALLOWED_HOSTS'] = allowed_hosts
        env_vars['CSRF_TRUSTED_ORIGINS'] = csrf_origins

        # --- Base de datos (variables individuales) ---
        if non_interactive:
            use_sqlite = True
        else:
            use_sqlite = input("¿Usar SQLite como base de datos? (s/N): ").lower() == 's'

        if use_sqlite:
            self.stdout.write("Usando SQLite (configuración por defecto).")
            # No se agregan variables de base de datos
        else:
            self.stdout.write("Configuración de base de datos (PostgreSQL/MySQL/Oracle):")
            db_engine_map = {
                'postgresql': 'django.db.backends.postgresql',
                'mysql': 'django.db.backends.mysql',
                'oracle': 'django.db.backends.oracle',
            }
            engine_choice = input("Motor (postgresql, mysql, oracle) [postgresql]: ") or 'postgresql'
            env_vars['DB_ENGINE'] = db_engine_map.get(engine_choice, 'django.db.backends.postgresql')
            env_vars['DB_NAME'] = input("Nombre de la base de datos: ")
            env_vars['DB_USER'] = input("Usuario: ")
            env_vars['DB_PASSWORD'] = input("Contraseña: ")
            env_vars['DB_HOST'] = input("Host [localhost]: ") or 'localhost'
            env_vars['DB_PORT'] = input("Puerto [5432 para PostgreSQL, 3306 para MySQL]: ") or '5432'

        # --- Celery / Redis ---
        if non_interactive:
            celery_broker = 'redis://localhost:6379/0'
            celery_backend = 'redis://localhost:6379/0'
        else:
            default_redis = 'redis://localhost:6379/0'
            celery_broker = input(f"CELERY_BROKER_URL [{default_redis}]: ") or default_redis
            celery_backend = input(f"CELERY_RESULT_BACKEND [{default_redis}]: ") or default_redis

        env_vars['CELERY_BROKER_URL'] = celery_broker
        env_vars['CELERY_RESULT_BACKEND'] = celery_backend

        # --- Correo electrónico (opcional) ---
        if non_interactive:
            configure_email = False
        else:
            configure_email = input("¿Quieres configurar correo electrónico? (s/N): ").lower() == 's'

        if configure_email:
            env_vars['EMAIL_HOST'] = input("EMAIL_HOST [smtp.gmail.com]: ") or 'smtp.gmail.com'
            env_vars['EMAIL_PORT'] = input("EMAIL_PORT [587]: ") or '587'
            env_vars['EMAIL_HOST_USER'] = input("EMAIL_HOST_USER: ")
            env_vars['EMAIL_HOST_PASSWORD'] = input("EMAIL_HOST_PASSWORD: ")
            env_vars['EMAIL_USE_TLS'] = input("EMAIL_USE_TLS (True/False) [True]: ") or 'True'

        # --- Escribir archivo .env ---
        try:
            with open(env_file, 'w') as f:
                f.write("# Archivo de configuración de entorno para Django Meteo Simulation API\n")
                f.write("# Generado automáticamente por el comando setup_env\n\n")
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            self.stdout.write(self.style.SUCCESS(f"Archivo {env_file} creado correctamente."))
            self.stdout.write(self.style.WARNING("\nIMPORTANTE: La SECRET_KEY original (no cifrada) es:"))
            self.stdout.write(raw_secret_key)
            self.stdout.write(self.style.WARNING("Guárdala en un lugar seguro, pero NO la incluyas en el .env"))
        except Exception as e:
            raise CommandError(f"Error al escribir el archivo: {e}")
