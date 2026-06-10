from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST ,require_GET
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
import random
from django.views.decorators.csrf import csrf_exempt
from .models import User , Student , School , Company ,Group,Team , Event , EventParticipant
from django.db.models import Q


def generate_code():
    return str(random.randint(100000, 999999))


def send_code_email(user ):
    code = generate_code()
    user.verification_code = code
    user.save(update_fields=["verification_code"])

    subject = "Code de verification"
    message = (
        f"Bonjour {user.first_name},\n\n"
        f"Votre code de verification est : {code}\n\n"
        f"Entrez ce code sur la page de verification pour activer votre compte.\n\n"
        f"Si vous n'êtes pas à l'origine de cette demande, ignorez cet email."
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
        recipient_list=[user.email],
        fail_silently=False,
    )

@csrf_exempt
@require_POST
def registration(request):
    role = request.POST.get("role", "").strip()
    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    confirm_password = request.POST.get("confirm_password", "")
    group_id = request.POST.get("group_id", "").strip()
    team_id = request.POST.get("team_id", "").strip()
    school_name = request.POST.get("school_name", "").strip()
    company_name = request.POST.get("company_name", "").strip()

    
    if not first_name or not last_name or not email or not password or not confirm_password or not role or (role == "student" and (not group_id)):
        return JsonResponse({"error": "All fields are required"}, status=400)

    if role not in ["student", "school", "company"]:
        return JsonResponse({"error": "Invalid role"}, status=400)

    if password != confirm_password:
        return JsonResponse({"error": "Passwords do not match"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already exists"}, status=400)
    if Company.objects.filter(name=company_name).exists():
        return JsonResponse({"error": "Company name already exists"}, status=400)
    if School.objects.filter(name=school_name).exists():
        return JsonResponse({"error": "School name already exists"}, status=400)
    group_obj = None
    team_obj = None

    if role == "student":
        group_obj = get_object_or_404(
            Group,
            id=group_id
        )

        if team_id and team_id != "null":
            team_obj = get_object_or_404(
                Team,
                id=team_id
            )
    user = User.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=make_password(password),
        role=role,
        is_verified=False,
        is_active=False,
    )
    if role == "student":
        Student.objects.create(
            user=user,
            group=group_obj,
            team=team_obj
        )
    elif role == "school":
        School.objects.create(
            user=user,
            name=school_name
        )
    elif role == "company":
        Company.objects.create(
            user=user,
            name=company_name
        )

    send_code_email(user)

    return JsonResponse({"message": "User registered successfully"}, status=201)

@csrf_exempt
@require_POST
def verify_user(request):
    email = request.POST.get("email", "").strip().lower()
    code = request.POST.get("code", "").strip()

    user = get_object_or_404(User, email=email)

    if user.verification_code != code:
        return JsonResponse({"error": "Invalid verification code"}, status=400)

    user.is_verified = True
    user.is_active = True
    user.verification_code = None
    user.save(update_fields=["is_verified", "is_active", "verification_code"])

    return JsonResponse({"message": "User verified successfully"}, status=200)

@csrf_exempt
@require_POST
def login(request):
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")

    user = User.objects.filter(email=email).first()
    if not user:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    if not user.is_verified:
        return JsonResponse({"error": "Account not verified"}, status=403)

    if not check_password(password, user.password):
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    request.session["user"] = {
        "id": user.id,
        "role": user.role,
    }

    return JsonResponse({"message": "Logged in successfully"}, status=200)

@csrf_exempt
@require_POST
def logout(request):
    request.session.flush()
    return JsonResponse({"message": "Logged out successfully"}, status=200)

@csrf_exempt
@require_POST
def reset_password(request):
    email = request.POST.get("email", "").strip().lower()

    user = get_object_or_404(User, email=email)
    send_code_email(user)

    return JsonResponse({"message": "Password reset code sent successfully"}, status=200)

@csrf_exempt
@require_POST
def update_password(request):

    email = request.POST.get("email", "").strip().lower()
    code = request.POST.get("code", "").strip()

    new_password = request.POST.get("new_password", "")
    confirm_password = request.POST.get("confirm_password", "")

    user = get_object_or_404(User, email=email)

    if not new_password:
        return JsonResponse(
            {"error": "Password is required"},
            status=400
        )

    if new_password != confirm_password:
        return JsonResponse(
            {"error": "Passwords do not match"},
            status=400
        )

    if not code or user.verification_code != code:
        return JsonResponse(
            {"error": "Invalid verification code"},
            status=400
        )

    user.password = make_password(new_password)
    user.verification_code = None

    user.save(
        update_fields=[
            "password",
            "verification_code"
        ]
    )

    return JsonResponse(
        {"message": "Password updated successfully"},
        status=200
    )
@csrf_exempt
@require_GET
def get_user(request):
    session_user = request.session.get("user")

    if not session_user:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    user = get_object_or_404(User, id=session_user["id"])

    if not user.is_verified:
        return JsonResponse({"error": "Account not verified"}, status=403)

    if user.role == "student":
        student = get_object_or_404(Student, user=user)

        events = Event.objects.filter(
            Q(target_group=student.group) |
            Q(target_team=student.team)
        ).distinct()

        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "group": {
                "id": student.group.id,
                "name": student.group.name,
            } if student.group else None,
            "team": {
                "id": student.team.id,
                "name": student.team.name,
            } if student.team else None,
            "school": {
                "id": student.group.school.id,
                "name": student.group.school.name,
            } if student.group else None,
            "company": {
                "id": student.team.company.id,
                "name": student.team.company.name,
            } if student.team else None,
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                }
                for event in events
            ],
        }

    elif user.role == "school":
        school = get_object_or_404(School, user=user)

        groups = Group.objects.filter(school=school)
        students = Student.objects.filter(group__in=groups).distinct()
        events = Event.objects.filter(target_group__in=groups).distinct()

        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "groups": [
                {
                    "id": group.id,
                    "name": group.name,
                }
                for group in groups
            ],
            "students": [
                {
                    "id": student.id,
                    "name": str(student),
                }
                for student in students
            ],
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                }
                for event in events
            ],
        }

    elif user.role == "company":
        company = get_object_or_404(Company, user=user)

        teams = Team.objects.filter(company=company)
        students = Student.objects.filter(team__in=teams).distinct()
        events = Event.objects.filter(target_team__in=teams).distinct()

        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "teams": [
                {
                    "id": team.id,
                    "name": team.name,
                }
                for team in teams
            ],
            "students": [
                {
                    "id": student.id,
                    "name": str(student),
                }
                for student in students
            ],
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                }
                for event in events
            ],
        }

    else:
        return JsonResponse({"error": "Invalid role"}, status=400)

    return JsonResponse(user_data)