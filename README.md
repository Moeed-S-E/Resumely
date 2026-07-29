<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=timeGradient&height=100&section=header" width="100%" />
  <h1>Resumely</h1>
  
  <br />
  
  <a href="https://readme-typing-svg.demolab.com">
    <img src="https://readme-typing-svg.demolab.com/?lines=Beat+the+ATS+Algorithm;Tailor+for+Your+Dream+Job;Instantly+Generate+LaTeX+Resumes;Outsmart+the+Competition&font=Inter&center=true&width=600&height=50&color=4F46E5&vCenter=true&pause=1500&size=22" alt="Typing SVG" />
  </a>

  <br />

  <p align="center">
    <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django"/>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
    <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase"/>
    <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind"/>
    <img src="https://img.shields.io/badge/Three.js-black?style=for-the-badge&logo=three.js&logoColor=white" alt="Three.js"/>

  </p>
</div>

---

<br>

> **Resumely** leverages state-of-the-art LLMs via the **Groq API** to score your resume against target job descriptions, provide actionable insights, and dynamically generate fully-tailored, ATS-friendly resumes in PDF format using the **Tectonic LaTeX** engine.

<br>

## ✨ Epic Features

| Feature | Description |
| :--- | :--- |
| 🎬 **Cinematic UI** | A premium 3D WebGL splash screen built with Three.js featuring dynamic camera orbit and particle physics. |
| 🧠 **AI ATS Scoring** | Rapidly extracts PDF text (`pdfplumber`) and cross-references it with job descriptions using LLaMA-3 70B (via Groq API). |
| 🎯 **Actionable Analytics** | Generates beautiful markdown reports highlighting Strengths, Weaknesses, and critical Missing Keywords. |
| ⚙️ **LaTeX Auto-Builder** | Dynamically rewrites your resume and compiles it into a stunning, ATS-compliant PDF using Tectonic. |
| 📧 **Async Email Delivery** | Sends PDF reports (via WeasyPrint) and tailor-made resumes directly to your inbox using background threading. |


## 💻 Local Setup & Development

### 1. Prerequisites
- `Python 3.10+`
- `Git`
- `tectonic` executable binary placed in the root directory (required for compiling LaTeX PDFs).

### 2. Installation
Drop into your terminal and run:
```bash
git clone https://github.com/Moeed-S-E/Resumely.git
cd Resumely

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the arsenal
pip install -r requirements.txt
```

### 3. Environment Variables (`core/.env`)
```env
SECRET_KEY="super-secret-key"
DEBUG=True
ALLOWED_HOSTS=*
GROQ_API_KEY="your_groq_api_key_here"

# Toggle Database: False for local SQLite, True for production Supabase
RENDER=False

# Email Configuration (for testing SMTP dispatch)
EMAIL_HOST_USER="your-email@gmail.com"
EMAIL_HOST_PASSWORD="your-app-password"
```

### 4. Ignite the Server
```bash
python manage.py migrate
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` and enjoy!


<div align="center">
  <b>Built with ❤️</b><br><br>
  <img src="https://capsule-render.vercel.app/api?type=waving&color=timeGradient&height=100&section=footer" width="100%" />
</div>
