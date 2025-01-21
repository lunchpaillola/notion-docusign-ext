from flask import Blueprint, jsonify, request
from ..utils.errors import DataIOError  # We'll create this

dataio = Blueprint('dataio', __name__)

class DataIOErrorCodes:
    """Error codes for Data IO operations"""
    NOT_FOUND = "NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SCHEMA_RETRIEVAL_FAILED = "SCHEMA_RETRIEVAL_FAILED"

@dataio.errorhandler(DataIOError)
def handle_dataio_error(error):
    """Handle DataIO specific errors"""
    response = {
        "code": error.code,
        "message": error.message
    }
    return jsonify(response), error.status_code

@dataio.route('/getTypeNames', methods=['POST'])
def get_type_names():
    """
    Return supported data types for Notion-DocuSign contract management.
    These types represent the main entities we'll sync between systems.
    """
    try:
        if not request.is_json:
            raise DataIOError(
                code=DataIOErrorCodes.BAD_REQUEST,
                message="Request must be JSON",
                status_code=400
            )

        # Return types regardless of request body content
        return jsonify({
            "typeNames": [
                {
                    "typeName": "contract",
                    "label": "Contract",
                    "description": "A contract document created in Notion ready for DocuSign"
                },
                {
                    "typeName": "signature_request",
                    "label": "Signature Request",
                    "description": "A DocuSign envelope status and tracking information"
                },
                {
                    "typeName": "template",
                    "label": "Contract Template",
                    "description": "Pre-configured contract templates with field mappings"
                },
                {
                    "typeName": "archive",
                    "label": "Archived Contract",
                    "description": "Signed and completed contracts with storage information"
                }
            ]
        })
        
    except DataIOError as e:
        raise
        
    except Exception as e:
        raise DataIOError(
            code=DataIOErrorCodes.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}",
            status_code=500
        )

