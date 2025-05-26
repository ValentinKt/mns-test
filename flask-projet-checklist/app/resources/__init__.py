from flask_restful import Api
from .template import TemplateAPI, TemplateListAPI
from .checklist import ChecklistAPI, ChecklistListAPI
from flask import Blueprint, jsonify, request
from flask_openapi3 import OpenAPI, Info, Tag
from pydantic import BaseModel, Field
from typing import List, Optional
from flask_swagger_ui import get_swaggerui_blueprint
from app.services.directory import DirectoryService

# Define OpenAPI models for documentation
class TemplateItem(BaseModel):
    id: Optional[int] = Field(None, description="Template item ID")
    content: str = Field(..., description="Content of the template item")

class TemplateBase(BaseModel):
    name: str = Field(..., description="Name of the template")
    items: List[str] = Field(..., description="List of template items")

class TemplateResponse(BaseModel):
    id: int = Field(..., description="Template ID")
    name: str = Field(..., description="Name of the template")
    items: List[TemplateItem] = Field(..., description="List of template items")

class TemplateListResponse(BaseModel):
    id: int = Field(..., description="Template ID")
    name: str = Field(..., description="Name of the template")
    item_count: int = Field(..., description="Number of items in the template")

class ChecklistItem(BaseModel):
    id: int = Field(..., description="Item ID")
    content: str = Field(..., description="Content of the item")
    checked: bool = Field(..., description="Whether the item is checked")

class ChecklistBase(BaseModel):
    template_id: int = Field(..., description="ID of the template")
    checked_items: Optional[List[int]] = Field(None, description="List of checked item IDs")
    comment: Optional[str] = Field(None, description="Comment for the checklist")

class ChecklistResponse(BaseModel):
    id: int = Field(..., description="Checklist ID")
    template: str = Field(..., description="Name of the template")
    timestamp: str = Field(..., description="Timestamp of creation")
    comment: Optional[str] = Field(None, description="Comment for the checklist")
    items: List[ChecklistItem] = Field(..., description="List of checklist items")

class ChecklistListResponse(BaseModel):
    id: int = Field(..., description="Checklist ID")
    template: str = Field(..., description="Name of the template")
    timestamp: str = Field(..., description="Timestamp of creation")
    completed: int = Field(..., description="Number of completed items")
    total: int = Field(..., description="Total number of items")

def init_resources(app):
    # Create a Blueprint for API routes
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)
    
    # Add resources to the API
    api.add_resource(TemplateListAPI, '/api/templates')
    api.add_resource(TemplateAPI, '/api/templates/<int:template_id>')
    api.add_resource(ChecklistListAPI, '/api/checklists')
    api.add_resource(ChecklistAPI, '/api/checklists/<int:checklist_id>')
    
    # Register the blueprint with the app
    return api_bp
    
    # Initialize Swagger UI blueprint
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    
    # Create Swagger UI blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Checklist API"
        }
    )
    
    # Register Swagger UI blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Generate OpenAPI spec
    generate_openapi_spec(app)

