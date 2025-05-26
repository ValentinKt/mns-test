from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from app.services import DirectoryService

def init_routes(app):

    # Web routes
    @app.route('/')
    def index():
        templates = DirectoryService.get_all_templates()
        return render_template('index.html', templates=templates)

    @app.route('/create-template', methods=['GET', 'POST'])
    def create_template():
        if request.method == 'POST':
            name = request.form.get('name')
            items = [item.strip() for item in request.form.get('items', '').split('\n') if item.strip()]
            
            if not name or not items:
                flash('Name and at least one item are required', 'error')
                return redirect(url_for('create_template'))
            
            DirectoryService.create_template(name, items)
            flash('Template created successfully!', 'success')
            return redirect(url_for('index'))
        
        return render_template('create_template.html')

    # Add this to your existing routes.py file
    
    @app.route('/fill-checklist/<int:template_id>', methods=['GET', 'POST'])
    def fill_checklist(template_id):
        # Fetch the template using the DirectoryService
        if request.method == 'POST':
            if not request.is_json:
                return {"message": "Unsupported Media Type. Request Content-Type must be 'application/json'"}, 415
                
            data = request.get_json()
            
            checklist_id = DirectoryService.create_checklist(
                data['template_id'],
                data.get('checked_items', []),
                data.get('comment')
            )
            
            if checklist_id:
                flash('Checklist saved successfully!', 'success')
                return jsonify({'id': checklist_id}), 201
            else:
                flash('Error saving checklist', 'error')
                return jsonify({'message': 'Error saving checklist'}), 500
           
        template = DirectoryService.get_template(template_id)
        return render_template('fill_checklist.html', template=template)

    @app.route('/history')
    def history():
        # Get all checklists with detailed information for the template
        history_data = DirectoryService.get_history()
        
        return render_template('history.html', history=history_data)

    @app.route('/delete-history/<int:checklist_id>', methods=['POST'])
    def delete_history(checklist_id):
        DirectoryService.delete_checklist(checklist_id)
        flash('Checklist deleted successfully', 'success')
        return redirect(url_for('history'))

    # Add this context processor to make 'now' available in all templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%d/%m/%Y %H:%M'):
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.strftime(format)
        
    @app.route('/swagger')
    def swagger_ui():
        return render_template('swagger_ui.html')
