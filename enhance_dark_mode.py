import os

templates_dir = "resume_ats_analyzer/templates/resume_ats_analyzer"
files = ["upload.html", "result.html", "builder.html", "builder_result.html"]

replacements = {
    'bg-surface ': 'bg-surface dark:bg-[#121212] ',
    'bg-surface"': 'bg-surface dark:bg-[#121212]"',
    'bg-white ': 'bg-white dark:bg-[#1e1e1e] ',
    'bg-white"': 'bg-white dark:bg-[#1e1e1e]"',
    'bg-surface-container-lowest ': 'bg-surface-container-lowest dark:bg-[#1e1e1e] ',
    'bg-surface-container-low ': 'bg-surface-container-low dark:bg-[#252525] ',
    'text-text-heading ': 'text-text-heading dark:text-white ',
    'text-text-heading"': 'text-text-heading dark:text-white"',
    'text-on-surface ': 'text-on-surface dark:text-gray-200 ',
    'text-on-surface"': 'text-on-surface dark:text-gray-200"',
    'text-on-surface-variant ': 'text-on-surface-variant dark:text-gray-400 ',
    'border-border-subtle ': 'border-border-subtle dark:border-gray-700 ',
    'border-outline-variant ': 'border-outline-variant dark:border-gray-700 ',
    'bg-gray-50 ': 'bg-gray-50 dark:bg-gray-800 ',
    'bg-[#f7f9fb]': 'bg-[#f7f9fb] dark:bg-[#121212]',
    'text-[#191c1e]': 'text-[#191c1e] dark:text-gray-200',
    'text-slate-900': 'text-slate-900 dark:text-white',
    'text-slate-600': 'text-slate-600 dark:text-gray-400',
    'bg-primary/10': 'bg-primary/10 dark:bg-primary/20',
    'text-gray-600': 'text-gray-600 dark:text-gray-400',
    'text-gray-500': 'text-gray-500 dark:text-gray-400',
    'text-gray-700': 'text-gray-700 dark:text-gray-300',
    'bg-gray-100': 'bg-gray-100 dark:bg-gray-800',
}

for filename in files:
    path = os.path.join(templates_dir, filename)
    with open(path, 'r') as f:
        content = f.read()
        
    for old, new in replacements.items():
        # Prevent double replacement if script is run multiple times
        if new not in content:
            content = content.replace(old, new)
            
    # Extra fix for splash screen gradient
    content = content.replace('background: radial-gradient(ellipse at top left, #F4F6FF 0%, #6B85E8 100%);', 'background: radial-gradient(ellipse at top left, var(--splash-bg-1, #F4F6FF) 0%, var(--splash-bg-2, #6B85E8) 100%);')
    
    with open(path, 'w') as f:
        f.write(content)

print("Injected dark mode utility classes")
