from django.contrib.auth.models import User
from django.db import models


class College(models.Model):
    """Catalogue row; preference-aligned fields power fuzzy search on the browse page."""

    INSTITUTION_TYPE_CHOICES = [
        ('', 'Unspecified'),
        ('public', 'Public'),
        ('private', 'Private'),
        ('ivy_league', 'Ivy League'),
        ('liberal_arts', 'Liberal Arts'),
        ('community_college', 'Community College'),
        ('hbcu', 'HBCU'),
        ('other', 'Other'),
    ]
    SETTING_CHOICES = [('', 'Any'), ('urban', 'Urban'), ('suburban', 'Suburban'), ('rural', 'Rural')]
    CLIMATE_CHOICES = [
        ('', 'No preference'),
        ('warm', 'Warm'),
        ('cold', 'Cold'),
        ('temperate', 'Temperate'),
        ('tropical', 'Tropical'),
    ]
    SIZE_CHOICES = [
        ('', 'Any'),
        ('small', 'Small (<5,000)'),
        ('medium', 'Medium (5,000–15,000)'),
        ('large', 'Large (>15,000)'),
    ]
    SPORTS_PROGRAM_CHOICES = [
        ('', 'No preference'),
        ('d1', 'Division I'),
        ('d2', 'Division II'),
        ('d3', 'Division III'),
        ('naia', 'NAIA'),
        ('intramural', 'Intramural only'),
    ]

    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    application_deadline = models.DateField()
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    institution_type = models.CharField(
        max_length=20, choices=INSTITUTION_TYPE_CHOICES, blank=True, default='',
    )
    state = models.CharField(
        max_length=100, blank=True, default='',
        help_text='State or region (searchable alongside location).',
    )
    campus_setting = models.CharField(
        max_length=15, choices=SETTING_CHOICES, blank=True, default='',
    )
    climate = models.CharField(
        max_length=15, choices=CLIMATE_CHOICES, blank=True, default='',
    )
    campus_size = models.CharField(
        max_length=10, choices=SIZE_CHOICES, blank=True, default='',
    )
    meal_options = models.CharField(
        max_length=300, blank=True, default='',
        help_text='Dining/diet options offered (e.g. vegetarian, halal, kosher).',
    )
    extracurriculars = models.CharField(
        max_length=500, blank=True, default='',
        help_text='Comma-separated highlights (sports, music, Greek life, …).',
    )
    housing_summary = models.CharField(
        max_length=200, blank=True, default='',
        help_text='Housing options (dorms, apartments, commuter-friendly, …).',
    )
    sports_program = models.CharField(
        max_length=15, choices=SPORTS_PROGRAM_CHOICES, blank=True, default='',
    )
    financial_aid_available = models.BooleanField(
        default=True,
        help_text='Uncheck if the profile should not match financial-aid-related searches.',
    )
    search_notes = models.TextField(
        blank=True, default='',
        help_text='Extra searchable text: nicknames, programs, anything students might type.',
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['application_deadline']


class Application(models.Model):
    STATUS_CHOICES = [
        ('researching', 'Researching'),
        ('applying', 'Applying'),
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('deferred', 'Deferred'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='researching')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.college.name}"

    class Meta:
        unique_together = ['user', 'college']


class Task(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['due_date', 'created_at']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    COLLEGE_TYPE_CHOICES = [
        ('', '-- Select --'),
        ('public', 'Public'),
        ('private', 'Private'),
        ('ivy_league', 'Ivy League'),
        ('liberal_arts', 'Liberal Arts'),
        ('community_college', 'Community College'),
        ('hbcu', 'HBCU'),
        ('other', 'Other'),
    ]
    college_type_preferences = models.CharField(
        max_length=20, choices=COLLEGE_TYPE_CHOICES, default='', blank=True,
    )

    MEAL_PLAN_CHOICES = [
        ('no_preference', 'No Preference'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('non_veg', 'Non-Vegetarian'),
        ('halal', 'Halal'),
        ('kosher', 'Kosher'),
    ]
    meal_plan_preference = models.CharField(
        max_length=15, choices=MEAL_PLAN_CHOICES, default='no_preference',
    )

    preferred_state = models.CharField(
        max_length=100, blank=True, default='',
        help_text='Preferred state (e.g., California)',
    )
    SETTING_CHOICES = [('', 'Any'), ('urban', 'Urban'), ('suburban', 'Suburban'), ('rural', 'Rural')]
    preferred_setting = models.CharField(
        max_length=15, choices=SETTING_CHOICES, default='', blank=True,
    )
    max_distance_from_home = models.PositiveIntegerField(
        default=0, blank=True, help_text='Miles from home (0 = no limit)',
    )
    CLIMATE_CHOICES = [
        ('', 'No preference'), ('warm', 'Warm'), ('cold', 'Cold'),
        ('temperate', 'Temperate'), ('tropical', 'Tropical'),
    ]
    preferred_climate = models.CharField(
        max_length=15, choices=CLIMATE_CHOICES, default='', blank=True,
    )

    SIZE_CHOICES = [
        ('', 'Any'), ('small', 'Small (<5,000)'),
        ('medium', 'Medium (5,000-15,000)'), ('large', 'Large (>15,000)'),
    ]
    preferred_campus_size = models.CharField(
        max_length=10, choices=SIZE_CHOICES, default='', blank=True,
    )

    EXTRACURRICULAR_CHOICES = [
        ('sports', 'Sports'), ('music', 'Music'), ('theater', 'Theater'),
        ('debate', 'Debate'), ('stem_club', 'STEM Club'),
        ('volunteering', 'Volunteering'), ('student_gov', 'Student Government'),
        ('arts', 'Visual Arts'), ('journalism', 'Journalism'),
        ('greek_life', 'Greek Life'),
    ]
    extracurriculars = models.CharField(
        max_length=300, blank=True, default='',
        help_text='Hold Ctrl/Cmd to select multiple.',
    )

    HOUSING_CHOICES = [
        ('', 'No preference'), ('dorm', 'Dormitory'),
        ('apartment', 'Off-campus Apartment'), ('commuter', 'Commuter'),
    ]
    preferred_housing = models.CharField(
        max_length=15, choices=HOUSING_CHOICES, default='', blank=True,
    )

    SPORTS_PROGRAM_CHOICES = [
        ('', 'No preference'), ('d1', 'Division I'), ('d2', 'Division II'),
        ('d3', 'Division III'), ('naia', 'NAIA'), ('intramural', 'Intramural Only'),
    ]
    sports_program_preference = models.CharField(
        max_length=15, choices=SPORTS_PROGRAM_CHOICES, default='', blank=True,
    )

    gpa_self_assessment = models.CharField(
        max_length=10, blank=True, default='',
        help_text='Approximate GPA on a 4.0 scale',
    )
    sat_act_score = models.PositiveIntegerField(
        default=0, blank=True, help_text='SAT/ACT score (0 = N/A)',
    )
    financial_aid_needed = models.BooleanField(
        default=False, help_text='Do you need financial aid?',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"
