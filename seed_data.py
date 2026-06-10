import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.hashers import make_password
from app.models import User, Student, School, Company, Group, Team

PWD = make_password("password123")


def make_user(email, first, last, role):
    user, created = User.objects.get_or_create(
        email=email,
        defaults=dict(
            first_name=first, last_name=last, role=role,
            password=PWD, is_verified=True, is_active=True,
        ),
    )
    if not created:
        user.first_name, user.last_name, user.role = first, last, role
        user.password = PWD
        user.is_verified = True
        user.is_active = True
        user.verification_code = None
        user.save()
    return user


school_user = make_user("school@test.com", "Sara", "School", "school")
school, _ = School.objects.get_or_create(user=school_user, defaults={"name": "EMSI"})
group, _ = Group.objects.get_or_create(school=school, name="Group 4", defaults={"year": 3})

company_user = make_user("company@test.com", "Karim", "Company", "company")
company, _ = Company.objects.get_or_create(user=company_user, defaults={"name": "Capgemini"})
team, _ = Team.objects.get_or_create(company=company, name="Backend Team")

student_user = make_user("student@test.com", "Sami", "Student", "student")
Student.objects.get_or_create(user=student_user, defaults={"group": group, "team": team})

print("=" * 48)
print("Seed complete. Password for ALL accounts: password123")
print("-" * 48)
print("School  -> school@test.com")
print("Company -> company@test.com")
print("Student -> student@test.com")
print("=" * 48)
