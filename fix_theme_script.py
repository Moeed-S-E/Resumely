import os

body_script = """
<script>
    document.addEventListener("DOMContentLoaded", function() {
        const themeBtn = document.getElementById('themeToggle');
        if(themeBtn) {
            themeBtn.addEventListener('click', () => {
                if (document.documentElement.classList.contains('dark')) {
                    document.documentElement.classList.remove('dark');
                    document.documentElement.classList.add('light');
                    localStorage.theme = 'light';
                } else {
                    document.documentElement.classList.add('dark');
                    document.documentElement.classList.remove('light');
                    localStorage.theme = 'dark';
                }
            });
        }
    });
</script>
</body>"""

templates_dir = "resume_ats_analyzer/templates/resume_ats_analyzer"
files = ["upload.html", "result.html", "builder.html", "builder_result.html"]

for filename in files:
    path = os.path.join(templates_dir, filename)
    with open(path, 'r') as f:
        content = f.read()
        
    if 'themeBtn.addEventListener' not in content:
        content = content.replace('</body>', body_script)
        
        with open(path, 'w') as f:
            f.write(content)

print("Injected theme toggle script into all templates")
