from django.db import models
import random


class User(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("school", "School"),
        ("company", "Company"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    
    password = models.CharField(max_length=255)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_verification_code(self):
        self.verification_code = str(random.randint(100000, 999999))
        self.save(update_fields=["verification_code"])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)


class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class School(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Team(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="teams"
    )
    name = models.CharField(max_length=100)

    students = models.ManyToManyField(
        Student,
        blank=True,
        related_name="teams"
    )

    def __str__(self):
        return self.name


class Group(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="groups"
    )
    name = models.CharField(max_length=100)
    year = models.IntegerField()

    students = models.ManyToManyField(
        Student,
        blank=True,
        related_name="groups"
    )

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    start_date = models.DateTimeField()

    end_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    target_group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    target_team = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title


class EventParticipant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("event", "participant")

    def __str__(self):
        return f"{self.event} - {self.participant}"