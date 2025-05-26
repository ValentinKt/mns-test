from flask_restful import Resource, reqparse
from flask import jsonify, request
from app.services.directory import DirectoryService

class ChecklistAPI(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('template_id', type=int, required=True)
        self.parser.add_argument('checked_items', type=list, location='json')
        self.parser.add_argument('comment', type=str)

    def get(self, checklist_id):
        checklist_data = DirectoryService.get_checklist(checklist_id)
        return jsonify(checklist_data)

    def post(self):
        # Check if Content-Type is application/json
        if not request.is_json:
            return {"message": "Unsupported Media Type. Request Content-Type must be 'application/json'"}, 415
            
        args = self.parser.parse_args()
        
        checklist_id = DirectoryService.create_checklist(
            args['template_id'], 
            args.get('checked_items', []), 
            args.get('comment')
        )
        return jsonify({'id': checklist_id}), 201

    def delete(self, checklist_id):
        DirectoryService.delete_checklist(checklist_id)
        return '', 204

class ChecklistListAPI(Resource):
    def get(self):
        checklists = DirectoryService.get_all_checklists()
        return jsonify(checklists)
        
    def post(self):
        # Check if Content-Type is application/json
        if not request.is_json:
            return {"message": "Unsupported Media Type. Request Content-Type must be 'application/json'"}, 415
            
        data = request.get_json()
        
        checklist_id = DirectoryService.create_checklist(
            data['template_id'],
            data.get('checked_items', []),
            data.get('comment')
        )
        return jsonify({'id': checklist_id}), 201
