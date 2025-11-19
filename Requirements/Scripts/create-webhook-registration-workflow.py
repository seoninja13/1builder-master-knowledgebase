#!/usr/bin/env python3
"""
Create an n8n workflow that registers the Google Drive webhook using OAuth credentials

This workflow will:
1. Use the existing OAuth credential in n8n
2. Register the webhook via HTTP Request node
3. Save the channel info to a file
"""

import json
import os
from datetime import datetime

# n8n API configuration
N8N_API_URL = "https://n8n.srv972609.hstgr.cloud/api/v1"
N8N_API_KEY = os.environ.get('N8N_API_KEY', '')

def create_workflow():
    """Create workflow JSON for webhook registration"""
    
    workflow = {
        "name": "1BuilderRAG-register-webhook-oauth",
        "nodes": [
            {
                "parameters": {},
                "id": "start-node",
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [240, 300]
            },
            {
                "parameters": {
                    "url": "https://www.googleapis.com/drive/v3/changes/startPageToken",
                    "authentication": "predefinedCredentialType",
                    "nodeCredentialType": "googleDriveOAuth2Api",
                    "options": {}
                },
                "id": "get-page-token",
                "name": "Get Page Token",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [460, 300],
                "credentials": {
                    "googleDriveOAuth2Api": {
                        "id": "5H3AyXzw4vMtE0jL",
                        "name": "Google Drive - 1builderMasterKnowledge"
                    }
                }
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": "https://www.googleapis.com/drive/v3/changes/watch",
                    "authentication": "predefinedCredentialType",
                    "nodeCredentialType": "googleDriveOAuth2Api",
                    "sendQuery": True,
                    "queryParameters": {
                        "parameters": [
                            {
                                "name": "pageToken",
                                "value": "={{ $json.startPageToken }}"
                            }
                        ]
                    },
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "id",
                                "value": f"={{{{ '1builderrag-oauth-{datetime.now().strftime('%Y%m%d-%H%M%S')}' }}}}"
                            },
                            {
                                "name": "type",
                                "value": "web_hook"
                            },
                            {
                                "name": "address",
                                "value": "https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications"
                            },
                            {
                                "name": "expiration",
                                "value": f"={{{{ {int((datetime.now().timestamp() + 7*24*60*60) * 1000)} }}}}"
                            }
                        ]
                    },
                    "options": {}
                },
                "id": "register-webhook",
                "name": "Register Webhook",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [680, 300],
                "credentials": {
                    "googleDriveOAuth2Api": {
                        "id": "5H3AyXzw4vMtE0jL",
                        "name": "Google Drive - 1builderMasterKnowledge"
                    }
                }
            }
        ],
        "connections": {
            "Manual Trigger": {
                "main": [[{"node": "Get Page Token", "type": "main", "index": 0}]]
            },
            "Get Page Token": {
                "main": [[{"node": "Register Webhook", "type": "main", "index": 0}]]
            }
        },
        "settings": {
            "executionOrder": "v1"
        }
    }
    
    return workflow

def main():
    print("\n" + "="*70)
    print("CREATE WEBHOOK REGISTRATION WORKFLOW")
    print("="*70 + "\n")
    
    workflow = create_workflow()
    
    # Save workflow JSON
    output_file = "webhook-registration-workflow.json"
    with open(output_file, 'w') as f:
        json.dump(workflow, f, indent=2)
    
    print(f"✅ Created workflow JSON: {output_file}\n")
    
    print("NEXT STEPS:")
    print("1. Import this workflow into n8n:")
    print("   - Go to: https://n8n.srv972609.hstgr.cloud/workflows")
    print("   - Click 'Import from File'")
    print(f"   - Select: {output_file}")
    print("2. Activate the workflow")
    print("3. Click 'Execute Workflow' to run it manually")
    print("4. Check the execution output for:")
    print("   - Channel ID")
    print("   - Resource ID")
    print("   - Page Token")
    print("5. Update the main webhook workflow with the new pageToken\n")
    
    print("This workflow uses OAuth credentials, so push notifications")
    print("will work for ALL file uploads to your Google Drive!\n")

if __name__ == "__main__":
    main()

