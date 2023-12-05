from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from myapp.models import Beekeepers, HivesPlaces, Hives, Mothers, Visits, Tasks


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

    def clean_name(self):
        beekeeper = self.cleaned_data.get('beekeeper')
        name = self.cleaned_data.get('name')

        # Kontrola, zda záznam s daným beekeeper_id a place_name již existuje
        if HivesPlaces.objects.filter(beekeeper=beekeeper, name=name).exists():
            raise forms.ValidationError("Záznam s tímto jménem již existuje pro daného včelaře.")

        return name

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
        mothers_queryset = Mothers.objects.filter(hive__place__beekeeper__username=user.username)
        self.fields['ancestor'].queryset = mothers_queryset

class AddVisit(forms.ModelForm):
    date = forms.CharField(initial=timezone.now().strftime('%d. %m. %Y'))
    performed_tasks = forms.ModelMultipleChoiceField(
        queryset=Tasks.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Visits
        fields = ['date', 'inspection_type', 'condition', 'hive_body_size',
                  'honey_supers_size', 'honey_yield', 'medication_application',
                  'disease', 'mite_drop', 'performed_tasks']

    def clean_date(self):
        raw_date = self.cleaned_data['date']
        formatted_date = timezone.datetime.strptime(raw_date, '%d. %m. %Y').strftime('%Y-%m-%d')
        return formatted_date


class ChangeHivesPlace(forms.Form):
    old_hives_place = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        hives_place_id = kwargs.pop('hives_place_id', None)
        super(ChangeHivesPlace, self).__init__(*args, **kwargs)

        self.fields['selected_hives'] = forms.ModelMultipleChoiceField(
            queryset=Hives.objects.filter(place__beekeeper=user),
            widget=forms.CheckboxSelectMultiple,
            label='Vyberte včelstva'
        )

        self.fields['new_hives_place'] = forms.ModelChoiceField(
            queryset=HivesPlaces.objects.filter(beekeeper=user, active=True).exclude(id=hives_place_id),
            label='Vyberte nové stanoviště',
        )

