from flask import Blueprint, jsonify

dataio = Blueprint('dataio', __name__)

@dataio.route('/getTypeNames', methods=['POST'])
def get_type_names():
    """
    Return supported data types for Notion-DocuSign contract management.
    These types represent the main entities we'll sync between systems.
    """
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