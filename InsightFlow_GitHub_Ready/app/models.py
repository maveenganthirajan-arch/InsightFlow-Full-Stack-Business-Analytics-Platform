from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    datasets = db.relationship('Dataset', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    dashboards = db.relationship('Dashboard', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Dataset(db.Model):
    __tablename__ = 'datasets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size_kb = db.Column(db.Float, default=0.0)
    row_count = db.Column(db.Integer, default=0)
    column_count = db.Column(db.Integer, default=0)
    columns_json = db.Column(db.Text, default='[]')
    summary_json = db.Column(db.Text, default='{}')
    is_cleaned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cleaning_jobs = db.relationship('CleaningJob', backref='dataset', lazy='dynamic', cascade='all, delete-orphan')
    analyses = db.relationship('Analysis', backref='dataset', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='dataset', lazy='dynamic', cascade='all, delete-orphan')

    def get_columns(self):
        try:
            return json.loads(self.columns_json or '[]')
        except Exception:
            return []

    def get_summary(self):
        try:
            return json.loads(self.summary_json or '{}')
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'row_count': self.row_count,
            'column_count': self.column_count,
            'file_size_kb': round(self.file_size_kb, 2),
            'is_cleaned': self.is_cleaned,
            'columns': self.get_columns(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }

    def __repr__(self):
        return f'<Dataset {self.original_filename} ({self.id})>'


class CleaningJob(db.Model):
    __tablename__ = 'cleaning_jobs'

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    settings_json = db.Column(db.Text, default='{}')
    rows_removed = db.Column(db.Integer, default=0)
    duplicates_removed = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_settings(self):
        try:
            return json.loads(self.settings_json or '{}')
        except Exception:
            return {}

    def __repr__(self):
        return f'<CleaningJob {self.id} for Dataset {self.dataset_id}>'


class Analysis(db.Model):
    __tablename__ = 'analyses'

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    analysis_type = db.Column(db.String(80), default='business_overview')
    results_json = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_results(self):
        try:
            return json.loads(self.results_json or '{}')
        except Exception:
            return {}

    def __repr__(self):
        return f'<Analysis {self.analysis_type} ({self.id})>'


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    report_type = db.Column(db.String(50), default='csv') # 'csv', 'excel', 'pdf', 'json'
    file_path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'report_type': self.report_type,
            'dataset_id': self.dataset_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }

    def __repr__(self):
        return f'<Report {self.title} ({self.report_type})>'


class Dashboard(db.Model):
    __tablename__ = 'dashboards'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), default='Business Overview')
    settings_json = db.Column(db.Text, default='{}')
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_settings(self):
        try:
            return json.loads(self.settings_json or '{}')
        except Exception:
            return {}

    def __repr__(self):
        return f'<Dashboard {self.name} ({self.id})>'
