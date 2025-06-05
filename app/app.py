from flask import Flask, render_template, jsonify, send_from_directory, request, send_file
import os
from pathlib import Path
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import io
import unicodedata
import json
from zipfile import ZipFile
import tempfile

CWD = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app = Flask(__name__, 
    static_folder='static',
    template_folder='templates')
CORS(app)  # Enable CORS for all routes

def normalize_ascii_filename(filename):
    # Remove accents and non-ASCII characters
    nfkd = unicodedata.normalize('NFKD', filename)
    return ''.join([c for c in nfkd if not unicodedata.combining(c) and ord(c) < 128])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/logos')
def get_logos():
    category = request.args.get('category', 'All Logos')
    base_dir = CWD
    print(f"[DEBUG] /api/logos called with category: {category}")
    
    # If this is a new category (block4_similarities_<Category>.json exists)
    similarities_file = os.path.join(base_dir, 'data', 'similarities', f'block4_similarities_{category}.json')
    if os.path.exists(similarities_file):
        print(f"[DEBUG] Using similarities file: {similarities_file}")
        with open(similarities_file, 'r') as f:
            similarities_data = json.load(f)
            logo_paths = set()
            if isinstance(similarities_data, dict) and 'scores' in similarities_data:
                for pair in similarities_data['scores'].keys():
                    f1, f2 = pair.split('|')
                    # Guess the directory from the category name
                    if category.startswith('pngs_') and '_inkscape_512' in category:
                        # e.g., category = 'pngs_A_inkscape_512'
                        logo_paths.add(f'data/logos/pngs_ALL_inkscape_512/{category}/{f1}')
                        logo_paths.add(f'data/logos/pngs_ALL_inkscape_512/{category}/{f2}')
                    else:
                        # fallback for other categories
                        logo_paths.add(f'data/logos/pngs_ALL_inkscape_512/new_logos/{f1}')
                        logo_paths.add(f'data/logos/pngs_ALL_inkscape_512/new_logos/{f2}')
            elif isinstance(similarities_data, list):
                # If the file is a list of dicts with 'path', fallback to old logic
                for item in similarities_data:
                    if 'path' in item:
                        filename = os.path.basename(item['path'])
                        logo_paths.add(f'data/logos/pngs_ALL_inkscape_512/new_logos/{filename}')
            logo_paths = list(logo_paths)
            # Filter out missing files
            logo_paths = [p for p in logo_paths if os.path.exists(os.path.join(base_dir, p))]
            print(f"[DEBUG] Returning {len(logo_paths)} logos for category '{category}' (first 5): {logo_paths[:5]}")
            return jsonify(logo_paths)
    
    # If category is a single letter (A-Z)
    if len(category) == 1 and category.isalpha():
        # First try to load the similarity file for this letter
        letter_similarities_file = os.path.join(base_dir, 'data', 'similarities', f'block4_similarities_pngs_{category.upper()}_inkscape_512.json')
        if os.path.exists(letter_similarities_file):
            print(f"[DEBUG] Using letter similarities file: {letter_similarities_file}")
            with open(letter_similarities_file, 'r') as f:
                similarities_data = json.load(f)
                logo_paths = set()
                # If the file has a 'scores' dict, extract filenames from keys
                if isinstance(similarities_data, dict) and 'scores' in similarities_data:
                    for pair in similarities_data['scores'].keys():
                        f1, f2 = pair.split('|')
                        logo_paths.add(f'data/logos/pngs_ALL_inkscape_512/pngs_{category.upper()}_inkscape_512/{f1}')
                        logo_paths.add(f'data/logos/pngs_ALL_inkscape_512/pngs_{category.upper()}_inkscape_512/{f2}')
                # If the file is a list of pairs, fallback to old logic
                elif isinstance(similarities_data, list):
                    for pair in similarities_data:
                        if '|' in pair:
                            f1, f2 = pair.split('|')
                            logo_paths.add(f'data/logos/pngs_ALL_inkscape_512/pngs_{category.upper()}_inkscape_512/{f1}')
                            logo_paths.add(f'data/logos/pngs_ALL_inkscape_512/pngs_{category.upper()}_inkscape_512/{f2}')
                logo_paths = list(logo_paths)
                # Filter out missing files
                logo_paths = [p for p in logo_paths if os.path.exists(os.path.join(base_dir, p))]
                print(f"[DEBUG] Returning {len(logo_paths)} logos for letter '{category}' from similarities (first 5): {logo_paths[:5]}")
                return jsonify(logo_paths)
        
        # If no similarity file exists, fall back to directory listing
        letter_dir = os.path.join(base_dir, 'data/logos/pngs_ALL_inkscape_512', f'pngs_{category.upper()}_inkscape_512')
        if not os.path.exists(letter_dir):
            print(f"[DEBUG] Letter dir missing: {letter_dir}")
            return jsonify([])
        files = [f for f in os.listdir(letter_dir) if f.endswith('.png')]
        logo_paths = [f'data/logos/pngs_ALL_inkscape_512/pngs_{category.upper()}_inkscape_512/{f}' for f in files]
        # Filter out missing files
        logo_paths = [p for p in logo_paths if os.path.exists(os.path.join(base_dir, p))]
        print(f"[DEBUG] Returning {len(logo_paths)} logos for letter '{category}' from directory (first 5): {logo_paths[:5]}")
        return jsonify(logo_paths)
    
    # Default case: return all logos
    return jsonify([])

