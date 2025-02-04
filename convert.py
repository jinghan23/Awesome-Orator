import os
import json
import shutil
from datetime import datetime

def backend_to_static():
    """Convert backend version to static version"""
    os.makedirs('data', exist_ok=True)
    
    pages = []
    for filename in os.listdir('pages'):
        if filename.endswith('.html'):
            file_path = os.path.join('pages', filename)
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Extract title from filename
                title = filename.replace('.html', '').replace('-', ' ').title()
                
                # Determine page type
                page_type = 'talk' if 'TALK_LINK' in content else 'reading'
                
                page_data = {
                    'title': title,
                    'type': page_type,
                    'url': f'pages/{filename}',
                    'created': os.path.getctime(file_path)
                }
                
                if page_type == 'talk':
                    # Handle talk link
                    try:
                        talk_link = content.split('href="')[2].split('"')[0]
                        if talk_link != '[TALK_LINK]':
                            page_data['talkLink'] = talk_link
                        else:
                            page_data['talkLink'] = '#'
                    except IndexError:
                        page_data['talkLink'] = '#'
                else:
                    # Handle PDF URL
                    try:
                        pdf_url = content.split("const url = '")[1].split("'")[0]
                        if pdf_url != '[PDF_URL]':
                            page_data['pdfUrl'] = pdf_url
                        else:
                            page_data['pdfUrl'] = '#'
                    except IndexError:
                        page_data['pdfUrl'] = '#'
                
                pages.append(page_data)
    
    # Sort by creation time
    pages.sort(key=lambda x: x['created'], reverse=True)
    
    # Write to pages.json
    with open('data/pages.json', 'w') as f:
        json.dump({'pages': pages}, f, indent=4)
    
    # Generate static chapter pages
    books_path = 'files'
    for book_id in os.listdir(books_path):
        book_path = os.path.join(books_path, book_id)
        if os.path.isdir(book_path):
            # Create book pages directory
            book_pages_dir = os.path.join('pages', book_id)
            os.makedirs(book_pages_dir, exist_ok=True)
            
            # Get all chapters
            txt_files = [f for f in os.listdir(book_path) if f.endswith('.txt')]
            txt_files.sort(key=lambda x: int(x.split('.')[0]))
            
            # Generate chapter list HTML
            chapters_html = ''
            for i, filename in enumerate(txt_files):
                chapter_num = filename.split('.')[0]
                with open(os.path.join(book_path, filename), 'r', encoding='utf-8') as f:
                    title = f.readline().strip()
                chapters_html += f'<div class="chapter-item"><a href="{book_id}/chapter_{chapter_num}.html">Chapter {i}: {title}</a></div>\n'
            
            # Generate index page for the book
            with open(os.path.join('templates', 'book_template.html'), 'r', encoding='utf-8') as f:
                book_template = f.read()
            
            book_html = book_template.replace('[CHAPTERS]', chapters_html)
            with open(os.path.join('pages', f'{book_id}.html'), 'w', encoding='utf-8') as f:
                f.write(book_html)
            
            # Generate individual chapter pages
            for filename in txt_files:
                chapter_num = filename.split('.')[0]
                with open(os.path.join(book_path, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    title = lines[0]
                    # Format the content by replacing spaces with newlines
                    text = '\n'.join(lines[1:]).replace(' ', '\n')
                
                with open(os.path.join('templates', 'chapter_template.html'), 'r', encoding='utf-8') as f:
                    chapter_template = f.read()
                
                chapter_html = chapter_template\
                    .replace('[TITLE]', title)\
                    .replace('[CONTENT]', text)\
                    .replace('[BOOK_ID]', book_id)\
                    .replace('[AUDIO_URL]', f'../../files/{book_id}/{chapter_num}.mp3')  # Fix audio path
                
                output_path = os.path.join(book_pages_dir, f'chapter_{chapter_num}.html')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(chapter_html)

    print("✓ Generated pages.json")
    print("✓ Generated static chapter pages")
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