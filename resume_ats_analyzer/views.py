from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt
from .models import ResumeAnalysis, ResumeBuilder
from .forms import ResumeUploadForm, ResumeBuilderForm
from .services import extract_resume_text, build_prompt, analyze_with_ai, parse_match_score, send_report_email, send_builder_email, generate_ats_resume, generate_report_pdf, generate_builder_pdf, extract_report_sections, ExtractionError, AIAnalysisError

def upload_view(request):
    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = form.cleaned_data["resume_file"]
            job_description = form.cleaned_data["job_description"]
            email = form.cleaned_data.get("email", "")
            
            analysis = ResumeAnalysis(
                user=request.user if request.user.is_authenticated else None,
                email=email,
                job_description=job_description,
                status="pending"
            )
            analysis.save()
            
            try:
                # Extract text directly from the uploaded file object in memory
                resume_text = extract_resume_text(resume_file)
                analysis.resume_text_extracted = resume_text
                
                # Analyze
                prompt = build_prompt(resume_text, job_description)
                report_markdown = analyze_with_ai(prompt)
                
                analysis.report_markdown = report_markdown
                analysis.match_score = parse_match_score(report_markdown)
                analysis.status = "complete"
                analysis.save()
                
                # Send email asynchronously so it doesn't block the web request
                if analysis.email:
                    import threading
                    threading.Thread(target=send_report_email, args=(analysis,)).start()
                    
                return redirect("resume_ats_analyzer:result", pk=analysis.pk)
                
            except ExtractionError as e:
                analysis.status = "failed"
                analysis.error_message = "We couldn't read text from this PDF. Try a text-based export."
                analysis.save()
                messages.error(request, analysis.error_message)
                return render(request, "resume_ats_analyzer/upload.html", {"form": form})
                
            except (AIAnalysisError, ValueError) as e:
                analysis.status = "failed"
                analysis.error_message = f"Analysis is temporarily unavailable, please try again shortly. Details: {str(e)}"
                analysis.save()
                messages.error(request, analysis.error_message)
                return render(request, "resume_ats_analyzer/upload.html", {"form": form})
                
            except Exception as e:
                analysis.status = "failed"
                analysis.error_message = f"An unexpected error occurred: {str(e)}"
                analysis.save()
                messages.error(request, analysis.error_message)
                return render(request, "resume_ats_analyzer/upload.html", {"form": form})
    else:
        initial = {}
        if request.user.is_authenticated:
            initial['email'] = request.user.email
        form = ResumeUploadForm(initial=initial)
        
    return render(request, "resume_ats_analyzer/upload.html", {"form": form, "debug_mode": settings.DEBUG})

def result_view(request, pk):
    analysis = get_object_or_404(ResumeAnalysis, pk=pk)
    
    # Simple parse for display
    # we can use markdown library in template or here
    import markdown
    html_report = markdown.markdown(analysis.report_markdown)
    
    # Extracted sections
    import re
    
    def extract_section(regex, md):
        match = re.search(regex, md, re.IGNORECASE | re.DOTALL)
        if match:
            items = match.group(1).strip().split('\n')
            return [re.sub(r'^[\*\-]\s+', '', item).strip() for item in items if item.strip()]
        return []
        
    strengths = extract_section(r'# Strengths\n(.*?)(?=\n#|$)', analysis.report_markdown)
    weaknesses = extract_section(r'# Weaknesses\n(.*?)(?=\n#|$)', analysis.report_markdown)
    keywords = extract_section(r'# Missing Keywords\n(.*?)(?=\n#|$)', analysis.report_markdown)
    suggestions = extract_section(r'# Suggestions\n(.*?)(?=\n#|$)', analysis.report_markdown)
    
    context = {
        "analysis": analysis,
        "html_report": html_report,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "keywords": keywords,
        "suggestions": suggestions,
    }
    
    return render(request, "resume_ats_analyzer/result.html", context)


def builder_view(request):
    analysis_id = request.GET.get('analysis_id') or request.POST.get('analysis_id')
    base_analysis = None
    if analysis_id:
        try:
            base_analysis = ResumeAnalysis.objects.get(id=analysis_id)
        except ResumeAnalysis.DoesNotExist:
            pass

    if request.method == "POST":
        form = ResumeBuilderForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = form.cleaned_data.get("resume_file")
            job_description = form.cleaned_data["job_description"]
            
            if not resume_file and not base_analysis:
                messages.error(request, "Please upload a resume to build from.")
                return render(request, "resume_ats_analyzer/builder.html", {"form": form, "base_analysis": base_analysis})
            
            builder = ResumeBuilder(
                user=request.user if request.user.is_authenticated else None,
                base_analysis=base_analysis,
                job_description=job_description,
            )
            builder.save()
            
            try:
                if resume_file:
                    resume_text = extract_resume_text(resume_file)
                else:
                    resume_text = base_analysis.resume_text_extracted
                    
                generated_markdown = generate_ats_resume(resume_text, job_description)
                builder.generated_resume_markdown = generated_markdown
                builder.save()
                
                # Send email asynchronously with generated resume PDF if email is available
                import threading
                threading.Thread(target=send_builder_email, args=(builder,)).start()
                
                return redirect("resume_ats_analyzer:builder_result", pk=builder.pk)
            except Exception as e:
                messages.error(request, f"Error generating resume: {str(e)}")
                return render(request, "resume_ats_analyzer/builder.html", {"form": form, "base_analysis": base_analysis})
    else:
        initial = {}
        if base_analysis:
            initial['job_description'] = base_analysis.job_description
        form = ResumeBuilderForm(initial=initial)
    return render(request, "resume_ats_analyzer/builder.html", {"form": form, "base_analysis": base_analysis})

def builder_result_view(request, pk):
    builder = get_object_or_404(ResumeBuilder, pk=pk)
    return render(request, "resume_ats_analyzer/builder_result.html", {"builder": builder})

def download_report_pdf(request, pk):
    analysis = get_object_or_404(ResumeAnalysis, pk=pk)
    strengths, weaknesses, keywords, suggestions = extract_report_sections(analysis.report_markdown)
    
    pdf_bytes = generate_report_pdf(analysis, strengths, weaknesses, keywords, suggestions)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="ats_report.pdf"'
    return response

@xframe_options_exempt
def download_builder_pdf(request, pk):
    builder = get_object_or_404(ResumeBuilder, pk=pk)
    
    try:
        pdf_bytes = generate_builder_pdf(builder)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="resume.pdf"'
        return response
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)