def generate_openapi_spec(app):
    """Generate OpenAPI specification and save it to a file"""
    # Define OpenAPI info
    info = {
        "title": "Checklist API",
        "description": "API for managing templates and checklists",
        "version": "1.0.0"
    }
    
    # Define paths
    paths = {
        "/api/templates": {
            "get": {
                "tags": ["Templates"],
                "summary": "Get all templates",
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/TemplateListResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Templates"],
                "summary": "Create a new template",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/TemplateBase"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Template created successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/templates/{template_id}": {
            "get": {
                "tags": ["Templates"],
                "summary": "Get a template by ID",
                "parameters": [
                    {
                        "name": "template_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TemplateResponse"}
                            }
                        }
                    }
                }
            },
            "delete": {
                "tags": ["Templates"],
                "summary": "Delete a template by ID",
                "parameters": [
                    {
                        "name": "template_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "204": {"description": "Template deleted successfully"}
                }
            }
        },
        "/api/checklists": {
            "get": {
                "tags": ["Checklists"],
                "summary": "Get all checklists",
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/ChecklistListResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Checklists"],
                "summary": "Create a new checklist",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ChecklistBase"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Checklist created successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/checklists/{checklist_id}": {
            "get": {
                "tags": ["Checklists"],
                "summary": "Get a checklist by ID",
                "parameters": [
                    {
                        "name": "checklist_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ChecklistResponse"}
                            }
                        }
                    }
                }
            },
            "delete": {
                "tags": ["Checklists"],
                "summary": "Delete a checklist by ID",
                "parameters": [
                    {
                        "name": "checklist_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "204": {"description": "Checklist deleted successfully"}
                }
            }
        }
    }
    
    # Define components
    components = {
        "schemas": {
            "TemplateItem": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "content": {"type": "string"}
                },
                "required": ["content"]
            },
            "TemplateBase": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["name", "items"]
            },
            "TemplateResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/TemplateItem"}
                    }
                },
                "required": ["id", "name", "items"]
            },
            "TemplateListResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "item_count": {"type": "integer"}
                },
                "required": ["id", "name", "item_count"]
            },
            "ChecklistItem": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "content": {"type": "string"},
                    "checked": {"type": "boolean"}
                },
                "required": ["id", "content", "checked"]
            },
            "ChecklistBase": {
                "type": "object",
                "properties": {
                    "template_id": {"type": "integer"},
                    "checked_items": {
                        "type": "array",
                        "items": {"type": "integer"}
                    },
                    "comment": {"type": "string"}
                },
                "required": ["template_id"]
            },
            "ChecklistResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "template": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "comment": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/ChecklistItem"}
                    }
                },
                "required": ["id", "template", "timestamp", "items"]
            },
            "ChecklistListResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "template": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "completed": {"type": "integer"},
                    "total": {"type": "integer"}
                },
                "required": ["id", "template", "timestamp", "completed", "total"]
            }
        }
    }
    
    # Create OpenAPI spec
    openapi_spec = {
        "openapi": "3.0.3",
        "info": info,
        "paths": paths,
        "components": components
    }
    
    # Save OpenAPI spec to file
    import json
    import os
    
    static_dir = os.path.join(app.root_path, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    with open(os.path.join(static_dir, 'swagger.json'), 'w') as f:
        json.dump(openapi_spec, f, indent=2)

    # Import DirectoryService here to avoid circular imports
    from app.services.directory import DirectoryService
    
    # API routes - use app directly
    @app.route("/api/templates", methods=["GET"])
    def get_templates():
        """Get all templates"""
        return jsonify(DirectoryService.get_all_templates())

    @app.route("/api/templates/<int:template_id>", methods=["GET"])
    def get_template(template_id):
        """Get a template by ID"""
        return jsonify(DirectoryService.get_template(template_id))

    @app.route("/api/templates", methods=["POST"])
    def create_template_api():
        """Create a new template"""
        data = request.json
        template_id = DirectoryService.create_template(data['name'], data['items'])
        return jsonify({'id': template_id}), 201

    @app.route("/api/templates/<int:template_id>", methods=["DELETE"])
    def delete_template(template_id):
        """Delete a template by ID"""
        DirectoryService.delete_template(template_id)
        return '', 204

    @app.route("/api/checklists", methods=["GET"])
    def get_checklists():
        """Get all checklists"""
        return jsonify(DirectoryService.get_all_checklists())

    @app.route("/api/checklists/<int:checklist_id>", methods=["GET"])
    def get_checklist(checklist_id):
        """Get a checklist by ID"""
        return jsonify(DirectoryService.get_checklist(checklist_id))

    @app.route("/api/checklists", methods=["POST"])
    def create_checklist_api():
        """Create a new checklist"""
        data = request.json
        checklist_id = DirectoryService.create_checklist(
            data['template_id'],
            data.get('checked_items', []),
            data.get('comment')
        )
        return jsonify({'id': checklist_id}), 201

    @app.route("/api/checklists/<int:checklist_id>", methods=["DELETE"])
    def delete_checklist_api(checklist_id):
        """Delete a checklist by ID"""
        DirectoryService.delete_checklist(checklist_id)
        return '', 204