from multiprocessing import context
import random

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.utils.dateparse import parse_date, parse_time

from .models import (
    Administrateur,
    Ecole,
    Groupe,
    Etudiant,
    Entreprise,
    EquipeStage,
    Evenement,
)


def index(request):
    return render(request, "webterminal/home.html")


def _generate_verification_code():
    return f"{random.randint(0, 999999):06d}"


def _send_verification_email(to_email, name, code):
    subject = "Code de verification"
    message = (
        f"Bonjour {name},\n\n"
        f"Votre code de verification est : {code}\n\n"
        f"Entrez ce code sur la page de verification pour activer votre compte.\n\n"
        f"Si vous n'êtes pas à l'origine de cette demande, ignorez cet email."
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "houssamsalek0707@gmail.com"),
        recipient_list=[to_email],
        fail_silently=False,
    )


def _find_user_by_session(role, uid):
    if role == "admin":
        return Administrateur.objects.filter(id=uid).first()
    if role == "etudiant":
        return Etudiant.objects.filter(id=uid).first()
    if role == "entreprise":
        return Entreprise.objects.filter(id=uid).first()
    return None


@require_GET
def login_view(request):
    return render(request, "webterminal/login.html", {"error": None})


@require_POST
def login_submit(request):
    email = request.POST.get("email", "").strip()
    password = request.POST.get("password", "")

    admin = Administrateur.objects.filter(email=email, password=password).first()
    if admin:
        request.session["user"] = {"role": "admin", "id": admin.id}
        return redirect("webterminal:dashboard")

    student = Etudiant.objects.filter(email=email, password=password).first()
    if student:
        if not student.email_verified:
            return render(request, "webterminal/login.html", {"error": "Email non vérifié. Contactez l'administrateur."})
        request.session["user"] = {"role": "etudiant", "id": student.id}
        return redirect("webterminal:dashboard")
    ecole = Ecole.objects.filter(email=email, password=password).first()
    if ecole:
        if not ecole.email_verified:
            return render(request, "webterminal/login.html", {"error": "Email non vérifié. Contactez l'administrateur."})
        request.session["user"] = {"role": "ecole", "id": ecole.id}
        return redirect("webterminal:dashboard")
    company = Entreprise.objects.filter(email=email, password=password).first()
    if company:
        if not company.email_verified:
            return render(request, "webterminal/login.html", {"error": "Email non vérifié. Contactez l'administrateur."})
        request.session["user"] = {"role": "entreprise", "id": company.id}
        return redirect("webterminal:dashboard")

    return render(request, "webterminal/login.html", {"error": "Email ou mot de passe incorrect."})


@require_GET
def register_view(request):
    return render(
        request,
        "webterminal/register.html",
        {
            "error": None,
            "ecoles": Ecole.objects.all().order_by("nom"),
            "groupes": Groupe.objects.select_related("ecole").all().order_by("ecole__nom", "nom"),
        },
    )