@app.route('/api/similar/<path:logo_path>')
def get_similar(logo_path):
    set_type = request.args.get('set', 'A')  # Default to set A
    method = request.args.get('method', 'block4')
    print(f"[DEBUG] /api/similar called with logo_path: {logo_path}, set_type: '{set_type}', method: {method}")
    # Handle category-based logos (new_logos)
    if not set_type or set_type == '':
        # Try to infer category from the path
        if 'new_logos' in logo_path:
            # Try to find the category from the currentCategory param (if sent)
            category = request.args.get('category', None)
            if not category:
                # Fallback: try to guess from the logo_path (not robust, but best effort)
                # e.g. logo_path: pngs_ALL_inkscape_512/new_logos/filename.png
                # We can't infer category, so return empty
                print(f"[WARNING] No category provided for new_logos. Returning empty list.")
                return jsonify([])
            similarities_file = os.path.join(CWD, 'data', 'similarities', f'block4_similarities_{category}.json')
            if not os.path.exists(similarities_file):
                print(f"[WARNING] No similarity file found for category {category} at {similarities_file}")
                return jsonify([])
            with open(similarities_file, 'r') as f:
                similarities_data = json.load(f)
                if isinstance(similarities_data, dict) and 'scores' in similarities_data:
                    filename = os.path.basename(logo_path)
                    similar_pairs = []
                    for pair, score in similarities_data['scores'].items():
                        f1, f2 = pair.split('|')
                        if f1 == filename:
                            similar_pairs.append((f'data/logos/pngs_ALL_inkscape_512/new_logos/{f2}', score))
                        elif f2 == filename:
                            similar_pairs.append((f'data/logos/pngs_ALL_inkscape_512/new_logos/{f1}', score))
                    print(f"[DEBUG] Found {len(similar_pairs)} similar pairs for {logo_path} in category {category}")
                    similar_pairs.sort(key=lambda x: x[1], reverse=True)
                    return jsonify(similar_pairs)
                else:
                    print(f"[WARNING] Similarity file for category {category} is not in expected format.")
                    return jsonify([])
        print(f"[WARNING] set_type is empty. This may be a category-based logo. Returning empty list.")
        return jsonify([])
    dir_prefix = f'data/logos/pngs_ALL_inkscape_512/pngs_{set_type}_inkscape_512/'
    print(f"[DEBUG] dir_prefix for similarity search: {dir_prefix}")
    if method == 'block4':
        similarities_file = os.path.join(CWD, 'data', 'similarities', f'block4_similarities_pngs_{set_type}_inkscape_512.json')
        if not os.path.exists(similarities_file):
            print(f"[WARNING] No similarity file found for set {set_type} at {similarities_file}")
            return jsonify([])
        with open(similarities_file, 'r') as f:
            similarities_data = json.load(f)
            if isinstance(similarities_data, dict) and 'scores' in similarities_data:
                similar_pairs = []
                for pair, score in similarities_data['scores'].items():
                    f1, f2 = pair.split('|')
                    f1_full = f1 if f1.startswith(dir_prefix) else dir_prefix + f1.split('/')[-1]
                    f2_full = f2 if f2.startswith(dir_prefix) else dir_prefix + f2.split('/')[-1]
                    if f1_full == logo_path:
                        similar_pairs.append((f2_full, score))
                    elif f2_full == logo_path:
                        similar_pairs.append((f1_full, score))
                print(f"[DEBUG] Found {len(similar_pairs)} block4 similar pairs for {logo_path}")
                similar_pairs.sort(key=lambda x: x[1], reverse=True)
                return jsonify(similar_pairs)
            else:
                print(f"[WARNING] Similarity file for set {set_type} is not in expected format.")
                return jsonify([])
    else:
        # For non-block4 method, we'll use the ssim_scores files
        ssim_file = os.path.join(CWD, 'data', 'similarities', f'ssim_scores_{set_type}.json')
        if not os.path.exists(ssim_file):
            print(f"[WARNING] No SSIM scores file found for set {set_type} at {ssim_file}")
            return jsonify([])
        with open(ssim_file, 'r') as f:
            ssim_scores = json.load(f)
            similar_pairs = []
            for (f1, f2), score in ssim_scores.items():
                f1_full = f1 if f1.startswith(dir_prefix) else dir_prefix + f1.split('/')[-1]
                f2_full = f2 if f2.startswith(dir_prefix) else dir_prefix + f2.split('/')[-1]
                if f1_full == logo_path:
                    similar_pairs.append((f2_full, score))
                elif f2_full == logo_path:
                    similar_pairs.append((f1_full, score))
            print(f"[DEBUG] Found {len(similar_pairs)} similar pairs for {logo_path}")
            similar_pairs.sort(key=lambda x: x[1], reverse=True)
            return jsonify(similar_pairs)

