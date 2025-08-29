from django import forms
from .models import Equipo
import re

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ["nombre_equipo", "nombre_capitan", "integrantes", "categoria"]

        widgets = {
            "nombre_equipo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Los Invencibles"}),
            "nombre_capitan": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Juan Pérez"}),
            "integrantes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ej. María, José, Carlos",
            }),
            "categoria": forms.Select(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get("nombre_equipo", "").strip()
        categoria = cleaned_data.get("categoria")

        if nombre and categoria:
            if Equipo.objects.filter(nombre_equipo__iexact=nombre, categoria=categoria).exists():
                self.add_error("nombre_equipo", "Ya existe un equipo con ese nombre en esta categoría.")

    def clean_integrantes(self):
        integrantes_raw = self.cleaned_data.get("integrantes", "")
        integrantes_lista = [i.strip() for i in integrantes_raw.split(",") if i.strip()]

        if len(integrantes_lista) < 3:
            raise forms.ValidationError("Debes ingresar al menos 3 integrantes separados por comas.")

        return ", ".join(integrantes_lista)

    def clean_nombre_capitan(self):
        nombre = self.cleaned_data.get("nombre_capitan", "").strip()
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError("El nombre del capitán solo puede contener letras y espacios.")
        return nombre
