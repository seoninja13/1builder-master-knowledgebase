#!/usr/bin/env python3
"""
Test if Google Drive is sending notifications for your file upload

This script will:
1. Check the current pageToken
2. Query the Changes API to see if your file upload is visible
3. Show you exactly what changes Google sees
"""

import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configuration
SERVICE_ACCOUNT_FILE = Path(__file__).parent.parent / "Credentials" / "builder-master-knowldgebase-79a4f60f66e1.json"
PAGE_TOKEN_FILE = Path(__file__).parent.parent / "Credentials" / "drive-page-token.json"
FOLDER_ID = "1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def main():
    print("\n" + "="*70)
    print("TESTING GOOGLE DRIVE CHANGES API")
    print("="*70 + "\n")
    
    # Load credentials
    credentials = service_account.Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_FILE),
        scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)
    
    # Load current pageToken
    with open(PAGE_TOKEN_FILE, 'r') as f:
        data = json.load(f)
    page_token = data['pageToken']
    
    print(f"Current pageToken: {page_token}")
    print(f"Querying changes since this token...\n")
    
    # Query changes
    response = service.changes().list(
        pageToken=page_token,
        fields='changes(file(id,name,mimeType,modifiedTime,parents)),newStartPageToken'
    ).execute()
    
    changes = response.get('changes', [])
    new_token = response.get('newStartPageToken')
    
    print(f"Found {len(changes)} changes\n")
    
    if changes:
        print("="*70)
        print("CHANGES DETECTED:")
        print("="*70 + "\n")
        
        for i, change in enumerate(changes, 1):
            file_data = change.get('file', {})
            print(f"Change #{i}:")
            print(f"  File ID: {file_data.get('id')}")
            print(f"  File Name: {file_data.get('name')}")
            print(f"  MIME Type: {file_data.get('mimeType')}")
            print(f"  Modified: {file_data.get('modifiedTime')}")
            print(f"  Parents: {file_data.get('parents', [])}")
            
            # Check if it's in our folder
            parents = file_data.get('parents', [])
            if FOLDER_ID in parents:
                print(f"  ✅ IN TARGET FOLDER!")
            else:
                print(f"  ⚠️  Not in target folder")
            print()
    else:
        print("❌ NO CHANGES FOUND")
        print("\nThis means:")
        print("1. Either Google hasn't sent a notification yet (wait 1-2 more minutes)")
        print("2. Or the file upload happened BEFORE the webhook was registered")
        print("3. Or there's an issue with the webhook registration\n")
    
    print("="*70)
    print(f"New pageToken: {new_token}")
    print("="*70 + "\n")
    
    # Update the pageToken file
    if new_token:
        data['pageToken'] = new_token
        data['updatedAt'] = json.dumps({"timestamp": "now"})
        with open(PAGE_TOKEN_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Updated pageToken to: {new_token}\n")
    
    print("="*70)
    print("NEXT STEPS:")
    print("="*70 + "\n")
    
    if changes:
        print("✅ Changes detected! The webhook SHOULD have triggered.")
        print("   Check n8n execution history:")
        print("   https://n8n.srv972609.hstgr.cloud/workflow/a5IiavhYT3sOMo4b/executions\n")
        print("   If no execution, the issue is with the webhook notification,")
        print("   not with the Changes API.\n")
    else:
        print("❌ No changes detected. Try uploading a NEW file now:")
        print(f"   https://drive.google.com/drive/folders/{FOLDER_ID}\n")
        print("   Then wait 1-2 minutes and run this script again.\n")

if __name__ == "__main__":
    main()

