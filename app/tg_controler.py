from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from .models import (
    User,
    Group,
    Team,
    Company,
    School,
    Student
)

@csrf_exempt
@require_POST
def create_team(request):

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

    if user.role != "company":
        return JsonResponse(
            {"error": "Only companies can create teams"},
            status=403
        )

    name = request.POST.get("name", "").strip()

    if not name:
        return JsonResponse(
            {"error": "Name is required"},
            status=400
        )

    company = get_object_or_404(
        Company,
        user=user
    )

    if Team.objects.filter(
        company=company,
        name=name
    ).exists():
        return JsonResponse(
            {"error": "Team already exists"},
            status=400
        )

    team = Team.objects.create(
        name=name,
        company=company
    )

    return JsonResponse(
        {
            "message": "Team created successfully",
            "team_id": team.id
        },
        status=201
    )

@csrf_exempt
@require_POST
def create_group(request):

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

    if user.role != "school":
        return JsonResponse(
            {"error": "Only schools can create groups"},
            status=403
        )

    name = request.POST.get("name", "").strip()
    year = request.POST.get("year", "").strip()

    if not name or not year:
        return JsonResponse(
            {"error": "Name and year are required"},
            status=400
        )

    school = get_object_or_404(
        School,
        user=user
    )

    if Group.objects.filter(
        school=school,
        name=name
    ).exists():
        return JsonResponse(
            {"error": "Group already exists"},
            status=400
        )

    group = Group.objects.create(
        name=name,
        school=school,
        year=year
    )

    return JsonResponse(
        {
            "message": "Group created successfully",
            "group_id": group.id
        },
        status=201
    )


@csrf_exempt
@require_GET
def get_groups(request):

    groups = Group.objects.all()

    group_list = []

    for group in groups:

        students = Student.objects.filter(
            group=group
        )

        group_list.append(
            {
                "id": group.id,
                "name": group.name,
                "year": group.year,
                "school": {
                    "id": group.school.id,
                    "name": group.school.name
                },
                "students": [
                    {
                        "id": student.id,
                        "name": f"{student.user.first_name} {student.user.last_name}"
                    }
                    for student in students
                ]
            }
        )

    return JsonResponse(
        {"groups": group_list},
        status=200
    )

@csrf_exempt
@require_GET
def get_teams(request):

    teams = Team.objects.all()

    team_list = []

    for team in teams:

        students = Student.objects.filter(
            team=team
        )

        team_list.append(
            {
                "id": team.id,
                "name": team.name,
                "company": {
                    "id": team.company.id,
                    "name": team.company.name
                },
                "students": [
                    {
                        "id": student.id,
                        "name": f"{student.user.first_name} {student.user.last_name}"
                    }
                    for student in students
                ]
            }
        )

    return JsonResponse(
        {"teams": team_list},
        status=200
    )