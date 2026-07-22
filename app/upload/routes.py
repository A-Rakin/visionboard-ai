import os
import uuid
from flask import Blueprint, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db
from app.models.image import Image
from app.ai.pipeline import process_uploaded_image

upload_bp = Blueprint('upload', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@upload_bp.route('/upload', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files and 'file' not in request.files:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'No image file uploaded.'}), 400
        flash('No file selected.', 'danger')
        return redirect(url_for('dashboard.feed'))

    file = request.files.get('image') or request.files.get('file')
    if file.filename == '':
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'Empty filename selected.'}), 400
        flash('No file selected.', 'danger')
        return redirect(url_for('dashboard.feed'))

    if file and allowed_file(file.filename):
        orig_filename = secure_filename(file.filename)
        ext = orig_filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
        file.save(save_path)

        # Create Database Record
        new_image = Image(
            user_id=current_user.id,
            image_name=unique_name,
            original_filename=orig_filename,
            file_path=save_path,
            processing_status='pending'
        )
        db.session.add(new_image)
        db.session.commit()

        # Run AI Pipeline
        process_uploaded_image(new_image.id, current_app.config['EMBEDDING_FOLDER'])

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({
                'success': True,
                'image_id': new_image.id,
                'redirect_url': url_for('dashboard.image_detail', image_id=new_image.id),
                'message': 'Image uploaded and processed successfully!'
            })

        flash('Image uploaded and processed by AI!', 'success')
        return redirect(url_for('dashboard.image_detail', image_id=new_image.id))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'success': False, 'error': 'Unsupported file type.'}), 400

    flash('Invalid file extension. Supported: JPG, PNG, WEBP.', 'danger')
    return redirect(url_for('dashboard.feed'))