@app.route('/logos/<path:filename>')
def serve_logo(filename):
    base_dir = CWD
    filename = normalize_ascii_filename(filename)
    # Serve from data/logos/pngs_ALL_inkscape_512 if path starts with that prefix
    if filename.startswith('data/logos/pngs_ALL_inkscape_512/'):
        rel_path = filename[len('data/logos/pngs_ALL_inkscape_512/'):]
        directory = os.path.join(base_dir, 'data/logos/pngs_ALL_inkscape_512')
    else:
        # Fallback to old logic for other cases
        logo_path = os.path.join(base_dir, 'logos', filename)
        directory = os.path.dirname(logo_path)
        rel_path = os.path.basename(logo_path)
    
    if not os.path.exists(os.path.join(directory, rel_path)):
        print(f"File not found: {os.path.join(directory, rel_path)}")
        return f"File not found: {filename}", 404
    return send_from_directory(directory, rel_path, as_attachment=False)

@app.route('/api/export_png', methods=['POST'])
def export_png():
    data = request.json
    main_logo = data.get('main_logo')
    similar_logos = data.get('similar_logos', [])  # List of {filename, label, score}
    # Settings
    bg_color = (17, 17, 17)  # #111
    thumb_size = 256
    padding = 48
    # Compose image list (no labels or scores needed)
    all_logos = [main_logo] + [item['filename'] for item in similar_logos]
    # Load images
    images = []
    for logo_filename in all_logos:
        img_path = logo_filename
        resolved_path = None
        if os.path.exists(img_path):
            resolved_path = img_path
        else:
            img_path2 = os.path.join('pngs_A_inkscape_512', logo_filename)
            if os.path.exists(img_path2):
                resolved_path = img_path2
            else:
                img_path3 = os.path.join('logos', logo_filename)
                if os.path.exists(img_path3):
                    resolved_path = img_path3
        print(f"[DEBUG] Logo: {logo_filename} | Resolved path: {resolved_path}")
        if resolved_path:
            try:
                img = Image.open(resolved_path).convert('RGBA')
                img = img.resize((thumb_size, thumb_size), Image.LANCZOS)
            except Exception as e:
                print(f"[ERROR] Failed to load image {resolved_path}: {e}")
                img = Image.new('RGBA', (thumb_size, thumb_size), (0, 0, 0, 0))
        else:
            print(f"[ERROR] Logo file not found: {logo_filename}")
            img = Image.new('RGBA', (thumb_size, thumb_size), (0, 0, 0, 0))
        images.append(img)
    # Calculate output size (no extra height for text)
    n = len(images)
    width = n * thumb_size + (n + 1) * padding
    height = thumb_size + 2 * padding
    out_img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(out_img)
    # Draw each logo (no labels or scores)
    for i, img in enumerate(images):
        x = padding + i * (thumb_size + padding)
        y = padding
        # Draw white rounded rectangle for each logo
        rect_radius = 32
        logo_margin = 16
        draw.rounded_rectangle([x, y, x + thumb_size, y + thumb_size], radius=rect_radius, fill=(255, 255, 255))
        # Resize logo to fit inside the margin
        logo_box = thumb_size - 2 * logo_margin
        img_resized = img.resize((logo_box, logo_box), Image.LANCZOS)
        out_img.paste(img_resized, (x + logo_margin, y + logo_margin), img_resized)
    # Output to bytes
    buf = io.BytesIO()
    out_img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=True, download_name='logos_compare.png')

