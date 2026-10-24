from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import pandas as pd
import json
import os
from app.analytics import analytics_bp
from app.models import Dataset, CleaningJob, Analysis, db
from app.analytics.metrics import compute_business_kpis
from app.analytics.charts import get_dashboard_chart_configs
from app.analytics.cleaning import inspect_dataset, clean_dataset

@analytics_bp.route('/')
@analytics_bp.route('/dashboard')
@login_required
def dashboard():
    """Main executive analytics dashboard route."""
    datasets = Dataset.query.filter_by(user_id=current_user.id).order_by(Dataset.created_at.desc()).all()
    
    selected_dataset_id = request.args.get('dataset_id', type=int)
    year = request.args.get('year', default='2025')
    
    current_dataset = None
    if selected_dataset_id:
        current_dataset = Dataset.query.filter_by(id=selected_dataset_id, user_id=current_user.id).first()
    elif datasets:
        current_dataset = datasets[0]

    # Calculate metrics
    df = None
    if current_dataset and os.path.exists(current_dataset.file_path):
        try:
            if current_dataset.file_path.endswith('.csv'):
                df = pd.read_csv(current_dataset.file_path)
            else:
                df = pd.read_excel(current_dataset.file_path)
        except Exception as e:
            df = None

    kpis = compute_business_kpis(df, year_filter=year)
    chart_configs = get_dashboard_chart_configs(kpis)

    return render_template(
        'dashboard.html',
        kpis=kpis,
        charts=chart_configs,
        datasets=datasets,
        current_dataset=current_dataset,
        selected_year=year
    )

@analytics_bp.route('/api/kpis')
@login_required
def api_kpis():
    """Returns computed KPIs and chart JSON for AJAX filtering."""
    dataset_id = request.args.get('dataset_id', type=int)
    year = request.args.get('year', default='2025')

    df = None
    if dataset_id:
        dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first()
        if dataset and os.path.exists(dataset.file_path):
            try:
                if dataset.file_path.endswith('.csv'):
                    df = pd.read_csv(dataset.file_path)
                else:
                    df = pd.read_excel(dataset.file_path)
            except Exception:
                df = None

    kpis = compute_business_kpis(df, year_filter=year)
    charts = get_dashboard_chart_configs(kpis)
    return jsonify({
        'status': 'success',
        'kpis': kpis,
        'charts': charts
    })

@analytics_bp.route('/datasets/<int:dataset_id>/clean', methods=['GET', 'POST'])
@login_required
def clean(dataset_id):
    """Data cleaning workbench."""
    dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first_or_404()
    
    if not os.path.exists(dataset.file_path):
        flash('Dataset file not found on disk.', 'danger')
        return redirect(url_for('datasets.list_datasets'))

    try:
        if dataset.file_path.endswith('.csv'):
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)
    except Exception as e:
        flash(f'Error reading dataset: {str(e)}', 'danger')
        return redirect(url_for('datasets.view_dataset', dataset_id=dataset.id))

    if request.method == 'POST':
        options = {
            'remove_duplicates': 'remove_duplicates' in request.form,
            'standardize_column_names': 'standardize_column_names' in request.form,
            'missing_action': request.form.get('missing_action', 'fill_mean_mode'),
            'convert_dates': 'convert_dates' in request.form,
            'drop_empty_cols': 'drop_empty_cols' in request.form
        }

        cleaned_df, stats = clean_dataset(df, options)

        # Save cleaned file back or update
        base_dir = os.path.dirname(dataset.file_path)
        cleaned_filename = f"cleaned_{dataset.filename}"
        cleaned_path = os.path.join(base_dir, cleaned_filename)

        if dataset.file_path.endswith('.csv'):
            cleaned_df.to_csv(cleaned_path, index=False)
        else:
            cleaned_df.to_excel(cleaned_path, index=False)

        # Update or record
        dataset.file_path = cleaned_path
        dataset.row_count = len(cleaned_df)
        dataset.column_count = len(cleaned_df.columns)
        dataset.columns_json = json.dumps([str(c) for c in cleaned_df.columns])
        dataset.is_cleaned = True

        # Log job
        job = CleaningJob(
            dataset_id=dataset.id,
            user_id=current_user.id,
            settings_json=json.dumps(options),
            rows_removed=stats['rows_removed'],
            duplicates_removed=stats['duplicates_removed'],
            status='completed'
        )
        db.session.add(job)
        db.session.commit()

        flash(f"Data cleaning successful! Removed {stats['rows_removed']} rows ({stats['duplicates_removed']} duplicates).", 'success')
        return redirect(url_for('datasets.view_dataset', dataset_id=dataset.id))

    inspection = inspect_dataset(df)
    return render_template('cleaning.html', dataset=dataset, inspection=inspection)
