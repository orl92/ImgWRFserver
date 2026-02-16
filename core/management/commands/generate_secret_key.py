import os
import sys
from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key
from cryptography.fernet import Fernet

class Command(BaseCommand):
    help = 'Genera una ENCRYPTION_KEY y una SECRET_KEY cifrada para Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--env-file',
            type=str,
            default='.env',
            help='Ruta al archivo .env (por defecto: .env)',
        )
        parser.add_argument(
            '--update-env',
            action='store_true',
            help='Actualiza el archivo .env con las nuevas claves (si existe)',
        )
        parser.add_argument(
            '--show-only',
            action='store_true',
            help='Muestra las claves sin guardarlas en el archivo .env',
        )

    def handle(self, *args, **options):
        env_file = options['env_file']
        update_env = options['update_env']
        show_only = options['show_only']

        # Generar ENCRYPTION_KEY
        encryption_key = Fernet.generate_key().decode()
        # Generar SECRET_KEY en texto plano
        raw_secret_key = get_random_secret_key()
        # Cifrar la SECRET_KEY
        fernet = Fernet(encryption_key.encode())
        encrypted_secret_key = fernet.encrypt(raw_secret_key.encode()).decode()

        self.stdout.write(self.style.SUCCESS('Claves generadas correctamente:\n'))
        self.stdout.write(f'ENCRYPTION_KEY={encryption_key}')
        self.stdout.write(f'SECRET_KEY (cifrada)={encrypted_secret_key}')
        self.stdout.write(self.style.WARNING('\n(SECRET_KEY original en texto plano, NO la guardes):'))
        self.stdout.write(raw_secret_key)

        if not show_only and update_env:
            self.update_env_file(env_file, encryption_key, encrypted_secret_key)
        elif not show_only:
            self.stdout.write(self.style.WARNING(
                '\nPara actualizar tu archivo .env automáticamente, ejecuta con --update-env'
            ))

    def update_env_file(self, env_file, encryption_key, encrypted_secret_key):
        """Actualiza o crea el archivo .env con las nuevas claves."""
        try:
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []

            # Diccionario con las nuevas claves
            new_vars = {
                'ENCRYPTION_KEY': encryption_key,
                'SECRET_KEY': encrypted_secret_key,
            }

            # Actualizar o añadir líneas
            updated_lines = []
            found = {key: False for key in new_vars}
            for line in lines:
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith('#'):
                    for key in new_vars:
                        if line_stripped.startswith(f'{key}='):
                            updated_lines.append(f'{key}={new_vars[key]}\n')
                            found[key] = True
                            break
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)

            # Añadir las que no se encontraron
            for key, value in new_vars.items():
                if not found[key]:
                    updated_lines.append(f'{key}={value}\n')

            # Escribir de vuelta
            with open(env_file, 'w') as f:
                f.writelines(updated_lines)

            self.stdout.write(self.style.SUCCESS(
                f'\nArchivo {env_file} actualizado con las nuevas claves.'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Error al actualizar {env_file}: {e}'
            ))
            sys.exit(1)
