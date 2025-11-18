from django import forms


class OrganizacionLoginForm(forms.Form):
    company = forms.CharField(max_length=200, label='Empresa', required=False)
    username = forms.CharField(max_length=150, label='Usuario')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')

    def clean_company(self):
        return self.cleaned_data.get('company', '').strip()

    def __init__(self, *args, **kwargs):
        # Accept and store `request` if LoginView passes it in get_form_kwargs
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
