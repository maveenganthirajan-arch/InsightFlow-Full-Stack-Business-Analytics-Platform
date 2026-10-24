import os
import uuid
import json
import pandas as pd
from flask import render_template, request, redirect, url_for, flash, current_app, send_file, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.datasets import datasets_bp
from app.models import Dataset, db
from app.analytics.cleaning import inspect_dataset

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@datasets_bp.route('/')
@datasets_bp.route('/list')
@login_required
def list_datasets():
    datasets = Dataset.query.filter_by(user_id=current_user.id).order_by(Dataset.created_at.desc()).all()
    return render_template('dataset_list.html', datasets=datasets)

@datasets_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'warning')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            
            user_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id))
            os.makedirs(user_upload_dir, exist_ok=True)
            saved_path = os.path.join(user_upload_dir, unique_filename)

            try:
                file.save(saved_path)
                file_size_kb = os.path.getsize(saved_path) / 1024.0

                # Validate and parse file with pandas
                if extension == 'csv':
                    df = pd.read_csv(saved_path)
                else:
                    df = pd.read_excel(saved_path)

                # Basic dataset metrics
                row_count = len(df)
                column_count = len(df.columns)
                columns = [str(col) for col in df.columns]
                summary = inspect_dataset(df)

                new_dataset = Dataset(
                    user_id=current_user.id,
                    filename=unique_filename,
                    original_filename=original_filename,
                    file_path=saved_path,
                    file_size_kb=file_size_kb,
                    row_count=row_count,
                    column_count=column_count,
                    columns_json=json.dumps(columns),
                    summary_json=json.dumps(summary)
                )

                db.session.add(new_dataset)
                db.session.commit()

                flash(f"Dataset '{original_filename}' uploaded successfully ({row_count:,} rows, {column_count} columns)!", 'success')
                return redirect(url_for('datasets.view_dataset', dataset_id=new_dataset.id))

            except Exception as e:
                if os.path.exists(saved_path):
                    os.remove(saved_path)
                flash(f"Failed to process dataset: {str(e)}", 'danger')
                return redirect(request.url)
        else:
            flash('Invalid file extension. Please upload CSV or Excel (.xlsx, .xls) files.', 'danger')

    return render_template('upload.html')

@datasets_bp.route('/<int:dataset_id>')
@login_required
def view_dataset(dataset_id):
    dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first_or_404()
    
    preview_data = []
    columns = dataset.get_columns()
    summary = dataset.get_summary()

    if os.path.exists(dataset.file_path):
        try:
            if dataset.file_path.endswith('.csv'):
                df = pd.read_csv(dataset.file_path, nrows=50)
            else:
                df = pd.read_excel(dataset.file_path, nrows=50)
            preview_data = df.to_dict(orient='records')
        except Exception as e:
            flash(f"Error loading preview: {str(e)}", 'warning')

    return render_template('dataset_detail.html', dataset=dataset, columns=columns, summary=summary, preview_data=preview_data)

@datasets_bp.route('/<int:dataset_id>/download')
@login_required
def download_dataset(dataset_id):
    dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first_or_404()
    if not os.path.exists(dataset.file_path):
        abort(404)
    return send_file(dataset.file_path, as_attachment=True, download_name=dataset.original_filename)

@datasets_bp.route('/<int:dataset_id>/delete', methods=['POST'])
@login_required
def delete_dataset(dataset_id):
    dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first_or_404()
    try:
        if os.path.exists(dataset.file_path):
            os.remove(dataset.file_path)
        db.session.delete(dataset)
        db.session.commit()
        flash(f"Dataset '{dataset.original_filename}' deleted successfully.", 'info')
    except Exception as e:
        flash(f"Error deleting dataset: {str(e)}", 'danger')

    return redirect(url_for('datasets.list_datasets'))
