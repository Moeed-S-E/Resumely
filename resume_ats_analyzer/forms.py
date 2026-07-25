from django import forms
from django.conf import settings

class ResumeUploadForm(forms.Form):
    resume_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'absolute inset-0 opacity-0 cursor-pointer',
            'id': 'fileInput',
            'accept': '.pdf'
        })
    )
    job_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full flex-grow p-6 text-body-base border-none focus:ring-0 resize-none custom-scrollbar placeholder:text-outline',
            'id': 'jobDescription',
            'placeholder': 'Paste the job posting here to compare with your resume skills and requirements...'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-white border border-border-subtle focus:border-primary focus:ring-3 focus:ring-primary/20 rounded-lg p-3 transition-all outline-none',
            'id': 'email',
            'placeholder': 'e.g. name@company.com'
        })
    )

    def clean_resume_file(self):
        f = self.cleaned_data["resume_file"]
        if f.content_type != "application/pdf":
            raise forms.ValidationError("Please upload a PDF file.")
        
        max_mb = getattr(settings, 'RESUME_ATS_MAX_UPLOAD_MB', 5)
        if f.size > max_mb * 1024 * 1024:
            raise forms.ValidationError(f"File too large (max {max_mb}MB).")
        return f

class ResumeBuilderForm(forms.Form):
    resume_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'absolute inset-0 opacity-0 cursor-pointer',
            'id': 'fileInput',
            'accept': '.pdf'
        })
    )
    job_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full flex-grow p-6 text-body-base border-none focus:ring-0 resize-none custom-scrollbar placeholder:text-outline',
            'id': 'jobDescription',
            'placeholder': 'Paste the job description here...',
            'rows': 6
        })
    )

    def clean_resume_file(self):
        f = self.cleaned_data.get("resume_file")
        if f:
            if f.content_type != "application/pdf":
                raise forms.ValidationError("Please upload a PDF file.")
            max_mb = getattr(settings, 'RESUME_ATS_MAX_UPLOAD_MB', 5)
            if f.size > max_mb * 1024 * 1024:
                raise forms.ValidationError(f"File too large (max {max_mb}MB).")
        return f
