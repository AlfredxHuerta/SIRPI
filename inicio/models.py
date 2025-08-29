from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Equipo(models.Model):
    CATEGORIAS = [
        ("seguidor_linea", "Seguidor de línea"),
        ("mini_zumo_rc", "Mini Zumo RC"),
        ("mini_zumo_auto", "Mini Zumo Autónomo"),
    ]

    nombre_equipo = models.CharField(max_length=100)
    nombre_capitan = models.CharField(max_length=100)
    integrantes = models.TextField(help_text="Separados por comas")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)

    def __str__(self):
        return self.nombre_equipo


class Batalla(models.Model):
    numero = models.AutoField(primary_key=True)
    CATEGORIAS = [
        ("SL", "Seguidor de línea"),
        ("MSRC", "Mini Sumo RC"),
        ("MSA", "Mini Sumo Autónomo"),
    ]

    equipos = models.ManyToManyField(Equipo, related_name="batallas")
    #categoria = models.CharField(max_length=10, choices=CATEGORIAS)
    categoria = models.CharField(max_length=10, choices=[("SL", "Seguidor de línea"), ("MSRC", "Mini Sumo RC"), ("MSA", "Mini Sumo Autónomo")])
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    cerrada = models.BooleanField(default=False)
    ganador = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="batallas_ganadas",
    )

    def __str__(self):
        if self.pk:
            nombres = ", ".join([e.nombre_equipo for e in self.equipos.all()])
            return f"Batalla #{self.numero}: {nombres}"
        return "Batalla nueva (sin guardar)"

    def validar_equipos(self):
        if self.equipos.count() < 3:
            raise ValidationError("La batalla debe tener al menos 3 equipos.")

    def cerrar_batalla(self):
        # Validar que la batalla no esté cerrada
        if self.cerrada:
            raise ValueError("La batalla ya está cerrada.")
        # Validar que la batalla tiene ronda (única)
        ronda = getattr(self, "ronda", None)
        if not ronda:
            raise ValueError("No hay ronda asignada a esta batalla.")
        # Validar que la ronda está cerrada para poder cerrar batalla
        if not ronda.cerrada:
            raise ValueError("La ronda aún está abierta.")
        # Validar mínimo equipos
        self.validar_equipos()

        # Determinar ganador por menor tiempo en la ronda
        tiempos = {
            ronda.equipo_1: ronda.tiempo_equipo_1,
            ronda.equipo_2: ronda.tiempo_equipo_2,
        }
        ganador = min(tiempos, key=tiempos.get)

        self.ganador = ganador
        self.cerrada = True
        self.fecha_fin = timezone.now()
        self.save()

        return self.ganador


class Ronda(models.Model):
    batalla = models.OneToOneField(
        'Batalla', on_delete=models.CASCADE, related_name='ronda'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    cerrada = models.BooleanField(default=False)

    def __str__(self):
        return f"Ronda de Batalla #{self.batalla.numero}"

class ParticipacionRonda(models.Model):
    ronda = models.ForeignKey(Ronda, on_delete=models.CASCADE, related_name='participaciones')
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    tiempo = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Tiempo en segundos")
    anotaciones = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('ronda', 'equipo')  # Un equipo solo una participación por ronda

    def __str__(self):
        return f"{self.equipo.nombre_equipo} en {self.ronda}"


# models.py
class EquipoEnEspera(models.Model):
    ronda = models.OneToOneField(Ronda, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Esperando tiempo de {self.equipo.nombre_equipo} en Ronda {self.ronda.id}"


# models.py
class EventoBatalla(models.Model):
    CATEGORIAS = [
        ("SL", "Seguidor de línea"),
        ("MSRC", "Mini Sumo RC"),
        ("MSA", "Mini Sumo Autónomo"),
    ]

    titulo = models.CharField(max_length=200)
    lugar = models.CharField(max_length=200)
    fecha = models.DateField()
    hora = models.TimeField()
    categoria = models.CharField(max_length=10, choices=CATEGORIAS)
    descripcion = models.TextField(blank=True, null=True)
    

    
    imagen = models.ImageField(upload_to="eventos_batalla/", blank=True, null=True)
    archivo = models.FileField(upload_to="archivos_eventos/", blank=True, null=True)
    link_info = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} - {self.fecha}"
