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
    print("POST =", request.POST)
    role = request.POST.get("role", "").strip()
    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    confirm_password = request.POST.get("confirm_password", "")

    if not first_name or not last_name or not email or not password or not confirm_password or not role:
        return JsonResponse({"error": "All fields are required"}, status=400)

    if role not in ["student", "school", "company"]:
        return JsonResponse({"error": "Invalid role"}, status=400)

    if password != confirm_password:
        return JsonResponse({"error": "Passwords do not match"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already exists"}, status=400)

    user = User.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=make_password(password),
        role=role,
        is_verified=False,
        is_active=False,
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
        return JsonResponse(
            {"error": "Not authenticated"},
            status=401
        )

    user = get_object_or_404(
        User,
        id=session_user["id"]
    )

    if not user.is_verified:
        return JsonResponse(
            {"error": "Account not verified"},
            status=403
        )

    if user.role == "student":

        student = get_object_or_404(
            Student,
            user=user
        )

        group = Group.objects.filter(
            students=student
        ).first()

        team = Team.objects.filter(
            students=student
        ).first()

        events = Event.objects.filter(
            Q(target_group=group)
            | Q(target_team=team)
        ).distinct()

        school = group.school if group else None
        company = team.company if team else None

        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "is_verified": user.is_verified,
            "is_active": user.is_active,

            "school": {
                "id": school.id,
                "name": school.name,
            } if school else None,

            "company": {
                "id": company.id,
                "name": company.name,
            } if company else None,

            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                }
                for event in events
            ]
        }


    elif user.role == "school":

        school = get_object_or_404(
            School,
            user=user
        )

        groups = Group.objects.filter(
            school=school
        )

        events = Event.objects.filter(
            target_group__in=groups
        ).distinct()

        students = Student.objects.filter(
            groups__in=groups
        ).distinct()

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
            ]
        }



    elif user.role == "company":

        company = get_object_or_404(
            Company,
            user=user
        )

        teams = Team.objects.filter(
            company=company
        )

        events = Event.objects.filter(
            target_team__in=teams
        ).distinct()

        students = Student.objects.filter(
            teams__in=teams
        ).distinct()

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
            ]
        }

    else:
        return JsonResponse(
            {"error": "Invalid role"},
            status=400
        )

    return JsonResponse(user_data)