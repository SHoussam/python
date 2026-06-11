from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from .models import Student, User, Event, Team, Group, EventParticipant , Company , School


@require_POST
def create_event(request):
    session_user = request.session.get("user")

    if not session_user:
        return JsonResponse(
            {"error": "Not authenticated"},
            status=401
        )

    user = get_object_or_404(User, id=session_user["id"])

    title = request.POST.get("title", "").strip()
    description = request.POST.get("description", "").strip()
    start_date_raw = request.POST.get("start_date", "").strip()
    end_date_raw = request.POST.get("end_date", "").strip()

    if not title or not start_date_raw or not end_date_raw:
        return JsonResponse(
            {"error": "Title, start date and end date are required"},
            status=400
        )

    start_date = parse_datetime(start_date_raw)
    end_date = parse_datetime(end_date_raw)

    if not start_date or not end_date:
        return JsonResponse(
            {"error": "Invalid start_date or end_date format"},
            status=400
        )

    created_events = []

    if user.role == "student":
        event = Event.objects.create(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            creator=user,
            target_group=None,
            target_team=None
        )

        EventParticipant.objects.create(
            event=event,
            participant=user
        )

        created_events.append(event.id)

    elif user.role == "school":
        group_ids = request.POST.getlist("group_ids") or request.POST.getlist("group_ids[]")

        if not group_ids:
            return JsonResponse(
                {"error": "At least one group is required"},
                status=400
            )

        for group_id in group_ids:
            group = get_object_or_404(Group, id=group_id)

            event = Event.objects.create(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                creator=user,
                target_group=group,
                target_team=None
            )

            created_events.append(event.id)

    elif user.role == "company":
        team_ids = request.POST.getlist("team_ids") or request.POST.getlist("team_ids[]")

        if not team_ids:
            return JsonResponse(
                {"error": "At least one team is required"},
                status=400
            )

        for team_id in team_ids:
            team = get_object_or_404(Team, id=team_id)

            event = Event.objects.create(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                creator=user,
                target_group=None,
                target_team=team
            )

            created_events.append(event.id)

    else:
        return JsonResponse(
            {"error": "Invalid role"},
            status=400
        )

    return JsonResponse(
        {
            "message": "Event created successfully",
            "created_count": len(created_events),
            "event_ids": created_events
        },
        status=201
    )
@require_POST
def edit_event(request, event_id):

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

    event = get_object_or_404(
        Event,
        id=event_id
    )

    if event.creator != user:
        return JsonResponse(
            {"error": "You do not have permission to edit this event"},
            status=403
        )

    title = request.POST.get(
        "title",
        ""
    ).strip()

    description = request.POST.get(
        "description",
        ""
    ).strip()

    start_date_raw = request.POST.get(
        "start_date",
        ""
    ).strip()

    end_date_raw = request.POST.get(
        "end_date",
        ""
    ).strip()

    if title:
        event.title = title

    if description:
        event.description = description

    if start_date_raw:
        start_date = parse_datetime(
            start_date_raw
        )

        if not start_date:
            return JsonResponse(
                {"error": "Invalid start_date format"},
                status=400
            )

        event.start_date = start_date

    if end_date_raw:
        end_date = parse_datetime(
            end_date_raw
        )

        if not end_date:
            return JsonResponse(
                {"error": "Invalid end_date format"},
                status=400
            )

        event.end_date = end_date

    if event.end_date < event.start_date:
        return JsonResponse(
            {"error": "End date must be after start date"},
            status=400
        )

    event.save()

    return JsonResponse(
        {
            "message": "Event updated successfully",
            "event_id": event.id
        },
        status=200
    )

@require_POST
def remove_event(request, event_id):

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

    event = get_object_or_404(
        Event,
        id=event_id
    )

    if event.creator != user:
        return JsonResponse(
            {"error": "You do not have permission to delete this event"},
            status=403
        )

    event.delete()

    return JsonResponse(
        {
            "message": "Event deleted successfully"
        },
        status=200
    )
@require_GET
def list_events(request):

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

    if user.role == "student":

        student = get_object_or_404(
            Student,
            user=user
        )

        events = Event.objects.filter(
            Q(target_group=student.group) |
            Q(target_team=student.team) |
            Q(eventparticipant__participant=user)
        ).distinct()

    elif user.role == "school":

        school = get_object_or_404(
            School,
            user=user
        )

        events = Event.objects.filter(
            Q(target_group__school=school) |
            Q(creator=user)
        ).distinct()

    elif user.role == "company":

        company = get_object_or_404(
            Company,
            user=user
        )

        events = Event.objects.filter(
            Q(target_team__company=company) |
            Q(creator=user)
        ).distinct()

    else:
        return JsonResponse(
            {"error": "Invalid role"},
            status=400
        )

    events_data = [
        {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_date": event.start_date.isoformat(),
            "end_date": event.end_date.isoformat(),
            "creator_id": event.creator.id,
            "target_group_id": (
                event.target_group.id
                if event.target_group
                else None
            ),
            "target_team_id": (
                event.target_team.id
                if event.target_team
                else None
            ),
        }
        for event in events
    ]

    return JsonResponse(
        {"events": events_data},
        status=200
    )