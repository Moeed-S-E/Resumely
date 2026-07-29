import os
import re

unified_header = """<header class="bg-surface dark:bg-[#121212] border-b border-border-subtle dark:border-gray-700 shadow-sm sticky top-0 z-50">
    <nav class="flex justify-between items-center w-full px-4 md:px-8 h-16 max-w-7xl mx-auto">
        <div class="flex items-center gap-8">
            <a href="{% url 'resume_ats_analyzer:upload' %}" class="text-2xl font-extrabold text-primary hover:underline">Resumely</a>
            <div class="flex items-center gap-6">
                <a href="{% url 'resume_ats_analyzer:upload' %}" class="font-bold text-on-surface dark:text-gray-200 hover:text-primary transition-colors flex items-center gap-1">
                    <span class="material-symbols-outlined text-xl">analytics</span> Analyzer
                </a>
                <a href="{% url 'resume_ats_analyzer:builder' %}" class="font-bold text-on-surface dark:text-gray-200 hover:text-primary transition-colors flex items-center gap-1">
                    <span class="material-symbols-outlined text-xl">auto_awesome</span> Builder
                </a>
            </div>
        </div>
        <div class="flex items-center gap-4">
            <button id="themeToggle" class="p-2 text-on-surface dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-800 rounded-full transition-colors flex items-center justify-center">
                <span class="material-symbols-outlined dark:hidden">dark_mode</span>
                <span class="material-symbols-outlined hidden dark:block">light_mode</span>
            </button>
        </div>
    </nav>
</header>"""

templates_dir = "resume_ats_analyzer/templates/resume_ats_analyzer"
files = ["upload.html", "result.html", "builder.html", "builder_result.html"]

for filename in files:
    path = os.path.join(templates_dir, filename)
    with open(path, 'r') as f:
        content = f.read()
        
    new_content = re.sub(r'<header.*?</header>', unified_header, content, flags=re.DOTALL)
    
    with open(path, 'w') as f:
        f.write(new_content)

print("Unified headers across all templates!")
