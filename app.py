from flask import Flask, render_template, jsonify, send_from_directory, request, send_file
from ssim_storage import SSIMStorage
import os
from pathlib import Path
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
storage = SSIMStorage()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/logos')
def get_logos():
    set_type = request.args.get('set', 'A')  # Default to set A
    method = request.args.get('method', 'block4')
    dir_prefix = f'pngs_ALL_inkscape_512/pngs_{set_type}_inkscape_512/'
    if method == 'block4':
        similarities = storage.load_block4_similarities_for_set(set_type)
        logos = set()
        for f1, f2 in similarities.keys():
            logos.add(f1 if f1.startswith(dir_prefix) else dir_prefix + f1.split('/')[-1])
            logos.add(f2 if f2.startswith(dir_prefix) else dir_prefix + f2.split('/')[-1])
        return jsonify(sorted(list(logos)))
    else:
        # Get all unique logo paths from the SSIM scores
        ssim_scores, metadata = storage.load_ssim_scores(name=f'ssim_scores_{set_type}')
        logos = set()
        for (f1, f2) in ssim_scores.keys():
            logos.add(f1 if f1.startswith(dir_prefix) else dir_prefix + f1.split('/')[-1])
            logos.add(f2 if f2.startswith(dir_prefix) else dir_prefix + f2.split('/')[-1])
        return jsonify(sorted(list(logos)))

@app.route('/api/similar/<path:logo_path>')
def get_similar(logo_path):
    set_type = request.args.get('set', 'A')  # Default to set A
    method = request.args.get('method', 'block4')
    dir_prefix = f'pngs_ALL_inkscape_512/pngs_{set_type}_inkscape_512/'
    print(f"[DEBUG] Requested similar logos for: {logo_path} (method={method})")
    if method == 'block4':
        similarities = storage.load_block4_similarities_for_set(set_type)
        similar_pairs = []
        for (f1, f2), score in similarities.items():
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
        ssim_scores, metadata = storage.load_ssim_scores(name=f'ssim_scores_{set_type}')
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
    base_dir = os.path.abspath(os.path.dirname(__file__))
    # If the filename starts with the new ALL path, serve from there
    if filename.startswith('pngs_ALL_inkscape_512/'):
        rel_path = filename[len('pngs_ALL_inkscape_512/'):]
        directory = os.path.join(base_dir, 'pngs_ALL_inkscape_512')
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

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001) 