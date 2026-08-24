from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Application, College, Task, UserProfile
from .views import filter_colleges_by_preferences, filter_colleges_fuzzy


class CollegeSearchTests(TestCase):
    def setUp(self):
        self.public_ca = College.objects.create(
            name="State U",
            location="Los Angeles, CA",
            state="California",
            institution_type="public",
            campus_setting="urban",
            climate="warm",
            campus_size="large",
            meal_options="vegetarian, halal",
            extracurriculars="debate, music",
            housing_summary="dorms and apartments",
            financial_aid_available=True,
            application_deadline=date.today() + timedelta(days=60),
        )
        self.private_ny = College.objects.create(
            name="Private College",
            location="New York, NY",
            state="New York",
            institution_type="private",
            campus_setting="urban",
            climate="cold",
            campus_size="small",
            meal_options="kosher",
            extracurriculars="theater",
            housing_summary="commuter-friendly",
            financial_aid_available=False,
            application_deadline=date.today() + timedelta(days=90),
        )

    def test_fuzzy_requires_all_tokens(self):
        qs = filter_colleges_fuzzy(College.objects.all(), "california warm")
        self.assertEqual(list(qs), [self.public_ca])

    def test_preferences_filter_state_and_type(self):
        user = User.objects.create_user("alice", password="pass12345")
        profile = user.profile
        profile.college_type_preferences = "public"
        profile.preferred_state = "California"
        profile.save()
        qs = filter_colleges_by_preferences(College.objects.all(), profile)
        self.assertEqual(list(qs), [self.public_ca])


class ApplicationFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("bob", password="pass12345")
        self.college = College.objects.create(
            name="Test College",
            location="Boston, MA",
            state="Massachusetts",
            application_deadline=date.today() + timedelta(days=45),
        )

    def test_add_college_and_create_task(self):
        self.client.login(username="bob", password="pass12345")
        response = self.client.post(
            reverse("apply_college"),
            {"college_id": self.college.id, "next": "/colleges"},
        )
        self.assertEqual(response.status_code, 302)
        app = Application.objects.get(user=self.user, college=self.college)

        response = self.client.post(
            reverse("create_task", args=[app.id]),
            {"title": "Write essay", "due_date": str(date.today() + timedelta(days=7))},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.filter(application=app).count(), 1)

        task = Task.objects.get(application=app)
        response = self.client.put(
            reverse("toggle_task", args=[task.id]),
            data='{"completed": true}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertTrue(task.completed)

    def test_match_prefs_query_param(self):
        profile = self.user.profile
        profile.preferred_state = "Massachusetts"
        profile.save()
        self.client.login(username="bob", password="pass12345")
        response = self.client.get(reverse("all_colleges"), {"match_prefs": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test College")
        self.assertTrue(response.context["match_prefs"])


class ProfileSignalTests(TestCase):
    def test_profile_created_with_user(self):
        user = User.objects.create_user("carol", password="pass12345")
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
