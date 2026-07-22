import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import db
from app.models.image import Image
from app.models.caption import Caption
from app.models.object import DetectedObject
from app.models.text import ExtractedText
from app.models.color import DominantColor
from app.models.tag import Tag
from app.models.collection import Collection
from app.models.search_history import SearchHistory
from app.models.embedding import ImageEmbedding
from app.ai.clip import generate_text_embedding, load_embedding_file, calculate_cosine_similarity, generate_image_embedding
from app.services.pdf_report import generate_ai_pdf_report

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def landing():
    popular_categories = ['Cars', 'Animals', 'Medical', 'Food', 'Fashion', 'Architecture']
    recent_searches = SearchHistory.query.order_by(SearchHistory.created_at.desc()).limit(8).all()
    sample_images = Image.query.order_by(Image.upload_time.desc()).limit(12).all()
    return render_template('landing.html', 
                           categories=popular_categories, 
                           recent_searches=recent_searches,
                           sample_images=sample_images)

@dashboard_bp.route('/dashboard')
@login_required
def feed():
    category = request.args.get('category', '').strip()
    tag_filter = request.args.get('tag', '').strip()
    
    query = Image.query.filter_by(user_id=current_user.id)

    if category:
        query = query.join(Image.tags).filter(Tag.tag_name.ilike(f"%{category}%"))
    if tag_filter:
        query = query.join(Image.tags).filter(Tag.tag_name.ilike(f"%{tag_filter}%"))

    images = query.order_by(Image.upload_time.desc()).all()
    user_collections = Collection.query.filter_by(user_id=current_user.id).all()
    
    # Popular category counts
    popular_categories = ['Cars', 'Animals', 'Medical', 'Food', 'Fashion', 'Architecture']

    return render_template('dashboard/feed.html', 
                           images=images, 
                           collections=user_collections,
                           popular_categories=popular_categories,
                           current_category=category)

@dashboard_bp.route('/image/<int:image_id>')
@login_required
def image_detail(image_id):
    img = Image.query.get_or_404(image_id)
    user_collections = Collection.query.filter_by(user_id=current_user.id).all()

    # Find Top Similar Images using CLIP Embeddings (Google Lens style)
    similar_images = []
    if img.embedding:
        current_vec = load_embedding_file(img.embedding.embedding_path)
        if current_vec is not None:
            all_embeddings = ImageEmbedding.query.filter(ImageEmbedding.image_id != img.id).all()
            scored_list = []
            for emb in all_embeddings:
                other_vec = load_embedding_file(emb.embedding_path)
                if other_vec is not None:
                    sim = calculate_cosine_similarity(current_vec, other_vec)
                    scored_list.append((sim, emb.image))
            
            # Sort by similarity descending
            scored_list.sort(key=lambda x: x[0], reverse=True)
            similar_images = [{'sim_score': round(s * 100, 1), 'image': im} for s, im in scored_list[:10]]


    return render_template('dashboard/image_detail.html', 
                           image=img, 
                           collections=user_collections,
                           similar_images=similar_images)

