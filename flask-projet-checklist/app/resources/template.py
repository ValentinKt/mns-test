from flask_restful import Resource, reqparse
from flask import jsonify
from app.services import DirectoryService

class TemplateAPI(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=True)
        self.parser.add_argument('items', type=list, location='json', required=True)

    def get(self, template_id):
        print(f"Fetching template with ID: {template_id}")
        template_data = DirectoryService.get_template(template_id)
        return jsonify(template_data)

    def post(self):
        print("Creating a new template")
        args = self.parser.parse_args()
        
        template_id = DirectoryService.create_template(args['name'], args['items'])
        return jsonify({'id': template_id}), 201

    def delete(self, template_id):
        print(f"Deleting template with ID: {template_id}")
        DirectoryService.delete_template(template_id)
        return '', 204

class TemplateListAPI(Resource):
    def get(self):
        print("Fetching all templates")
        templates = DirectoryService.get_all_templates()
        return jsonify(templates)
