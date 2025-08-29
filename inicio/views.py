from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Batalla
from .forms import EquipoForm  # Asegúrate de importar tu formulario
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from .models import Batalla, Equipo, Ronda
from django.contrib import messages

from .models import ParticipacionRonda,EquipoEnEspera

from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
    # views.py
from django.views.decorators.csrf import csrf_exempt

import json
from django.http import JsonResponse

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from .models import Batalla
from django.contrib import messages
from django.shortcuts import redirect, render



# Vistas para renderizar las páginas
def index(request):
    return render(request, "index.html")


def seguidor_linea(request):
    return render(request, "seguidor_linea.html")


def mini_zumo(request):
    return render(request, "mini_zumo.html")


def carrera_libre(request):
    return render(request, "carrera_libre.html")


def calendario(request):
    return render(request, "calendario.html")


def capturar_equipo(request):
    if request.method == "POST":
        form = EquipoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Equipo registrado con éxito!')
            return redirect(
                "capturar_equipo"
            )  # Redirige a la misma vista por nombre de URL
    else:
        
        form = EquipoForm()

    return render(
        request, "capturar_equipo.html", {"form": form}
    )  # Incluye carpeta 'inicio'

def batallas_seguidor(request):
    batallas = (
        Batalla.objects.all()
    )  # Asegúrate de que esté recuperando las batallas correctamente
    return render(request, "batallas_seguidor.html", {"batallas": batallas})


def ranking(request):
    return render(request, "ranking.html")


# def detalles_batalla(request, batalla_id):
#     batalla = get_object_or_404(Batalla, id=batalla_id)
#     return render(request, 'detalles_batalla.html', {'batalla': batalla})

@login_required
def detalles_batalla(request, batalla_id):
    batalla = Batalla.objects.get(numero=batalla_id)  # Usa `numero` en lugar de `id`
    return render(request, "detalles_batalla.html", {"batalla": batalla})


# Para la pantalla donde se administran las batallas
# views.py
@login_required
def crear_batalla(request):
    equipos = Equipo.objects.all()

    if request.method == "POST":
        equipo_ids = request.POST.getlist("equipos")
        categoria = request.POST.get("categoria")
        descripcion = request.POST.get("descripcion")

        if len(equipo_ids) < 3:
            messages.error(request, "Debes seleccionar al menos 3 equipos.")
            messages.error(request, '¡La batalla NO fue creada!')
            return redirect("crear_batalla")

        batalla = Batalla.objects.create(categoria=categoria, descripcion=descripcion)
        batalla.equipos.set(equipo_ids)
        batalla.save()
        

        ronda = Ronda.objects.create(batalla=batalla)
        messages.success(request, '¡Batalla creada con éxito!')

        # Crear participaciones
        for eid in equipo_ids:
            ParticipacionRonda.objects.create(ronda=ronda, equipo_id=eid)
        
        return redirect("ver_ronda", batalla_id=batalla.pk)
    
    
    return render(request, "crear_batalla.html", {"equipos": equipos})


from django.shortcuts import render, get_object_or_404

@login_required
def ver_ronda(request, batalla_id):
    batalla = get_object_or_404(Batalla, pk=batalla_id)
    ronda = batalla.ronda
    participaciones = ronda.participaciones.select_related("equipo")

    tiempos_completos = all(p.tiempo > 0 for p in participaciones)

    return render(request, "ver_ronda.html", {
        "batalla": batalla,
        "ronda": ronda,
        "participaciones": participaciones,
        "tiempos_completos": tiempos_completos,
    })

@require_POST
def cerrar_ronda(request, batalla_id):
    batalla = get_object_or_404(Batalla, pk=batalla_id)
    ronda = batalla.ronda
    participaciones = ronda.participaciones.all()

    if any(p.tiempo <= 0 for p in participaciones):
        messages.error(request, "Todos los tiempos deben estar registrados.")
        return redirect("ver_ronda", batalla_id=batalla_id)

    # Ordenar participaciones por tiempo
    participaciones_ordenadas = participaciones.order_by("tiempo")

    print("=== Participaciones ordenadas por tiempo ===")
    for p in participaciones_ordenadas:
        print(p.equipo.nombre_equipo, p.tiempo)

    ganador = participaciones_ordenadas.first()
    print("Ganador elegido:", ganador.equipo.nombre_equipo, ganador.tiempo)

    ronda.cerrada = True
    ronda.save()

    batalla.ganador = ganador.equipo
    batalla.cerrada = True
    batalla.fecha_fin = timezone.now()
    batalla.save()

    messages.success(request, f"Ronda cerrada. Ganador: {ganador.equipo.nombre_equipo}")
    return redirect("ver_ronda", batalla_id=batalla_id)

    
    