@dataio.route('/getTypeDefinitions', methods=['POST'])
def get_type_definitions():
    """Return Concerto definitions for contract management types"""
    try:
        print("\n=== GetTypeDefinitions Request ===")
        print("Headers:", dict(request.headers))
        
        if not request.is_json:
            print("❌ Error: Request is not JSON")
            raise DataIOError(
                code=DataIOErrorCodes.BAD_REQUEST,
                message="Request must be JSON",
                status_code=400
            )

        request_data = request.get_json()
        print("Request body:", request_data)
        
        type_names = request_data.get('typeNames')
        print("Requested types:", type_names)
        
        if not type_names:
            print("❌ Error: No typeNames provided")
            raise DataIOError(
                code=DataIOErrorCodes.BAD_REQUEST,
                message="typeNames array is required",
                status_code=400
            )
        
        if not isinstance(type_names, list):
            print("❌ Error: typeNames is not an array")
            raise DataIOError(
                code=DataIOErrorCodes.BAD_REQUEST,
                message="typeNames must be an array",
                status_code=400
            )

        declarations = []
        errors = []
        
        # Process each requested type
        for type_name in type_names:
            print(f"\nProcessing type: {type_name}")
            try:
                if type_name == 'contract':
                    print("✅ Adding contract declaration")
                    declarations.append({
                        "$class": "concerto.metamodel@1.0.0.ConceptDeclaration",
                        "name": "contract",
                        "isAbstract": False,
                        "decorators": [
                            {
                                "$class": "concerto.metamodel@1.0.0.Decorator",
                                "name": "Term",
                                "arguments": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                        "value": "Contract"
                                    }
                                ]
                            },
                            {
                                "$class": "concerto.metamodel@1.0.0.Decorator",
                                "name": "Crud",
                                "arguments": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                        "value": "Createable,Readable,Updateable"
                                    }
                                ]
                            }
                        ],
                        "identified": {
                            "$class": "concerto.metamodel@1.0.0.IdentifiedBy",
                            "name": "id"
                        },
                        "properties": [
                            {
                                "$class": "concerto.metamodel@1.0.0.StringProperty",
                                "name": "id",
                                "isOptional": False,
                                "isArray": False,
                                "decorators": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Term",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Contract ID"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "$class": "concerto.metamodel@1.0.0.StringProperty",
                                "name": "title",
                                "isOptional": False,
                                "isArray": False,
                                "decorators": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Term",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Contract Title"
                                            }
                                        ]
                                    },
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Crud",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Createable,Readable,Updateable"
                                            }
                                        ]
                                    }
                                ],
                                "lengthValidator": {
                                    "$class": "concerto.metamodel@1.0.0.StringLengthValidator",
                                    "maxLength": 100
                                }
                            },
                            {
                                "$class": "concerto.metamodel@1.0.0.StringProperty",
                                "name": "notionPageId",
                                "isOptional": False,
                                "isArray": False,
                                "decorators": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Term",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Notion Page ID"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    })
                elif type_name == 'signature_request':
                    print("✅ Adding signature_request declaration")
                    declarations.append({
                        "$class": "concerto.metamodel@1.0.0.ConceptDeclaration",
                        "name": "signature_request",
                        "isAbstract": False,
                        "decorators": [
                            {
                                "$class": "concerto.metamodel@1.0.0.Decorator",
                                "name": "Term",
                                "arguments": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                        "value": "Signature Request"
                                    }
                                ]
                            },
                            {
                                "$class": "concerto.metamodel@1.0.0.Decorator",
                                "name": "Crud",
                                "arguments": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                        "value": "Createable,Readable,Updateable"
                                    }
                                ]
                            }
                        ],
                        "identified": {
                            "$class": "concerto.metamodel@1.0.0.IdentifiedBy",
                            "name": "envelopeId"
                        },
                        "properties": [
                            {
                                "$class": "concerto.metamodel@1.0.0.StringProperty",
                                "name": "envelopeId",
                                "isOptional": False,
                                "isArray": False,
                                "decorators": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Term",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "DocuSign Envelope ID"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "$class": "concerto.metamodel@1.0.0.StringProperty",
                                "name": "status",
                                "isOptional": False,
                                "isArray": False,
                                "decorators": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Term",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Signature Status"
                                            }
                                        ]
                                    },
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Crud",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Readable,Updateable"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "$class": "concerto.metamodel@1.0.0.RelationshipProperty",
                                "name": "contract",
                                "isOptional": False,
                                "isArray": False,
                                "decorators": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Term",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Associated Contract"
                                            }
                                        ]
                                    }
                                ],
                                "type": {
                                    "$class": "concerto.metamodel@1.0.0.TypeIdentifier",
                                    "name": "contract"
                                }
                            }
                        ]
                    })
                elif type_name == 'template':
                    print("✅ Adding template declaration")
                    declarations.append({
                        "$class": "concerto.metamodel@1.0.0.ConceptDeclaration",
                        "name": "template",
                        "isAbstract": False,
                        "decorators": [
                            {
                                "$class": "concerto.metamodel@1.0.0.Decorator",
                                "name": "Term",
                                "arguments": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                        "value": "Contract Template"
                                    }
                                ]
                            },
                            {
                                "$class": "concerto.metamodel@1.0.0.Decorator",
                                "name": "Crud",
                                "arguments": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                        "value": "Createable,Readable,Updateable"
                                    }
                                ]
                            }
                        ],
                        "identified": {
                            "$class": "concerto.metamodel@1.0.0.IdentifiedBy",
                            "name": "templateId"
                        },
                        "properties": [
                            {
                                "$class": "concerto.metamodel@1.0.0.StringProperty",
                                "name": "templateId",
                                "isOptional": False,
                                "isArray": False,
                                "decorators": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Term",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Template ID"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "$class": "concerto.metamodel@1.0.0.StringProperty",
                                "name": "name",
                                "isOptional": False,
                                "isArray": False,
                                "decorators": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Term",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Template Name"
                                            }
                                        ]
                                    },
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Crud",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Createable,Readable,Updateable"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "$class": "concerto.metamodel@1.0.0.StringProperty",
                                "name": "fieldMappings",
                                "isOptional": True,
                                "isArray": True,
                                "decorators": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Term",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Field Mappings"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    })
                elif type_name == 'archive':
                    print("✅ Adding archive declaration")
                    declarations.append({
                        "$class": "concerto.metamodel@1.0.0.ConceptDeclaration",
                        "name": "archive",
                        "isAbstract": False,
                        "decorators": [
                            {
                                "$class": "concerto.metamodel@1.0.0.Decorator",
                                "name": "Term",
                                "arguments": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                        "value": "Archived Contract"
                                    }
                                ]
                            },
                            {
                                "$class": "concerto.metamodel@1.0.0.Decorator",
                                "name": "Crud",
                                "arguments": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                        "value": "Createable,Readable"
                                    }
                                ]
                            }
                        ],
                        "identified": {
                            "$class": "concerto.metamodel@1.0.0.IdentifiedBy",
                            "name": "archiveId"
                        },
                        "properties": [
                            {
                                "$class": "concerto.metamodel@1.0.0.StringProperty",
                                "name": "archiveId",
                                "isOptional": False,
                                "isArray": False,
                                "decorators": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Term",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Archive ID"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "$class": "concerto.metamodel@1.0.0.StringProperty",
                                "name": "storageUrl",
                                "isOptional": False,
                                "isArray": False,
                                "decorators": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Term",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Storage URL"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "$class": "concerto.metamodel@1.0.0.RelationshipProperty",
                                "name": "contract",
                                "isOptional": False,
                                "isArray": False,
                                "decorators": [
                                    {
                                        "$class": "concerto.metamodel@1.0.0.Decorator",
                                        "name": "Term",
                                        "arguments": [
                                            {
                                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                                "value": "Original Contract"
                                            }
                                        ]
                                    }
                                ],
                                "type": {
                                    "$class": "concerto.metamodel@1.0.0.TypeIdentifier",
                                    "name": "contract"
                                }
                            }
                        ]
                    })
                else:
                    print(f"❌ Unsupported type: {type_name}")
                    errors.append({
                        "typeName": type_name,
                        "code": DataIOErrorCodes.NOT_FOUND,
                        "message": f"Type '{type_name}' is not supported"
                    })
            except Exception as e:
                print(f"❌ Error processing type {type_name}: {str(e)}")
                errors.append({
                    "typeName": type_name,
                    "code": DataIOErrorCodes.SCHEMA_RETRIEVAL_FAILED,
                    "message": f"Failed to process type '{type_name}': {str(e)}"
                })
        
        response_data = {
            "declarations": declarations,
            "errors": errors
        }
        print("\n=== Response Data ===")
        print("Declarations:", len(declarations))
        print("Errors:", len(errors))
        print("Error details:", errors)
        
        return jsonify(response_data)
        
    except DataIOError as e:
        print(f"\n❌ DataIOError: {e.code} - {e.message}")
        raise
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        raise DataIOError(
            code=DataIOErrorCodes.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}",
            status_code=500
        ) 