@require_POST
def register_submit(request):
    role = request.POST.get("role")
    nom = request.POST.get("nom", "").strip()
    email = request.POST.get("email", "").strip()
    password = request.POST.get("password", "")
    confirm = request.POST.get("confirm", "")
    ville = request.POST.get("ville", "").strip()

    if not nom or not email or not password or not confirm:
        return render(request, "webterminal/register.html", {"error": "Tous les champs sont obligatoires."})
    if password != confirm:
        return render(request, "webterminal/register.html", {"error": "Les mots de passe ne correspondent pas."})

    if (
        Administrateur.objects.filter(email=email).exists()
        or Etudiant.objects.filter(email=email).exists()
        or Entreprise.objects.filter(email=email).exists()
        or Ecole.objects.filter(nom=email).exists()
    ):
        return render(request, "webterminal/register.html", {"error": "Cet email est déjà utilisé."})

    code = _generate_verification_code()

    request.session["pending_verification"] = {
        "email": email.lower(),
        "code": code,
        "role": role,
    }

    if role == "etudiant":
        ecole_id = request.POST.get("ecole")
        groupe_id = request.POST.get("groupe")

        if not ecole_id:
            return render(request, "webterminal/register.html", {"error": "Veuillez choisir une école."})

        ecole = get_object_or_404(Ecole, id=ecole_id)

        groupe = None
        if groupe_id:
            groupe = get_object_or_404(Groupe, id=groupe_id, ecole=ecole)

        Etudiant.objects.create(
            nom=nom,
            email=email,
            password=password,
            ecole=ecole,
            groupe=groupe,
            email_verified=False,
            verification_code=code,
        )

        try:
            _send_verification_email(email, nom, code)
            request.session["verification_notice"] = "Un code a été envoyé à votre adresse email."
        except Exception:
            request.session["verification_notice"] = "Impossible d'envoyer l'email automatiquement. Le code a quand même été généré."

        return redirect("webterminal:verify_email")
    if role == "ecole":
        Ecole.objects.create(
            nom=nom,
            ville=ville,
            email=email,
            password=password,
            verified=False,
            email_verified=False,
            verification_code=code,
        )
        return redirect("webterminal:login")
    if role == "entreprise":
        secteur = request.POST.get("secteur", "").strip()

        Entreprise.objects.create(
            nom=nom,
            email=email,
            password=password,
            secteur=secteur,
            verified=False,
            email_verified=False,
            verification_code=code,
        )

        try:
            _send_verification_email(email, nom, code)
            request.session["verification_notice"] = "Un code a été envoyé à votre adresse email."
        except Exception:
            request.session["verification_notice"] = "Impossible d'envoyer l'email automatiquement. Le code a quand même été généré."

        return redirect("webterminal:verify_email")

    return render(request, "webterminal/register.html", {"error": "Rôle invalide."})


@require_GET
def verify_email_view(request):
    pending = request.session.get("pending_verification")
    if not pending:
        return redirect("webterminal:register")

    notice = request.session.pop("verification_notice", None)
    return render(
        request,
        "webterminal/verify_email.html",
        {"error": None, "email": pending.get("email"), "notice": notice},
    )


@require_POST
def verify_email_submit(request):
    pending = request.session.get("pending_verification")
    if not pending:
        return redirect("webterminal:register")

    code = request.POST.get("code", "").strip()
    if code != pending.get("code"):
        return render(
            request,
            "webterminal/verify_email.html",
            {"error": "Code invalide.", "email": pending.get("email")},
        )

    email = pending.get("email", "")
    role = pending.get("role")

    user = None
    if role == "etudiant":
        user = Etudiant.objects.filter(email=email).first()
    elif role == "entreprise":
        user = Entreprise.objects.filter(email=email).first()

    if not user:
        return render(
            request,
            "webterminal/verify_email.html",
            {"error": "Compte introuvable.", "email": email},
        )

    user.email_verified = True
    user.verification_code = None
    user.save()

    request.session.pop("pending_verification", None)
    return redirect("webterminal:login")


@require_GET
def dashboard(request):
    user = request.session.get("user")
    if not user:
        return redirect("webterminal:login")

    role = user.get("role")
    uid = user.get("id")
    info = _find_user_by_session(role, uid)

    context = {
        "role": role,
        "info": info,
    }

    if role == "ecole":
        context["entreprises_attente"] = Entreprise.objects.filter(verified=False).order_by("nom")
        context["stats"] = {
            "etudiants": Etudiant.objects.count(),
            "entreprises": Entreprise.objects.count(),
            "evenements": Evenement.objects.count(),
            "ecoles": Ecole.objects.count(),
            "groupes": Groupe.objects.count(),
            "equipes": EquipeStage.objects.count(),
        }
        all_events = Evenement.objects.all().order_by("date", "heure")
        context["events"] = all_events[:3]
        context["events_count"] = all_events.count()

    elif role == "etudiant":
        if not info:
            return redirect("webterminal:logout")

        events_qs = Evenement.objects.filter(
            Q(createur_role="etudiant", createur_id=info.id)
            | Q(etudiants=info)
            | Q(groupes=info.groupe)
            | Q(ecoles=info.ecole)
        ).distinct().order_by("date", "heure")

        membres_groupe = []
        if info.groupe:
            membres_groupe = Etudiant.objects.filter(groupe=info.groupe).exclude(id=info.id).order_by("nom")

        context["events"] = events_qs[:3]
        context["events_count"] = events_qs.count()
        context["groupe_membres"] = membres_groupe
        context["equipes_stage"] = info.equipes_stage.select_related("entreprise").all()

    elif role == "entreprise":
        if not info:
            return redirect("webterminal:logout")

        events_qs = Evenement.objects.filter(
            Q(createur_role="entreprise", createur_id=info.id)
            | Q(entreprises=info)
            | Q(equipes_stage__entreprise=info)
        ).distinct().order_by("date", "heure")

        context["events"] = events_qs[:3]
        context["events_count"] = events_qs.count()
        context["equipes_stage"] = EquipeStage.objects.filter(entreprise=info).prefetch_related("etudiants").order_by("nom")

    return render(request, "webterminal/dashboard.html", context)


