import uuid
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import ResumeAnalysis, ResumeBuilder

class ResumeATSModelsTests(TestCase):
    def test_resume_analysis_creation(self):
        analysis = ResumeAnalysis.objects.create(
            email="test@example.com",
            job_description="Software Engineer role",
            resume_text_extracted="My Resume Text",
            report_markdown="## Report",
            match_score=85,
            status="complete"
        )
        self.assertEqual(analysis.email, "test@example.com")
        self.assertEqual(analysis.match_score, 85)
        self.assertEqual(analysis.status, "complete")
        self.assertIsInstance(analysis.id, uuid.UUID)

    def test_resume_builder_creation(self):
        analysis = ResumeAnalysis.objects.create(
            email="test@example.com",
            job_description="Software Engineer role",
        )
        builder = ResumeBuilder.objects.create(
            base_analysis=analysis,
            job_description="Software Engineer role",
            generated_resume_markdown="LaTeX content here"
        )
        self.assertEqual(builder.base_analysis, analysis)
        self.assertEqual(builder.job_description, "Software Engineer role")
        self.assertIsInstance(builder.id, uuid.UUID)


class ResumeATSE2ETests(TestCase):
    def setUp(self):
        self.client = Client()
        self.analysis = ResumeAnalysis.objects.create(
            email="test@example.com",
            job_description="Test Job Description",
            resume_text_extracted="Test Resume Content",
            report_markdown="## AI Report",
            match_score=90,
            status="complete"
        )
        self.builder = ResumeBuilder.objects.create(
            base_analysis=self.analysis,
            job_description="Test Job Description",
            generated_resume_markdown="\\begin{document} Test \\end{document}"
        )

    @patch('resume_ats_analyzer.views.send_report_email')
    @patch('resume_ats_analyzer.views.extract_resume_text')
    @patch('resume_ats_analyzer.views.analyze_with_ai')
    @patch('resume_ats_analyzer.views.parse_match_score')
    @patch('resume_ats_analyzer.views.extract_report_sections')
    def test_upload_and_analyze_e2e(self, mock_extract_sections, mock_parse, mock_analyze, mock_extract_text, mock_send_email):
        """E2E Test: Upload a resume, get analyzed, and see the report."""
        mock_extract_text.return_value = "Extracted Resume Text"
        mock_analyze.return_value = "## Test Report"
        mock_parse.return_value = 85
        mock_extract_sections.return_value = (["Strength"], ["Weakness"], ["Keyword"], ["Suggestion"])

        pdf_content = b"%PDF-1.4 test pdf content"
        test_file = SimpleUploadedFile("test_resume.pdf", pdf_content, content_type="application/pdf")

        # 1. Access Upload Page
        response = self.client.get(reverse("resume_ats_analyzer:upload"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload Resume")

        # 2. Submit Upload Form
        post_data = {
            "resume_file": test_file,
            "job_description": "We need a Python developer.",
            "email": "applicant@example.com"
        }
        response = self.client.post(reverse("resume_ats_analyzer:upload"), post_data)
        
        # Should redirect to result page
        self.assertEqual(response.status_code, 302)
        
        # Verify DB object was created
        analysis = ResumeAnalysis.objects.latest('created_at')
        self.assertEqual(analysis.email, "applicant@example.com")
        self.assertEqual(analysis.match_score, 85)

        # 3. Access Result Page
        result_url = reverse("resume_ats_analyzer:result", kwargs={"pk": analysis.id})
        response = self.client.get(result_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "85")

    @patch('resume_ats_analyzer.views.send_builder_email')
    @patch('resume_ats_analyzer.views.generate_ats_resume')
    def test_builder_flow_e2e(self, mock_generate, mock_send_email):
        """E2E Test: Use a previous analysis to build a new ATS resume."""
        mock_generate.return_value = "\\begin{document} Generated Resume \\end{document}"
        
        # 1. Access Builder Page with analysis_id
        build_url = reverse("resume_ats_analyzer:builder") + f"?analysis_id={self.analysis.id}"
        response = self.client.get(build_url)
        self.assertEqual(response.status_code, 200)
        
        # 2. Submit Builder Form
        post_data = {
            "job_description": "New targeted job description."
        }
        response = self.client.post(build_url, post_data)
        
        # Should redirect to builder result page
        self.assertEqual(response.status_code, 302)
        
        builder = ResumeBuilder.objects.latest('created_at')
        self.assertEqual(builder.job_description, "New targeted job description.")
        
        # 3. Access Builder Result Page
        result_url = reverse("resume_ats_analyzer:builder_result", kwargs={"pk": builder.id})
        response = self.client.get(result_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tailored specifically for the provided job description.")

    @patch('subprocess.run')
    def test_pdf_generation_endpoint(self, mock_subprocess):
        """E2E Test: Verify the PDF generation endpoint simulates correctly."""
        # Mock the subprocess so Tectonic doesn't actually run in tests
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # We also need to mock the reading of the generated PDF file since Tectonic didn't run
        with patch('builtins.open', unittest.mock.mock_open(read_data=b"%PDF-1.4 dummy pdf")):
            pdf_url = reverse("resume_ats_analyzer:download_builder", kwargs={"pk": self.builder.id})
            response = self.client.get(pdf_url)
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/pdf')
            self.assertEqual(response['Content-Disposition'], 'inline; filename="resume.pdf"')
