from flask import Blueprint, request, jsonify
from ..utils.errors import AuthError
import base64
import os
import json
import requests
from string import Template

archive = Blueprint('archive', __name__)

@archive.route('/archive', methods=['POST'])
def archive_files():
    """
    Handle DocuSign file archive requests
    
    Expected request:
    {
        "files": [{
            "name": "Agreement {{test-var-1}} about {{test-var-2}}",
            "content": "SSBhZ3JlZSE=",  # Base64 encoded file
            "contentType": "bytes",
            "path": "Folder1/Folder2/",
            "pathTemplateValues": ["1", "Contract negotiation"]
        }]
    }
    """
    try:
        print("\n=== Archive Request ===")
        print("Headers:", dict(request.headers))
        data = request.get_json()
        print("Request Data:", json.dumps(data, indent=2))
        
        if not data or 'files' not in data:
            raise AuthError("No files provided")
            
        processed_files = []
        for file in data['files']:
            # Replace template variables in filename
            filename = file['name']
            if 'pathTemplateValues' in file:
                # Replace {{var-1}} with actual values
                for i, value in enumerate(file['pathTemplateValues']):
                    filename = filename.replace(f"{{{{test-var-{i+1}}}}}", value)
            
            try:
                # Try to decode base64 content, but handle non-base64 content for testing
                content = base64.b64decode(file['content'])
            except Exception as e:
                print(f"Warning: Could not decode base64 content, using raw content for testing")
                content = file['content']
            
            # Log the full request structure
            print(f"\nProcessing file: {filename}")
            print(f"Path: {file.get('path', '')}")
            print(f"Content: {content}")
            print(f"Order: {data.get('order')}")
            print(f"Parent: {data.get('parent')}")
            print(f"Metadata: {data.get('metadata')}")
            
            processed_files.append(filename)
            
        return jsonify({
            "message": f"Successfully processed {len(processed_files)} files",
            "files": processed_files
        }), 200
            
    except Exception as e:
        print(f"❌ Archive Error: {str(e)}")
        return jsonify({
            "message": f"Error processing files: {str(e)}"
        }), 500 