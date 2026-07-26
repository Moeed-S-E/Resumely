import re
import pdfplumber
import docx
from groq import Groq
import markdown
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from weasyprint import HTML
from django.template.loader import render_to_string
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import time

class ExtractionError(Exception):
    pass

class AIAnalysisError(Exception):
    pass

def extract_resume_text(file) -> str:
    try:
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        if not text.strip():
            raise ExtractionError("No text found in PDF.")
        return text
    except Exception as e:
        raise ExtractionError(f"Failed to extract text from PDF: {str(e)}")

def build_prompt(resume_text: str, job_description: str) -> str:
    return f"""
Act as an expert ATS (Applicant Tracking System) analyzer and recruiter.

Compare the following resume against the job description.

Job Description:
{job_description}

Resume:
{resume_text}

Provide a detailed analysis in Markdown format EXACTLY following this structure:

# Score
[Give a match score out of 100, e.g., 78]

# Strengths
* [Strength 1]
* [Strength 2]

# Weaknesses
* [Weakness 1]
* [Weakness 2]

# Missing Keywords
* [Keyword 1]
* [Keyword 2]

# Suggestions
* [Suggestion 1]
* [Suggestion 2]
"""

def analyze_with_ai(prompt: str) -> str:
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    # Retry logic
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert ATS (Applicant Tracking System) analyzer and recruiter."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            response_text = completion.choices[0].message.content
            if not response_text:
                raise ValueError("Empty response from AI")
            return response_text
        except Exception as e:
            if attempt == max_retries:
                raise AIAnalysisError(f"AI Analysis failed after retries: {str(e)}")
            time.sleep(2 ** attempt)

def parse_match_score(report_markdown: str) -> int:
    match = re.search(r'# Score\n.*?(\d+)', report_markdown, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # fallback
    match = re.search(r'Score.*?(\d+)', report_markdown, re.IGNORECASE)
    if match:
        return int(match.group(1))
        
    return 0

def extract_report_sections(report_markdown: str):
    def extract_section(regex, md):
        match = re.search(regex, md, re.IGNORECASE | re.DOTALL)
        if match:
            items = match.group(1).strip().split('\n')
            return [re.sub(r'^[\*\-]\s+', '', item).strip() for item in items if item.strip()]
        return []
    strengths = extract_section(r'# Strengths\n(.*?)(?=\n#|$)', report_markdown)
    weaknesses = extract_section(r'# Weaknesses\n(.*?)(?=\n#|$)', report_markdown)
    keywords = extract_section(r'# Missing Keywords\n(.*?)(?=\n#|$)', report_markdown)
    suggestions = extract_section(r'# Suggestions\n(.*?)(?=\n#|$)', report_markdown)
    return strengths, weaknesses, keywords, suggestions

def send_report_email(analysis) -> None:
    if not analysis.email:
        return
        
    html_content = render_to_string("resume_ats_analyzer/email_report.html", {"analysis": analysis})
    text_content = strip_tags(html_content)
    
    subject = "Your Resume ATS Analysis Report"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@resumely.com')
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [analysis.email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        strengths, weaknesses, keywords, suggestions = extract_report_sections(analysis.report_markdown)
        pdf_bytes = generate_report_pdf(analysis, strengths, weaknesses, keywords, suggestions)
        msg.attach("ats_report.pdf", pdf_bytes, "application/pdf")
        msg.send()
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_builder_email(builder) -> None:
    if not builder.base_analysis or not builder.base_analysis.email:
        return
        
    html_content = render_to_string("resume_ats_analyzer/email_builder.html", {"builder": builder})
    text_content = strip_tags(html_content)
    
    subject = "Your ATS-Friendly Resume is Ready!"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@resumely.com')
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [builder.base_analysis.email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        pdf_bytes = generate_builder_pdf(builder)
        msg.attach("generated_resume.pdf", pdf_bytes, "application/pdf")
        msg.send()
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_latex_template_text(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading latex template: {e}")
        return ""

def generate_ats_resume(resume_text: str, job_description: str) -> str:
    template_path = settings.BASE_DIR / 'resume.tex'
    template_text = get_latex_template_text(template_path)
    
    prompt = f"""
You are an expert resume writer. Rewrite the following resume to be highly ATS-friendly and tailored specifically for the following job description:
{job_description}

Focus on actionable metrics, clear structure, and strong professional summary.

IMPORTANT FORMATTING RULE:
You MUST output raw, valid LaTeX code that strictly uses the identical structure, packages, and custom commands defined in the following template.
Do NOT use Markdown. Do NOT use any packages not already included in the template (CRITICAL: Do NOT use fontspec or setmainfont). Do not output anything other than the LaTeX code (no markdown code blocks, just the raw LaTeX). Make sure to properly escape special LaTeX characters (like &, %, $).

--- TEMPLATE START ---
{template_text}
--- TEMPLATE END ---

Return ONLY the rewritten resume in raw LaTeX code.
Original Resume:
{resume_text}
"""
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a professional ATS resume writer and LaTeX expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            response_text = completion.choices[0].message.content
            if not response_text:
                raise ValueError("Empty response from AI")
                
            # Strip markdown code blocks if the model insists on adding them
            response_text = re.sub(r'^```latex\s*', '', response_text, flags=re.MULTILINE)
            response_text = re.sub(r'^```\s*$', '', response_text, flags=re.MULTILINE)
            return response_text.strip()
        except Exception as e:
            if attempt == max_retries:
                raise AIAnalysisError(f"AI Generation failed after retries: {str(e)}")
            time.sleep(2 ** attempt)

def generate_report_pdf(analysis, strengths, weaknesses, keywords, suggestions) -> bytes:
    html_string = render_to_string(
        "resume_ats_analyzer/report_pdf.html",
        {
            "analysis": analysis,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "keywords": keywords,
            "suggestions": suggestions,
        }
    )
    return HTML(string=html_string).write_pdf()

def generate_builder_pdf(builder) -> bytes:
    import tempfile
    import os
    import subprocess
    
    with tempfile.TemporaryDirectory() as tempdir:
        tex_path = os.path.join(tempdir, "resume.tex")
        with open(tex_path, "w") as f:
            f.write(builder.generated_resume_markdown)
            
        tectonic_path = os.path.join(settings.BASE_DIR, "tectonic")
        env = os.environ.copy()
        env["XDG_CACHE_HOME"] = os.path.join(settings.BASE_DIR, ".cache")
        try:
            subprocess.run([tectonic_path, tex_path], check=True, cwd=tempdir, capture_output=True, env=env)
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else e.stdout.decode()
            print("Tectonic compilation failed:", error_msg)
            raise Exception(f"Failed to compile LaTeX. The AI might have produced invalid markup.")
        
        pdf_path = os.path.join(tempdir, "resume.pdf")
        with open(pdf_path, "rb") as f:
            return f.read()
