import os
import glob

# Dark mode script and toggle logic
head_script = """<head>
    <script>
        if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.add('light');
        }
    </script>"""

toggle_btn = """<div class="flex items-center gap-4">
            <button id="themeToggle" class="p-2 text-on-surface hover:bg-surface-variant rounded-full transition-colors flex items-center justify-center">
                <span class="material-symbols-outlined dark:hidden">dark_mode</span>
                <span class="material-symbols-outlined hidden dark:block">light_mode</span>
            </button>"""

body_script = """
<script>
    document.getElementById('themeToggle')?.addEventListener('click', () => {
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
</script>
</body>
"""

templates_dir = "resume_ats_analyzer/templates/resume_ats_analyzer"

for filename in ["upload.html", "result.html", "builder.html", "builder_result.html"]:
    path = os.path.join(templates_dir, filename)
    with open(path, 'r') as f:
        content = f.read()
    
    # 1. Update html tag
    content = content.replace('<html class="light" lang="en">', '<html lang="en">')
    
    # 2. Inject head script
    if '<script>if (localStorage.theme' not in content:
        content = content.replace('<head>', head_script)
    
    # 3. Inject toggle button
    # Find the rightmost part of the header to inject the button.
    # We can just look for the last </div> before </nav> or </header>
    if 'id="themeToggle"' not in content:
        if '<div class="flex gap-4">' in content:
            content = content.replace('<div class="flex gap-4">', toggle_btn)
        elif '</nav>' in content:
            content = content.replace('</nav>', '    ' + toggle_btn + '</div>\n    </nav>')
        elif '</header>' in content:
            content = content.replace('</header>', '    ' + toggle_btn + '</div>\n    </header>')
    
    # 4. Inject body script
    if 'themeToggle' not in content.split('</body>')[0] or 'localStorage.theme' not in content.split('</body>')[0]:
        content = content.replace('</body>', body_script)
        
    with open(path, 'w') as f:
        f.write(content)
        
print("Updated templates for dark mode")
