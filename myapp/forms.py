from django import forms
from django.contrib.auth.forms import UserCreationForm
from myapp.models import Beekeepers, HivesPlaces, Hives, Mothers


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    beekeeper_id = forms.IntegerField()

    class Meta:
        model = Beekeepers
        fields = ['username', 'email', 'password1', 'password2', 'beekeeper_id']


class AddHivesPlace(forms.ModelForm):
    class Meta:
        model = HivesPlaces
        fields = ['name', 'type', 'location', 'comment']


class AddHive(forms.ModelForm):
    class Meta:
        model = Hives
        fields = ['type', 'size', 'comment']


class AddMother(forms.ModelForm):
    class Meta:
        model = Mothers
        fields = ['ancestor', 'mark', 'year', 'male_line', 'female_line', 'comment']

    def __init__(self, user, *args, **kwargs):
        super(AddMother, self).__init__(*args, **kwargs)
        # Omezit hodnoty pro 'ancestor' pouze na záznamy z tabulky Mothers, které jsou propojené s přihlášeným uživatelem
        self.fields['ancestor'].queryset = Mothers.objects.filter(hive__place__beekeeper__username=user.username)
