from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Batalla, Ronda, ParticipacionRonda, Equipo, EventoBatalla


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ("nombre_equipo", "nombre_capitan", "categoria", "integrantes")
    search_fields = ("nombre_equipo", "nombre_capitan")
    list_filter = ("categoria",)


class ParticipacionRondaInline(admin.TabularInline):
    model = ParticipacionRonda
    extra = 0
    can_delete = False
    fields = ('equipo', 'tiempo', 'anotaciones')  # No poner 'batalla' aquí
    readonly_fields = ()

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.cerrada:
            return [f.name for f in self.model._meta.fields]
        return []


@admin.register(Ronda)
class RondaAdmin(admin.ModelAdmin):
    list_display = ("batalla", "cerrada", "fecha")
    inlines = [ParticipacionRondaInline]
    list_filter = ("batalla", "cerrada")
    search_fields = ("batalla__numero",)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.cerrada:
            return [f.name for f in obj._meta.fields]
        return []


@admin.register(Batalla)
class BatallaAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "get_equipos",
        "categoria",
        "cerrada",
        "fecha_inicio",
        "fecha_fin",
        "ganador",
    )
    list_filter = ("categoria", "cerrada")
    search_fields = ("numero",)
    filter_horizontal = ("equipos",)

    actions = ["cerrar_batalla"]

    def get_equipos(self, obj):
        return ", ".join(e.nombre_equipo for e in obj.equipos.all())
    get_equipos.short_description = "Equipos"

    def cerrar_batalla(self, request, queryset):
        for batalla in queryset:
            try:
                ganador = batalla.cerrar_batalla()
                self.message_user(
                    request,
                    f"Batalla {batalla.numero} cerrada correctamente. Ganador: {ganador.nombre_equipo}",
                )
            except Exception as e:
                self.message_user(request, f"Error: {str(e)}", level="error")
        return HttpResponseRedirect(reverse("admin:inicio_batalla_changelist"))

    def save_model(self, request, obj, form, change):
        obj.full_clean()  # valida mínimo 3 equipos
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        # Crear ronda automáticamente si no existe y hay equipos asignados
        if not hasattr(obj, "ronda") and obj.equipos.exists():
            ronda = Ronda.objects.create(batalla=obj)
            for equipo in obj.equipos.all():
                ParticipacionRonda.objects.create(
                    ronda=ronda,
                    equipo=equipo,
                    tiempo=0,
                    anotaciones="",
                )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.cerrada:
            return [f.name for f in obj._meta.fields]
        return []


@admin.register(EventoBatalla)
class EventoBatallaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha', 'hora', 'categoria', 'lugar')
    list_filter = ('categoria', 'fecha')
    search_fields = ('titulo', 'descripcion', 'lugar')
