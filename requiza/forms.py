from django import forms
from .models import Requiza

class RequizaForm(forms.ModelForm):
    class Meta:
        model = Requiza
        fields = ['producto', 'cantidad', 'motivo']