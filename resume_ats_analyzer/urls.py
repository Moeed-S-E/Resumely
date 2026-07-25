from django.urls import path
from . import views

app_name = "resume_ats_analyzer"
urlpatterns = [
    path("", views.upload_view, name="upload"),
    path("result/<uuid:pk>/", views.result_view, name="result"),
    path("result/<uuid:pk>/pdf/", views.download_report_pdf, name="download_report"),
    path("build/", views.builder_view, name="builder"),
    path("build/result/<uuid:pk>/", views.builder_result_view, name="builder_result"),
    path("build/result/<uuid:pk>/pdf/", views.download_builder_pdf, name="download_builder"),
]
