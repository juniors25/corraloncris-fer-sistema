import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import Usuario

if not Usuario.objects.filter(username='admin').exists():
    Usuario.objects.create_superuser(
        username='admin',
        email='admin@ferreteria.com',
        password='admin123',
        role='admin',
        telefono='0000000000'
    )
    print("Superusuario creado exitosamente")
    print("Usuario: admin")
    print("Contraseña: admin123")
else:
    print("El usuario admin ya existe")