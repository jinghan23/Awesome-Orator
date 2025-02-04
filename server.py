from flask import Flask, request, render_template, send_from_directory
import shutil
import os
from functools import wraps

app = Flask(__name__, static_url_path='')
ADMIN_PASSWORD = "your_secret_password"  # Simple password protection

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if auth != ADMIN_PASSWORD:
            return {'error': 'Unauthorized'}, 401
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def root():
    return send_from_directory('.', 'index.html')

@app.route('/pages/<path:filename>')
def serve_pages(filename):
    return send_from_directory('pages', filename)

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/get_pages')
def get_pages():
    pages = []
    for filename in os.listdir('pages'):
        if filename.endswith('.html'):
            file_path = os.path.join('pages', filename)
            # Get file creation time
            creation_time = os.path.getctime(file_path)
            pages.append({
                'filename': filename,
                'url': f'/pages/{filename}',
                'title': filename.replace('.html', '').replace('-', ' ').title(),
                'created': creation_time
            })
    
    # Sort pages by creation time, newest first
    pages.sort(key=lambda x: x['created'], reverse=True)
    return {'pages': pages}

@app.route('/create_page', methods=['POST'])
@requires_auth
def create_page():
    page_type = request.json['type']
    title = request.json['title']
    
    filename = f"pages/{title.lower().replace(' ', '-')}.html"
    
    if os.path.exists(filename):
        return {'error': 'Page already exists'}, 400
    
    if page_type == 'talk':
        with open('templates/talk_template.html', 'r') as template_file:
            template_content = template_file.read()
            content = template_content.replace('[TITLE]', title)
            content = content.replace('[TALK_LINK]', '#')  # You can add a form to input this later
    else:  # reading page
        with open('templates/reading_template.html', 'r') as template_file:
            template_content = template_file.read()
            content = template_content.replace('[TITLE]', title)
            content = content.replace('[PDF_URL]', '#')  # You can add a form to input this later
    
    with open(filename, 'w') as new_file:
        new_file.write(content)
        
    return {'success': True, 'filename': filename}

@app.route('/delete_page', methods=['POST'])
@requires_auth
def delete_page():
    filename = request.json['filename']
    file_path = os.path.join('pages', filename)
    
    if not os.path.exists(file_path):
        return {'error': 'Page not found'}, 404
        
    try:
        os.remove(file_path)
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/chapters/<book_id>')
def get_chapters(book_id):
    book_path = os.path.join('files', book_id)
    chapters = []
    
    if not os.path.exists(book_path):
        return {'error': 'Book not found'}, 404
        
    for filename in sorted(os.listdir(book_path)):
        if filename.endswith('.txt'):
            file_path = os.path.join(book_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                chapters.append({
                    'title': first_line,
                    'file': filename
                })
    
    return chapters

if __name__ == '__main__':
    app.run(debug=True) 