@dashboard_bp.route('/image/<int:image_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(image_id):
    img = Image.query.filter_by(id=image_id, user_id=current_user.id).first_or_404()
    img.is_favorite = not img.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': img.is_favorite})

@dashboard_bp.route('/favorites')
@login_required
def favorites():
    favorite_images = Image.query.filter_by(user_id=current_user.id, is_favorite=True).order_by(Image.upload_time.desc()).all()
    return render_template('dashboard/favorites.html', images=favorite_images)

@dashboard_bp.route('/collections', methods=['GET', 'POST'])
@login_required
def collections():
    if request.method == 'POST':
        name = request.form.get('collection_name', '').strip()
        description = request.form.get('description', '').strip()
        if name:
            new_col = Collection(user_id=current_user.id, collection_name=name, description=description)
            db.session.add(new_col)
            db.session.commit()
            flash(f'Collection "{name}" created!', 'success')
            return redirect(url_for('dashboard.collections'))

    user_cols = Collection.query.filter_by(user_id=current_user.id).order_by(Collection.created_at.desc()).all()
    return render_template('dashboard/collections.html', collections=user_cols)

@dashboard_bp.route('/collections/<int:collection_id>')
@login_required
def collection_detail(collection_id):
    col = Collection.query.filter_by(id=collection_id, user_id=current_user.id).first_or_404()
    return render_template('dashboard/collection_detail.html', collection=col, images=col.images)

@dashboard_bp.route('/collections/add_image', methods=['POST'])
@login_required
def add_to_collection():
    image_id = request.form.get('image_id', type=int)
    collection_id = request.form.get('collection_id', type=int)

    img = Image.query.filter_by(id=image_id, user_id=current_user.id).first_or_404()
    col = Collection.query.filter_by(id=collection_id, user_id=current_user.id).first_or_404()

    if img not in col.images:
        col.images.append(img)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Added to "{col.collection_name}"'})

    return jsonify({'success': True, 'message': 'Image already in collection'})

@dashboard_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    query_text = request.args.get('q', '').strip() or request.form.get('q', '').strip()
    color_hex = request.args.get('color', '').strip()
    results = []

    if query_text:
        # Log search history
        sh = SearchHistory(user_id=current_user.id, query_text=query_text, search_type='natural_language')
        db.session.add(sh)

        db.session.commit()

        # Natural Language Vector Embedding Search via CLIP
        text_vec = generate_text_embedding(query_text)
        all_embeddings = ImageEmbedding.query.join(Image).filter(Image.user_id == current_user.id).all()
        
        scored_list = []
        for emb in all_embeddings:
            img_vec = load_embedding_file(emb.embedding_path)
            if img_vec is not None:
                sim = calculate_cosine_similarity(text_vec, img_vec)
                scored_list.append((sim, emb.image))
        
        scored_list.sort(key=lambda x: x[0], reverse=True)
        results = [{'sim_score': round(s[0] * 100, 1), 'image': im} for s, im in scored_list if s[0] > 0.15]

    elif color_hex:
        # Reverse Color Search
        matching_colors = DominantColor.query.join(Image).filter(
            Image.user_id == current_user.id, 
            DominantColor.hex_code.ilike(f"%{color_hex.replace('#','')}%")
        ).all()
        results = [{'sim_score': col.percentage, 'image': col.image} for col in matching_colors]

    return render_template('dashboard/search.html', query=query_text, color=color_hex, results=results)

@dashboard_bp.route('/analytics')
@login_required
def analytics():
    user_id = current_user.id
    total_images = Image.query.filter_by(user_id=user_id).count()
    
    # Objects breakdown
    top_objects = db.session.query(
        DetectedObject.object_name, 
        func.count(DetectedObject.id).label('count')
    ).join(Image).filter(Image.user_id == user_id).group_by(DetectedObject.object_name).order_by(func.count(DetectedObject.id).desc()).limit(8).all()

    # Dominant Colors breakdown
    top_colors = db.session.query(
        DominantColor.hex_code,
        func.count(DominantColor.id).label('count')
    ).join(Image).filter(Image.user_id == user_id).group_by(DominantColor.hex_code).order_by(func.count(DominantColor.id).desc()).limit(6).all()

    avg_quality = db.session.query(func.avg(Image.quality_score)).filter(Image.user_id == user_id).scalar() or 0.0

    return render_template('dashboard/analytics.html', 
                           total_images=total_images,
                           top_objects=top_objects,
                           top_colors=top_colors,
                           avg_quality=round(avg_quality, 1))

@dashboard_bp.route('/image/<int:image_id>/download_report')
@login_required
def download_report(image_id):
    img = Image.query.filter_by(id=image_id, user_id=current_user.id).first_or_404()
    pdf_filename = f"report_image_{img.id}.pdf"
    pdf_path = os.path.join(current_app.config['REPORT_FOLDER'], pdf_filename)
    
    generate_ai_pdf_report(img, pdf_path)
    return send_file(pdf_path, as_attachment=True, download_name=f"VisionBoard_AI_Report_{img.id}.pdf")

@dashboard_bp.route('/uploads/<filename>')
def serve_upload(filename):
    return send_file(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
