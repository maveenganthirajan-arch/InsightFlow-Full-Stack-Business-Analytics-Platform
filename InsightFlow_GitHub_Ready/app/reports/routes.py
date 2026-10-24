import os
import uuid
import csv
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, current_app, send_file, abort
from flask_login import login_required, current_user
import pandas as pd
from app.reports import reports_bp
from app.models import Report, Dataset, db
from app.analytics.metrics import compute_business_kpis

@reports_bp.route('/')
@login_required
def list_reports():
    reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    return render_template('reports.html', reports=reports, datasets=datasets)

@reports_bp.route('/generate', methods=['POST'])
@login_required
def generate_report():
    dataset_id = request.form.get('dataset_id', type=int)
    report_type = request.form.get('report_type', 'csv').lower()
    title = request.form.get('title', 'Executive Business Performance Report')
    year = request.form.get('year', '2025')

    df = None
    dataset = None
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

    reports_dir = os.path.join(current_app.config['REPORTS_FOLDER'], str(current_user.id))
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"report_{timestamp}_{uuid.uuid4().hex[:6]}.{report_type if report_type in ['csv', 'json'] else 'csv'}"
    file_path = os.path.join(reports_dir, filename)

    if report_type == 'csv':
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['InsightFlow Business Analytics Executive Report'])
            writer.writerow(['Generated At', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')])
            writer.writerow(['Year', year])
            writer.writerow(['Dataset', dataset.original_filename if dataset else 'Built-in Benchmark Data'])
            writer.writerow([])
            writer.writerow(['Metric', 'Value', 'YoY Growth / Change'])
            writer.writerow(['Total Revenue', f"${kpis['total_revenue']:,.2f}", f"+{kpis['revenue_change_pct']}%"])
            writer.writerow(['Paid Orders', f"{kpis['paid_orders']:,}", f"+{kpis['orders_change_pct']}%"])
            writer.writerow(['New Customers', f"{kpis['new_customers']:,}", f"+{kpis['customers_change_pct']}%"])
            writer.writerow(['Conversion Rate', f"{kpis['conversion_rate']}%", f"+{kpis['conversion_change_pp']} pp"])
            writer.writerow(['Total Profit', f"${kpis['total_profit']:,.2f}", f"{kpis['profit_margin']}% Margin"])
            writer.writerow([])
            writer.writerow(['Acquisition Channel Breakdown'])
            writer.writerow(['Channel', 'Revenue', 'Share (%)'])
            for ch in kpis['channels']:
                writer.writerow([ch['channel'], f"${ch['revenue']:,.2f}", f"{ch['percentage']}%"])
            writer.writerow([])
            writer.writerow(['Quarterly Orders'])
            writer.writerow(['Quarter', f"Orders ({year})", 'Prior Year'])
            for q_label, curr_val, prev_val in zip(kpis['quarters']['labels'], kpis['quarters']['current'], kpis['quarters']['previous']):
                writer.writerow([q_label, curr_val, prev_val])
    elif report_type == 'json':
        with open(file_path, 'w', encoding='utf-8') as f:
            import json
            json.dump({
                'title': title,
                'year': year,
                'created_at': datetime.utcnow().isoformat(),
                'kpis': kpis
            }, f, indent=2)

    new_report = Report(
        user_id=current_user.id,
        dataset_id=dataset.id if dataset else None,
        title=title,
        report_type=report_type,
        file_path=file_path
    )
    db.session.add(new_report)
    db.session.commit()

    flash(f"Report '{title}' generated successfully!", 'success')
    return redirect(url_for('reports.list_reports'))

@reports_bp.route('/<int:report_id>/download')
@login_required
def download_report(report_id):
    report = Report.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    if not os.path.exists(report.file_path):
        abort(404)
    download_filename = f"{report.title.replace(' ', '_').lower()}.{report.report_type if report.report_type in ['csv', 'json'] else 'csv'}"
    return send_file(report.file_path, as_attachment=True, download_name=download_filename)

@reports_bp.route('/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    report = Report.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    try:
        if os.path.exists(report.file_path):
            os.remove(report.file_path)
        db.session.delete(report)
        db.session.commit()
        flash(f"Report '{report.title}' removed.", 'info')
    except Exception as e:
        flash(f"Error removing report: {str(e)}", 'danger')

    return redirect(url_for('reports.list_reports'))
