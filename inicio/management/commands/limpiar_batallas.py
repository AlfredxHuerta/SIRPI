from django.core.management.base import BaseCommand
from django.db import connection
from inicio.models import Batalla, Ronda, ParticipacionRonda

class Command(BaseCommand):
    help = 'Elimina todas las batallas y reinicia los contadores de ID'

    def handle(self, *args, **kwargs):
        self.stdout.write("Eliminando batallas, rondas y participaciones...")

        ParticipacionRonda.objects.all().delete()
        Ronda.objects.all().delete()
        Batalla.objects.all().delete()

        with connection.cursor() as cursor:
            # Reiniciar secuencias de autoincremento (SQLite y PostgreSQL)
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='inicio_batalla'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='inicio_ronda'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='inicio_participacionronda'")

        self.stdout.write(self.style.SUCCESS("✔️ Base de datos limpiada y contadores reiniciados."))
