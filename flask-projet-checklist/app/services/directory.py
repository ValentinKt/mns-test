from app import db
from app.models import Template, TemplateItem, Checklist, ChecklistItem
from flask import jsonify

class DirectoryService:
    @staticmethod
    def get_template(template_id):
        """Get a template by ID and format it as JSON"""
        template = Template.query.get_or_404(template_id)
        return {
            'id': template.id,
            'name': template.name,
            'items': [{'id': i.id, 'content': i.content} for i in template.items]
        }
    
    @staticmethod
    def get_all_templates():
        """Get all templates and format them as JSON"""
        templates = Template.query.all()
        return [{
            'id': t.id,
            'name': t.name,
            'items': [{'id': i.id, 'content': i.content} for i in t.items]
        } for t in templates]
    
    @staticmethod
    def create_template(name, items):
        """Create a new template with the given name and items"""
        template = Template(name=name)
        db.session.add(template)
        db.session.flush()  # To get the template.id
        
        for item_content in items:
            item = TemplateItem(content=item_content, template_id=template.id)
            db.session.add(item)
        
        db.session.commit()
        return template.id
    
    @staticmethod
    def delete_template(template_id):
        """Delete a template by ID"""
        template = Template.query.get_or_404(template_id)
        db.session.delete(template)
        db.session.commit()
    
    @staticmethod
    def get_checklist(checklist_id):
        """Get a checklist by ID and format it as JSON"""
        checklist = Checklist.query.get_or_404(checklist_id)
        return {
            'id': checklist.id,
            'template': checklist.template.name,
            'timestamp': checklist.timestamp.isoformat(),
            'comment': checklist.comment,
            'items': [{
                'id': item.id,
                'content': item.template_item.content,
                'checked': item.checked
            } for item in checklist.items]
        }
    
    @staticmethod
    def get_all_checklists():
        """Get all checklists and format them as JSON"""
        checklists = Checklist.query.order_by(Checklist.timestamp.desc()).all()
        return [{
            'id': c.id,
            'template': c.template.name,
            'timestamp': c.timestamp.isoformat(),
            'completed': sum(1 for i in c.items if i.checked),
            'total': len(c.items)
        } for c in checklists]
    
    @staticmethod
    def get_history():
        """Get all checklists and format them as JSON"""
        checklists = Checklist.query.order_by(Checklist.timestamp.desc()).all()

        history_data = []
        #checklists = DirectoryService.get_all_checklists()
        
        for checklist_summary in checklists:
            checklist_id = checklist_summary.id
            checklist_detail = DirectoryService.get_checklist(checklist_id)
            
            checked_items = [item['id'] for item in checklist_detail['items'] if item['checked']]
            
            history_data.append({
                'id': checklist_id,
                'template': {
                    'id': checklist_detail['template_id'] if 'template_id' in checklist_detail else None,
                    'name': checklist_detail['template'],
                    'items': [
                        {
                            'id': item['id'],
                            'content': item['content'],
                            'checked': item['checked']
                     }  for item in checklist_detail['items']]
                },
                'timestamp': checklist_detail['timestamp'],
                'checked_items': checked_items,
                'comment': checklist_detail['comment']
            })
        
        return history_data

    @staticmethod
    def create_checklist(template_id, checked_items=None, comment=None):
        """Create a new checklist for the given template"""
        if checked_items is None:
            checked_items = []
            
        template = Template.query.get_or_404(template_id)
        checklist = Checklist(
            template_id=template.id,
            comment=comment
        )
        
        db.session.add(checklist)
        
        for item in template.items:
            checked = item.id in checked_items
            checklist_item = ChecklistItem(
                checklist_id=checklist.id,
                template_item_id=item.id,
                checked=checked
            )
            db.session.add(checklist_item)
        
        db.session.commit()
        return checklist.id
    
    @staticmethod
    def delete_checklist(checklist_id):
        """Delete a checklist by ID"""
        checklist = Checklist.query.get_or_404(checklist_id)
        db.session.delete(checklist)
        db.session.commit()