# views.py
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # O usa el token en JS (preferible como ya lo tienes)
@require_POST
def seleccionar_equipo(request):
    data = json.loads(request.body)
    equipo_id = data["equipo_id"]
    ronda_id = data["ronda_id"]

    equipo = Equipo.objects.get(pk=equipo_id)
    ronda = Ronda.objects.get(pk=ronda_id)

    EquipoEnEspera.objects.update_or_create(
        ronda=ronda,
        defaults={"equipo": equipo}
    )

    return JsonResponse({"status": "ok"})

# views.py
@csrf_exempt
@require_POST
def registrar_tiempo_desde_esp32(request):
    data = json.loads(request.body)
    tiempo = data.get("tiempo")  # por ejemplo 12.45

    # Obtener el equipo en espera más reciente
    equipo_en_espera = EquipoEnEspera.objects.order_by("-timestamp").first()

    if not equipo_en_espera:
        return JsonResponse({"error": "No hay equipo en espera"}, status=400)

    ronda = equipo_en_espera.ronda
    equipo = equipo_en_espera.equipo

    participacion = Participacion.objects.get(ronda=ronda, equipo=equipo)
    if participacion.tiempo > 0:
        return JsonResponse({"error": "Tiempo ya registrado"}, status=400)

    participacion.tiempo = tiempo
    participacion.save()

    return JsonResponse({
        "message": f"Tiempo {tiempo} asignado a {equipo.nombre_equipo}",
        "ronda": ronda.id,
        "equipo": equipo.id
    })


# Login del juez
def login_juez(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard_juez')
        else:
            return render(request, 'login_juez.html', {'error': 'Credenciales inválidas o no eres juez'})
    return render(request, 'login_juez.html')


@login_required
def dashboard_juez(request):
    batallas = Batalla.objects.all().order_by('-fecha_inicio')
    return render(request, 'dashboard_juez.html', {'batallas': batallas})


# views.py
from .models import Batalla, Ronda, ParticipacionRonda  # Asegúrate de importar bien

def ver_detalles_general(request, numero):
    batalla = get_object_or_404(Batalla, numero=numero)

    # Obtenemos la ronda asociada sin usar .rondas (sin related_name)
    ronda = Ronda.objects.filter(batalla=batalla).first()

    # Participaciones ordenadas por tiempo
    participaciones = ParticipacionRonda.objects.filter(ronda=ronda).select_related("equipo").order_by("tiempo")

    return render(request, 'ver_detalles_general.html', {
        'batalla': batalla,
        'ronda': ronda,
        'participaciones': participaciones,
    })
    
# views.py
from .models import EventoBatalla
from datetime import date

def calendario(request):
    eventos = EventoBatalla.objects.filter(fecha__gte=date.today()).order_by('fecha')
    return render(request, 'calendario.html', {'eventos': eventos})


# views.py
from django.shortcuts import render
from .models import Batalla  # Asegúrate de que sea el modelo correcto
import json
# views.py
from django.shortcuts import render
from .models import Batalla, ParticipacionRonda
import json

def ranking_ultima_batalla(request):
    batalla = Batalla.objects.filter(cerrada=True).order_by('-fecha_fin').first()

    if not batalla or not hasattr(batalla, 'ronda'):
        return render(request, "ranking.html", {
            "equipos_json": json.dumps([]),
            "tiempos_json": json.dumps([]),
        })

    participaciones = ParticipacionRonda.objects.filter(ronda=batalla.ronda).order_by('tiempo')

    equipos = [p.equipo.nombre_equipo for p in participaciones]
    tiempos = [float(p.tiempo) for p in participaciones]

    return render(request, "ranking.html", {
        "equipos_json": json.dumps(equipos),
        "tiempos_json": json.dumps(tiempos),
    })
