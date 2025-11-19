#!/usr/bin/env python3
"""
Test if push notifications work when the SERVICE ACCOUNT uploads a file
vs when a USER uploads a file

This will help us determine if the issue is related to WHO uploads the file.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configuration
SERVICE_ACCOUNT_FILE = Path(__file__).parent.parent / "Credentials" / "builder-master-knowldgebase-79a4f60f66e1.json"
FOLDER_ID = "1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_"
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    print("\n" + "="*70)
    print("SERVICE ACCOUNT FILE UPLOAD TEST")
    print("="*70 + "\n")
    
    print("HYPOTHESIS:")
    print("Google Drive push notifications might only be sent for changes")
    print("made BY the service account, not FOR files the service account")
    print("has access to.\n")
    
    print("This test will:")
    print("1. Upload a file using the SERVICE ACCOUNT")
    print("2. Check if this triggers a webhook notification")
    print("3. Compare with user-uploaded files\n")
    
    # Load credentials
    credentials = service_account.Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_FILE),
        scopes=SCOPES
    )
    
    with open(SERVICE_ACCOUNT_FILE, 'r') as f:
        sa_data = json.load(f)
    
    service_account_email = sa_data['client_email']
    print(f"Service Account: {service_account_email}\n")
    
    service = build('drive', 'v3', credentials=credentials)
    
    # Create a test file
    test_filename = f"SA-UPLOAD-TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    test_content = f"""
This file was uploaded BY the service account at {datetime.now().isoformat()}

If this triggers a webhook notification but user-uploaded files don't,
then we've found the issue: Google only sends notifications for changes
made BY the authenticated account, not FOR files it has access to.

This would mean we need to use a different approach:
- Option 1: Use OAuth with user credentials instead of service account
- Option 2: Use polling instead of push notifications
- Option 3: Have users upload via an API that uses the service account
"""
    
    test_file_path = Path(__file__).parent / test_filename
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    print(f"Uploading test file: {test_filename}")
    upload_time = datetime.now()
    print(f"Upload time: {upload_time.isoformat()}\n")
    
    # Upload to Google Drive
    file_metadata = {
        'name': test_filename,
        'parents': [FOLDER_ID]
    }
    media = MediaFileUpload(str(test_file_path), mimetype='text/plain')
    
    try:
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,modifiedTime,owners'
        ).execute()
        
        print(f"✅ File uploaded successfully!")
        print(f"   File ID: {uploaded_file['id']}")
        print(f"   File Name: {uploaded_file['name']}")
        print(f"   Modified Time: {uploaded_file['modifiedTime']}")
        print(f"   Owner: {uploaded_file.get('owners', [{}])[0].get('emailAddress', 'N/A')}\n")
        
        # Clean up local file
        test_file_path.unlink()
        
        print("="*70)
        print("NEXT STEPS")
        print("="*70 + "\n")
        print("1. Wait 2-3 minutes")
        print("2. Check n8n executions:")
        print("   https://n8n.srv972609.hstgr.cloud/workflow/a5IiavhYT3sOMo4b/executions")
        print()
        print("3. Look for a NEW execution (not just the sync message)")
        print()
        print("IF YOU SEE A NEW EXECUTION:")
        print("  ✅ The webhook works for service account uploads")
        print("  ❌ But NOT for user uploads")
        print("  → This means we need to use OAuth with user credentials")
        print()
        print("IF YOU DON'T SEE A NEW EXECUTION:")
        print("  ❌ The webhook doesn't work at all")
        print("  → We need to investigate further or use polling")
        print()
        
    except Exception as e:
        print(f"❌ Upload failed: {e}\n")

if __name__ == "__main__":
    main()

