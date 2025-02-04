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

@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('data', filename)

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
    
    print(f"Attempting to load chapters from: {book_path}")  # Debug log
    
    if not os.path.exists(book_path):
        print(f"Book path not found: {book_path}")  # Debug log
        return {'error': f'Book directory not found: {book_path}'}, 404
        
    try:
        # Get all txt files and sort them numerically
        files = [f for f in os.listdir(book_path) if f.endswith('.txt')]
        print(f"Found {len(files)} text files: {files}")  # Debug log
        
        if not files:
            return {'error': 'No .txt files found in book directory'}, 404
            
        files.sort(key=lambda x: int(x.split('.')[0]))  # Sort by numeric prefix
        
        for filename in files:
            file_path = os.path.join(book_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    chapters.append({
                        'title': first_line or f"Chapter {filename.split('.')[0]}",  # Fallback title if empty
                        'file': filename
                    })
                print(f"Successfully loaded chapter from {filename}")  # Debug log
            except Exception as e:
                print(f"Error reading file {filename}: {str(e)}")  # Debug log
                continue
        
        if not chapters:
            print("No chapters found")  # Debug log
            return {'error': 'No valid chapters found'}, 404
            
        print(f"Successfully loaded {len(chapters)} chapters")  # Debug log
        return {'chapters': chapters}
        
    except Exception as e:
        print(f"Error processing chapters: {str(e)}")  # Debug log
        return {'error': str(e)}, 500

@app.route('/check_files/<book_id>')
def check_files(book_id):
    book_path = os.path.join('files', book_id)
    result = {
        'book_path_exists': os.path.exists(book_path),
        'book_path': book_path,
        'files': []
    }
    
    if result['book_path_exists']:
        try:
            files = os.listdir(book_path)
            result['files'] = files
        except Exception as e:
            result['error'] = str(e)
    
    return result

@app.route('/debug/paths')
def debug_paths():
    return {
        'current_dir': os.getcwd(),
        'data_exists': os.path.exists('data'),
        'data_files': os.listdir('data') if os.path.exists('data') else [],
        'files_exists': os.path.exists('files'),
        'files_contents': os.listdir('files') if os.path.exists('files') else []
    }

@app.route('/files/<path:filename>')
def serve_files(filename):
    print(f"Attempting to serve file: {filename}")  # Debug log
    try:
        return send_from_directory('files', filename)
    except Exception as e:
        print(f"Error serving file: {str(e)}")  # Debug log
        return {'error': str(e)}, 404

if __name__ == '__main__':
    app.run(debug=True) 