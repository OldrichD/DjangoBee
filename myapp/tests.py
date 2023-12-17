from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from myapp.forms import LoginForm, RegisterForm, AddHivesPlace, AddHive, AddMother, AddVisit, EditVisit, EditHivesPlace
from myapp.models import Beekeepers, HivesPlaces, Hives, Mothers, Tasks, Visits


class MyappTestCase(TestCase):
    def setUp(self):
        # Vytvoření testovacích dat
        self.user = Beekeepers.objects.create_user(username='testuser', password='testpassword', beekeeper_id=1)
        self.hives_place = HivesPlaces.objects.create(beekeeper=self.user, name='TestPlace', type='TestType',
                                                      location='TestLocation', comment='TestComment', active=True)
        self.hive = Hives.objects.create(place=self.hives_place, number=1, type='TestType', comment='TestComment',
                                         active=True)

    def test_index_view(self):
        # Testování zobrazení úvodní stránky, když uživatel není přihlášen
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        # Testování zobrazení úvodní stránky, když je uživatel přihlášen
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('index'))
        self.assertRedirects(response, reverse('overview'))

    def test_login_user_view(self):
        # Testování přihlašovacího pohledu, když uživatel není přihlášen
        response = self.client.get(reverse('login_user'))
        self.assertEqual(response.status_code, 200)

        # Testování přihlašovacího pohledu, když je uživatel přihlášen
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('login_user'))
        self.assertRedirects(response, reverse('overview'))

        # Testování přihlášení s platnými údaji
        response = self.client.post(reverse('login_user'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertRedirects(response, reverse('overview'))

        # Testování přihlášení s neplatnými údaji
        response = self.client.post(reverse('login_user'), {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 302)

    def test_add_hives_place_view(self):
        # Testování pohledu pro přidání stanoviště
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('add_hives_place'))
        self.assertEqual(response.status_code, 200)

        # Testování odeslání formuláře pro přidání stanoviště s platnými údaji
        response = self.client.post(reverse('add_hives_place'), {'name': 'Nové Stanoviště', 'type': 'typ stanoviště'})

        # Aktualizovaný kód: Očekávejte přesměrování s HTTP kódem 302
        self.assertRedirects(response, reverse('overview'), status_code=302)

    def tearDown(self):
        # Úklid testovacích dat
        self.user.delete()
        self.hives_place.delete()
        self.hive.delete()


class ModelTestCase(TestCase):
    def setUp(self):
        # Vytvoření testovacích dat
        self.user = Beekeepers.objects.create_user(username='testuser', password='testpassword', beekeeper_id=1)
        self.hives_place = HivesPlaces.objects.create(beekeeper=self.user, name='TestPlace', type='TestType', location='TestLocation', comment='TestComment', active=True)
        self.hive = Hives.objects.create(place=self.hives_place, number=1, type='TestType', comment='TestComment', active=True)
        self.mother = Mothers.objects.create(hive=self.hive, mark='TestMother', year=2022, male_line='TestMaleLine', female_line='TestFemaleLine', comment='TestComment', active=True)
        self.task = Tasks.objects.create(name='TestTask')
        self.visit = Visits.objects.create(hive=self.hive, date='2022-01-01', inspection_type='TestInspection', condition=5, hive_body_size=3, honey_supers_size=2, honey_yield=10.5, medication_application='TestMedication', disease='TestDisease', mite_drop=20, active=True, comment='TestComment')
        self.visit.performed_tasks.add(self.task)

    def test_user_model(self):
        self.assertEqual(self.user.beekeeper_id, 1)

    def test_hives_places_model(self):
        self.assertEqual(str(self.hives_place), 'TestPlace')

    def test_hives_model(self):
        self.assertEqual(str(self.hive), '1')
        self.assertEqual(self.hive.last_honey_yield(), self.visit)
        self.assertEqual(self.hive.last_medication_application(), self.visit)
        self.assertEqual(self.hive.last_mite_drop(), self.visit)
        self.assertEqual(self.hive.last_disease(), self.visit)
        self.assertEqual(self.hive.last_comment(), self.visit)

    def test_mothers_model(self):
        self.assertEqual(self.mother.display_name(), 'TestMother (linie: TestFemaleLine)')

    def test_tasks_model(self):
        self.assertEqual(str(self.task), 'TestTask')

    def test_visits_model(self):
        self.assertEqual(str(self.visit), '2022-01-01')
        self.assertEqual(self.visit.hive.number, 1)
        self.assertEqual(self.visit.performed_tasks.first(), self.task)

    def tearDown(self):
        # Úklid testovacích dat
        self.user.delete()
        self.hives_place.delete()
        self.hive.delete()
        self.mother.delete()
        self.task.delete()
        self.visit.delete()


class FormTestCase(TestCase):
    def setUp(self):
        # Vytvoření testovacích dat
        self.user = Beekeepers.objects.create_user(username='testuser', password='testpassword', beekeeper_id=1)
        self.hives_place = HivesPlaces.objects.create(beekeeper=self.user, name='TestPlace', type='TestType',
                                                      location='TestLocation', comment='TestComment', active=True)
        self.hive = Hives.objects.create(place=self.hives_place, number=1, type='TestType', comment='TestComment',
                                         active=True)
        self.mother = Mothers.objects.create(hive=self.hive, mark='TestMother', year=2022, male_line='TestMaleLine',
                                             female_line='TestFemaleLine', comment='TestComment', active=True)
        self.task = Tasks.objects.create(name='TestTask')
        self.visit = Visits.objects.create(hive=self.hive, date=timezone.now().date(), inspection_type='TestInspection',
                                           condition=5, hive_body_size=3, honey_supers_size=2, honey_yield=10.5,
                                           medication_application='TestMedication', disease='TestDisease', mite_drop=20,
                                           active=True, comment='TestComment')
        self.visit.performed_tasks.add(self.task)

    def test_login_form(self):
        form_data = {'username': 'testuser', 'password': 'testpassword'}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_register_form(self):
        form_data = {'username': 'newuser', 'email': 'newuser@example.com', 'password1': 'newpassword1234',
                     'password2': 'newpassword1234', 'beekeeper_id': 123456}
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_add_hives_place_form(self):
        form_data = {'name': 'NewPlace', 'type': 'NewType', 'location': 'NewLocation', 'comment': 'NewComment',
                     'beekeeper': self.user}
        form = AddHivesPlace(data=form_data)
        self.assertTrue(form.is_valid())

    def test_add_hive_form(self):
        form_data = {'type': 'NewType', 'comment': 'NewComment', 'place': self.hives_place}
        form = AddHive(data=form_data)
        self.assertTrue(form.is_valid())

    def test_add_mother_form(self):
        form_data = {'ancestor': self.mother, 'mark': 'NewMother', 'year': 2023, 'male_line': 'NewMaleLine',
                     'female_line': 'NewFemaleLine', 'comment': 'NewComment'}
        form = AddMother(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_add_visit_form(self):
        form_data = {'date': timezone.now().date(), 'inspection_type': 'NewInspection', 'condition': 4,
                     'hive_body_size': 2, 'honey_supers_size': 1, 'honey_yield': 5.5,
                     'medication_application': 'NewMedication', 'disease': 'NewDisease', 'mite_drop': 15,
                     'performed_tasks': [self.task]}
        form = AddVisit(data=form_data)
        self.assertTrue(form.is_valid())

    def test_edit_visit_form(self):
        form_data = {'date': timezone.now().date(), 'inspection_type': 'EditInspection', 'condition': 3,
                     'hive_body_size': 1, 'honey_supers_size': 3, 'honey_yield': 7.5,
                     'medication_application': 'EditMedication', 'disease': 'EditDisease', 'mite_drop': 10,
                     'comment': 'EditComment', 'performed_tasks': [self.task]}
        form = EditVisit(data=form_data)
        self.assertTrue(form.is_valid())

    def test_edit_hives_place_form(self):
        form_data = {'name': 'EditPlace', 'type': 'EditType', 'location': 'EditLocation', 'comment': 'EditComment',
                     'beekeeper': self.user}
        form = EditHivesPlace(data=form_data)
        self.assertTrue(form.is_valid())


    def tearDown(self):
        # Úklid testovacích dat
        self.user.delete()
        self.hives_place.delete()
        self.hive.delete()
        self.mother.delete()
        self.task.delete()
        self.visit.delete()