@app.route('/api/categories')
def get_categories():
    # List all block4_similarities_<Category>.json files in the similarities directory
    base_dir = os.path.join(CWD, 'data', 'similarities')
    files = os.listdir(base_dir)
    categories = []
    for f in files:
        if f.startswith('block4_similarities_') and f.endswith('.json'):
            cat = f[len('block4_similarities_'):-len('.json')]
            # Exclude categories like 'pngs_X_inkscape_512' and 'All Logos'
            if cat.startswith('pngs_') and cat.endswith('_inkscape_512'):
                continue
            if cat.lower() == 'all logos':
                continue
            categories.append(cat)
    categories = sorted(categories, key=lambda x: x.lower())
    return jsonify(categories)

@app.route('/api/export_svgs', methods=['POST'])
def export_svgs():
    data = request.json or {}
    # Optionally accept a list of filenames or a letter/category
    filenames = data.get('filenames')  # List of SVG filenames (relative to svgs/ or svgs/A/ etc)
    letter = data.get('letter')  # e.g., 'A'
    base_svg_dir = os.path.join(CWD, 'data', 'logos', 'svgs')
    svg_files = []
    # Debug: print incoming filenames
    print('[DEBUG] Requested SVG filenames:', filenames)
    found_svgs = []
    missing_svgs = []
    if filenames:
        # Only include requested files
        for fname in filenames:
            fpath = os.path.join(base_svg_dir, fname)
            if os.path.exists(fpath):
                svg_files.append((fname, fpath))
                found_svgs.append(fname)
            else:
                missing_svgs.append(fname)
        print('[DEBUG] Found SVGs:', found_svgs)
        print('[DEBUG] Missing SVGs:', missing_svgs)
    elif letter:
        # Include all SVGs in the letter subdir
        letter_dir = os.path.join(base_svg_dir, letter)
        if os.path.isdir(letter_dir):
            for f in os.listdir(letter_dir):
                if f.endswith('.svg'):
                    svg_files.append((f'{letter}/{f}', os.path.join(letter_dir, f)))
    else:
        # Include all SVGs in base_svg_dir and subdirs
        for root, dirs, files in os.walk(base_svg_dir):
            for f in files:
                if f.endswith('.svg'):
                    rel_path = os.path.relpath(os.path.join(root, f), base_svg_dir)
                    svg_files.append((rel_path, os.path.join(root, f)))
    if not svg_files:
        print('[DEBUG] No SVGs found for export, returning 404')
        return 'No SVGs found for export', 404
    # Create a temporary ZIP file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
        with ZipFile(tmp_zip, 'w') as zipf:
            for i, (_, fpath) in enumerate(svg_files, 1):
                arcname = f'logo_{i}.svg'
                zipf.write(fpath, arcname)
        tmp_zip_path = tmp_zip.name
    # Send the ZIP file
    return send_file(tmp_zip_path, as_attachment=True, download_name='exported_logos.zip')

if __name__ == '__main__':
    app.run(debug=True, port=5001) 