from app import db
from datetime import datetime

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    items = db.relationship('TemplateItem', backref='template', lazy=True, cascade='all, delete-orphan')
    checklists = db.relationship('Checklist', backref='template', lazy=True)

class TemplateItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), nullable=False)

class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    comment = db.Column(db.Text)
    items = db.relationship('ChecklistItem', backref='checklist', lazy=True, cascade='all, delete-orphan')

class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'), nullable=False)
    template_item_id = db.Column(db.Integer, db.ForeignKey('template_item.id'), nullable=False)
    checked = db.Column(db.Boolean, default=False)
    template_item = db.relationship('TemplateItem')

