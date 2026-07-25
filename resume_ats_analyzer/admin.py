from django.contrib import admin
from .models import ResumeAnalysis

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "status", "match_score", "created_at")
    readonly_fields = ("resume_text_extracted", "report_markdown", "status", "match_score", "error_message")