@require_POST
def verify_entreprise(request):
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        return HttpResponseBadRequest("Non autorisé")

    ent_id = request.POST.get("entreprise_id")
    if not ent_id:
        return HttpResponseBadRequest("Entreprise manquante")

    entreprise = get_object_or_404(Entreprise, id=ent_id)
    entreprise.verified = True
    entreprise.save()

    return redirect("webterminal:dashboard")


from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404
from django.utils.dateparse import parse_date, parse_time
from django.views.decorators.http import require_POST

from .models import (
    Etudiant,
    Entreprise,
    Ecole,
    Groupe,
    EquipeStage,
    Evenement,
)


@require_POST
def create_event(request):
    user = request.session.get("user")

    if not user or user.get("role") not in ["etudiant", "entreprise", "ecole"]:
        return HttpResponseBadRequest("Non autorisé")

    titre = request.POST.get("titre", "").strip()
    ev_type = request.POST.get("type", "autre")
    date_raw = request.POST.get("date", "").strip()
    heure_raw = request.POST.get("heure", "").strip()
    lieu = request.POST.get("lieu", "").strip()
    description = request.POST.get("description", "").strip()

    if not titre:
        return HttpResponseBadRequest("Titre obligatoire")

    date_ev = parse_date(date_raw)
    heure_ev = parse_time(heure_raw)

    if not date_ev or not heure_ev:
        return HttpResponseBadRequest("Date ou heure invalide")

    creator_role = user["role"]
    creator_id = user["id"]

    event = Evenement.objects.create(
        titre=titre,
        type=ev_type,
        date=date_ev,
        heure=heure_ev,
        lieu=lieu,
        description=description,
        createur_role=creator_role,
        createur_id=creator_id,
        statut="planifie",
    )

    if creator_role == "etudiant":
        student = get_object_or_404(Etudiant, id=creator_id)
        event.etudiants.add(student)

    elif creator_role == "entreprise":
        company = get_object_or_404(Entreprise, id=creator_id)
        event.entreprises.add(company)

        equipe_ids = request.POST.getlist("equipes_stage")
        if equipe_ids:
            event.equipes_stage.set(
                EquipeStage.objects.filter(
                    id__in=equipe_ids,
                    entreprise=company
                )
            )

    elif creator_role == "ecole":
        school = get_object_or_404(Ecole, id=creator_id)
        event.ecoles.add(school)

        ecole_ids = request.POST.getlist("ecoles")
        groupe_ids = request.POST.getlist("groupes")
        etudiant_ids = request.POST.getlist("etudiants")
        entreprise_ids = request.POST.getlist("entreprises")
        equipe_ids = request.POST.getlist("equipes_stage")

        if ecole_ids:
            event.ecoles.add(*Ecole.objects.filter(id__in=ecole_ids))

        if groupe_ids:
            event.groupes.add(*Groupe.objects.filter(id__in=groupe_ids))

        if etudiant_ids:
            event.etudiants.add(*Etudiant.objects.filter(id__in=etudiant_ids))

        if entreprise_ids:
            event.entreprises.add(*Entreprise.objects.filter(id__in=entreprise_ids))

        if equipe_ids:
            event.equipes_stage.add(*EquipeStage.objects.filter(id__in=equipe_ids))

    return redirect("webterminal:dashboard")
