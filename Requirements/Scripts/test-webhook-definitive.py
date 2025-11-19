#!/usr/bin/env python3
"""
Definitive webhook test:
1. Upload a test file via API
2. Monitor n8n for executions
3. Show exactly what's happening
"""

import json
import time
from pathlib import Path
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests

# Configuration
SERVICE_ACCOUNT_FILE = Path(__file__).parent.parent / "Credentials" / "builder-master-knowldgebase-79a4f60f66e1.json"
FOLDER_ID = "1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_"
SCOPES = ['https://www.googleapis.com/auth/drive']
N8N_API_URL = "https://n8n.srv972609.hstgr.cloud/api/v1"
N8N_API_KEY = "n8n_api_4f0b8c9e2d1a3f5b7e9c0d2a4f6b8e1a3f5b7e9c0d2a4f6b8e1a3f5b7e9c0d2a"  # Replace with actual key
WORKFLOW_ID = "a5IiavhYT3sOMo4b"

def get_n8n_executions():
    """Get recent n8n executions"""
    try:
        headers = {"X-N8N-API-KEY": N8N_API_KEY}
        response = requests.get(
            f"{N8N_API_URL}/executions",
            headers=headers,
            params={"workflowId": WORKFLOW_ID, "limit": 5}
        )
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    except:
        return []

def main():
    print("\n" + "="*70)
    print("DEFINITIVE WEBHOOK TEST")
    print("="*70 + "\n")
    
    # Load credentials
    credentials = service_account.Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_FILE),
        scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)
    
    # Get current execution count
    print("1. Getting current n8n execution count...")
    initial_executions = get_n8n_executions()
    initial_count = len(initial_executions)
    print(f"   Current executions: {initial_count}\n")
    
    # Create a test file
    test_filename = f"webhook-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    test_content = f"Webhook test file created at {datetime.now().isoformat()}"
    
    test_file_path = Path(__file__).parent / test_filename
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    print(f"2. Uploading test file: {test_filename}")
    upload_time = datetime.now()
    print(f"   Upload time: {upload_time.isoformat()}\n")
    
    # Upload to Google Drive
    file_metadata = {
        'name': test_filename,
        'parents': [FOLDER_ID]
    }
    media = MediaFileUpload(str(test_file_path), mimetype='text/plain')
    
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,name,modifiedTime'
    ).execute()
    
    print(f"✅ File uploaded successfully!")
    print(f"   File ID: {uploaded_file['id']}")
    print(f"   File Name: {uploaded_file['name']}")
    print(f"   Modified Time: {uploaded_file['modifiedTime']}\n")
    
    # Clean up local file
    test_file_path.unlink()
    
    # Monitor for webhook notification
    print("="*70)
    print("MONITORING FOR WEBHOOK NOTIFICATION")
    print("="*70 + "\n")
    print("Waiting for Google to send push notification...")
    print("(This can take 10-60 seconds, sometimes up to 5 minutes)\n")
    
    max_wait = 120  # Wait up to 2 minutes
    check_interval = 5  # Check every 5 seconds
    elapsed = 0
    
    while elapsed < max_wait:
        time.sleep(check_interval)
        elapsed += check_interval
        
        current_executions = get_n8n_executions()
        current_count = len(current_executions)
        
        print(f"[{elapsed}s] Checking... (executions: {current_count})", end='\r')
        
        if current_count > initial_count:
            print(f"\n\n✅ NEW EXECUTION DETECTED after {elapsed} seconds!\n")
            
            # Get the new execution
            new_execution = current_executions[0]
            print(f"Execution ID: {new_execution['id']}")
            print(f"Status: {new_execution['status']}")
            print(f"Started: {new_execution['startedAt']}")
            print()
            
            # Check if it's our file
            print("Checking execution details...")
            # Note: Would need to fetch full execution data to see file details
            print("Check the execution in n8n to see if it contains your file!\n")
            break
    else:
        print(f"\n\n❌ NO NEW EXECUTION after {max_wait} seconds\n")
        print("This suggests one of the following:")
        print("  1. Google's notification is delayed (can take up to 5-10 minutes)")
        print("  2. There's an issue with the webhook registration")
        print("  3. Google is batching notifications\n")
        print("Keep monitoring n8n executions for the next few minutes.\n")
    
    print("="*70)
    print("TEST FILE INFO")
    print("="*70 + "\n")
    print(f"File ID: {uploaded_file['id']}")
    print(f"File Name: {uploaded_file['name']}")
    print(f"Upload Time: {upload_time.isoformat()}")
    print(f"View in Drive: https://drive.google.com/file/d/{uploaded_file['id']}/view")
    print(f"View folder: https://drive.google.com/drive/folders/{FOLDER_ID}")
    print()

if __name__ == "__main__":
    main()

