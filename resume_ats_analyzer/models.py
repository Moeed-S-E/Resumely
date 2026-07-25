from django.db import models
from django.conf import settings
import uuid

class ResumeAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("complete", "Complete"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField()
    job_description = models.TextField()
    resume_text_extracted = models.TextField(blank=True)
    report_markdown = models.TextField(blank=True)
    match_score = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ResumeBuilder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    base_analysis = models.ForeignKey(ResumeAnalysis, null=True, blank=True, on_delete=models.SET_NULL)
    job_description = models.TextField()
    generated_resume_markdown = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