@require_GET
def edit_event(request, event_id):
    user = request.session.get("user")
    if not user:
        return HttpResponseBadRequest("Non autorisé")

    event = get_object_or_404(Evenement, id=event_id)

    if user.get("role") != "admin":
        if event.createur_role != user.get("role") or event.createur_id != user.get("id"):
            return HttpResponseBadRequest("Non autorisé")

    return render(request, "webterminal/edit_event.html", {"event": event})


@require_POST
def update_event(request, event_id):
    user = request.session.get("user")
    if not user:
        return HttpResponseBadRequest("Non autorisé")

    event = get_object_or_404(Evenement, id=event_id)

    if user.get("role") != "admin":
        if event.createur_role != user.get("role") or event.createur_id != user.get("id"):
            return HttpResponseBadRequest("Non autorisé")

    titre = request.POST.get("titre", event.titre).strip()
    ev_type = request.POST.get("type", event.type)
    date_raw = request.POST.get("date", str(event.date))
    heure_raw = request.POST.get("heure", str(event.heure))
    lieu = request.POST.get("lieu", event.lieu).strip()
    desc = request.POST.get("description", event.description).strip()
    statut = request.POST.get("statut", event.statut)

    date_ev = parse_date(date_raw)
    heure_ev = parse_time(heure_raw)

    if not date_ev or not heure_ev:
        return HttpResponseBadRequest("Date ou heure invalide")

    event.titre = titre
    event.type = ev_type
    event.date = date_ev
    event.heure = heure_ev
    event.lieu = lieu
    event.description = desc
    event.statut = statut
    event.save()

    if user.get("role") == "admin":
        if request.POST.getlist("ecoles"):
            event.ecoles.set(Ecole.objects.filter(id__in=request.POST.getlist("ecoles")))
        if request.POST.getlist("groupes"):
            event.groupes.set(Groupe.objects.filter(id__in=request.POST.getlist("groupes")))
        if request.POST.getlist("etudiants"):
            event.etudiants.set(Etudiant.objects.filter(id__in=request.POST.getlist("etudiants")))
        if request.POST.getlist("entreprises"):
            event.entreprises.set(Entreprise.objects.filter(id__in=request.POST.getlist("entreprises")))
        if request.POST.getlist("equipes_stage"):
            event.equipes_stage.set(EquipeStage.objects.filter(id__in=request.POST.getlist("equipes_stage")))

    return redirect("webterminal:dashboard")
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET

from .models import Etudiant, Entreprise, Ecole, Evenement


@require_GET
def event(request):
    user = request.session.get("user")

    if not user:
        return redirect("webterminal:login")

    role = user["role"]
    user_id = user["id"]
    info = None

    if role == "etudiant":
        student = get_object_or_404(Etudiant, id=user_id)
        info = student

        filters = (
            Q(etudiants=student)
            | Q(ecoles=student.ecole)
            | Q(equipes_stage__etudiants=student)
        )

        if student.groupe:
            filters |= Q(groupes=student.groupe)

        events = (
            Evenement.objects.filter(filters)
            .distinct()
            .order_by("date", "heure")
        )

    elif role == "entreprise":
        company = get_object_or_404(Entreprise, id=user_id)
        info = company

        events = (
            Evenement.objects.filter(
                Q(entreprises=company)
                | Q(equipes_stage__entreprise=company)
            )
            .distinct()
            .order_by("date", "heure")
        )

    elif role == "ecole":
        school = get_object_or_404(Ecole, id=user_id)
        info = school

        events = (
            Evenement.objects.filter(
                Q(ecoles=school)
                | Q(groupes__ecole=school)
                | Q(etudiants__ecole=school)
                | Q(equipes_stage__etudiants__ecole=school)
            )
            .distinct()
            .order_by("date", "heure")
        )

    else:
        events = Evenement.objects.none()

    return render(
        request,
        "webterminal/events.html",
        {
            "events": events,
            "role": role,
            "info": info,
        },
    )
@require_GET
def logout_view(request):
    request.session.pop("user", None)
    request.session.pop("pending_verification", None)
    request.session.pop("verification_notice", None)
    return redirect("webterminal:index")