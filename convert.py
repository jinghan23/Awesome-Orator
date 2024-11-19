import os
import json
import shutil
from datetime import datetime

def backend_to_static():
    """Convert backend version to static version"""
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate pages.json from existing pages
    pages = []
    for filename in os.listdir('pages'):
        if filename.endswith('.html'):
            with open(f'pages/{filename}', 'r') as f:
                content = f.read()
                title = content.split('<title>')[1].split('</title>')[0]
                page_type = 'talk' if 'TALK_LINK' in content else 'reading'
                
                page_data = {
                    'title': title,
                    'type': page_type,
                    'url': f'pages/{filename}',
                    'created': os.path.getctime(f'pages/{filename}')
                }
                
                # Extract specific links
                if page_type == 'talk':
                    talk_link = content.split('href="')[2].split('"')[0]
                    page_data['talkLink'] = talk_link
                else:
                    pdf_url = content.split("const url = '")[1].split("'")[0]
                    page_data['pdfUrl'] = pdf_url
                
                pages.append(page_data)
    
    # Sort by creation time
    pages.sort(key=lambda x: x['created'], reverse=True)
    
    # Write to pages.json
    with open('data/pages.json', 'w') as f:
        json.dump({'pages': pages}, f, indent=4)
    
    print("✓ Generated pages.json")
    print("✓ Static version ready")

def static_to_backend():
    """Convert static version to backend version"""
    # Ensure templates directory exists
    os.makedirs('templates', exist_ok=True)
    
    # Copy templates if they don't exist
    if not os.path.exists('templates/talk_template.html'):
        shutil.copy('templates/talk_template.html.bak', 'templates/talk_template.html')
    if not os.path.exists('templates/reading_template.html'):
        shutil.copy('templates/reading_template.html.bak', 'templates/reading_template.html')
    
    print("✓ Templates restored")
    print("✓ Backend version ready")

def backup_templates():
    """Backup template files"""
    shutil.copy('templates/talk_template.html', 'templates/talk_template.html.bak')
    shutil.copy('templates/reading_template.html', 'templates/reading_template.html.bak')
    print("✓ Templates backed up")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python convert.py [to-static|to-backend|backup]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "to-static":
        backend_to_static()
    elif command == "to-backend":
        static_to_backend()
    elif command == "backup":
        backup_templates()
    else:
        print("Invalid command. Use: to-static, to-backend, or backup") 