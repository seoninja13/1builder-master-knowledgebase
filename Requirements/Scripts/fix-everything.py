#!/usr/bin/env python3
"""
MASTER FIX SCRIPT - Fixes Everything Automatically
This is the ONLY script you need to run!

What this script does:
1. Stops the old webhook channel
2. Gets a valid pageToken from Google Drive API
3. Registers a NEW webhook using the correct changes().watch() API
4. Saves all configuration files
5. Provides clear instructions for the final n8n workflow update

Project: 1BuilderRAG
Run this script and follow the final instructions to complete the fix.
"""

import json
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Configuration
FOLDER_ID = "1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_"
WEBHOOK_URL = "https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications"
SERVICE_ACCOUNT_FILE = Path(__file__).parent.parent / "Credentials" / "builder-master-knowldgebase-79a4f60f66e1.json"
CHANNEL_OUTPUT_FILE = Path(__file__).parent.parent / "Credentials" / "drive-webhook-channel.json"
PAGE_TOKEN_FILE = Path(__file__).parent.parent / "Credentials" / "drive-page-token.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
WORKFLOW_ID = "a5IiavhYT3sOMo4b"

# Old channel info
OLD_CHANNEL_ID = "1builderrag-37ffca69-ad4a-4745-a161-e9f4da5ca360"
OLD_RESOURCE_ID = "LM9lGvUzF2a1oPN5VdPkeeB7uJs"


def print_section(title, char="="):
    """Print a formatted section header"""
    print("\n" + char*70)
    print(title)
    print(char*70 + "\n")


def load_service_account():
    """Load service account credentials"""
    if not SERVICE_ACCOUNT_FILE.exists():
        print(f"❌ ERROR: Service account file not found: {SERVICE_ACCOUNT_FILE}")
        sys.exit(1)
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(SERVICE_ACCOUNT_FILE),
            scopes=SCOPES
        )
        print(f"✅ Service account loaded: {credentials.service_account_email}")
        return credentials
    except Exception as e:
        print(f"❌ ERROR loading service account: {e}")
        sys.exit(1)


def stop_old_channel(service):
    """Stop the old webhook channel"""
    print("🛑 Stopping old webhook channel...")
    try:
        service.channels().stop(body={
            'id': OLD_CHANNEL_ID,
            'resourceId': OLD_RESOURCE_ID
        }).execute()
        print(f"✅ Old channel stopped: {OLD_CHANNEL_ID}\n")
    except HttpError as e:
        if e.resp.status == 404:
            print(f"⚠️  Old channel not found (already expired)\n")
        else:
            print(f"⚠️  Warning: {e}\n")


def get_start_page_token(service):
    """Get the starting pageToken for Changes API"""
    print("📄 Getting valid pageToken from Google Drive API...")
    try:
        response = service.changes().getStartPageToken().execute()
        page_token = response.get('startPageToken')
        print(f"✅ Got pageToken: {page_token}\n")
        return page_token
    except HttpError as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)


def register_webhook(service, page_token):
    """Register NEW webhook channel"""
    print("📡 Registering NEW webhook channel...")
    
    channel_id = f"1builderrag-{uuid.uuid4()}"
    expiration_time = datetime.now() + timedelta(days=7)
    
    body = {
        'id': channel_id,
        'type': 'web_hook',
        'address': WEBHOOK_URL,
        'expiration': int(expiration_time.timestamp() * 1000)
    }
    
    try:
        response = service.changes().watch(
            pageToken=page_token,
            body=body
        ).execute()
        
        print(f"✅ Webhook registered successfully!")
        print(f"   Channel ID: {response.get('id')}")
        print(f"   Resource ID: {response.get('resourceId')}")
        print(f"   Expires: {datetime.fromtimestamp(int(response.get('expiration'))/1000).strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return response
    except HttpError as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)


def save_config(response, page_token):
    """Save configuration files"""
    print("💾 Saving configuration files...")
    
    # Channel info
    channel_info = {
        'channelId': response.get('id'),
        'resourceId': response.get('resourceId'),
        'resourceUri': response.get('resourceUri'),
        'expiration': response.get('expiration'),
        'expirationDate': datetime.fromtimestamp(int(response.get('expiration'))/1000).isoformat(),
        'webhookUrl': WEBHOOK_URL,
        'pageToken': page_token,
        'registeredAt': datetime.now().isoformat()
    }
    
    CHANNEL_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHANNEL_OUTPUT_FILE, 'w') as f:
        json.dump(channel_info, f, indent=2)
    
    # Page token
    with open(PAGE_TOKEN_FILE, 'w') as f:
        json.dump({'pageToken': page_token, 'updatedAt': datetime.now().isoformat()}, f, indent=2)
    
    print(f"✅ Saved to: {CHANNEL_OUTPUT_FILE}")
    print(f"✅ Saved to: {PAGE_TOKEN_FILE}\n")


def print_final_instructions(page_token):
    """Print final manual steps"""
    print_section("🎯 FINAL STEP: Update n8n Workflow", "=")
    
    print("Almost done! Just one manual step remaining:\n")
    
    print("1️⃣  Open your workflow:")
    print(f"   https://n8n.srv972609.hstgr.cloud/workflow/{WORKFLOW_ID}\n")
    
    print("2️⃣  Click the 'Get Drive Changes' node\n")
    
    print("3️⃣  Find 'Query Parameters' → 'pageToken'\n")
    
    print("4️⃣  Change the value:")
    print("   ❌ FROM: 1")
    print(f"   ✅ TO:   {page_token}\n")
    
    print("5️⃣  Click 'Save' (top-right corner)\n")
    
    print("6️⃣  Ensure workflow is ACTIVE (toggle in top-right)\n")
    
    print_section("🧪 TEST IT!", "-")
    print("1. Upload a test file to Google Drive:")
    print(f"   https://drive.google.com/drive/folders/{FOLDER_ID}\n")
    print("2. Wait 1-2 minutes\n")
    print("3. Check n8n executions:")
    print(f"   https://n8n.srv972609.hstgr.cloud/workflow/{WORKFLOW_ID}/executions\n")
    print("4. You should see a new execution with actual file changes!\n")
    
    print_section("✅ DONE!", "=")


def main():
    print_section("🚀 1BUILDERRAG WEBHOOK FIX - MASTER SCRIPT", "=")
    print("This script will fix all webhook issues automatically.\n")
    
    # Execute all steps
    credentials = load_service_account()
    service = build('drive', 'v3', credentials=credentials)
    
    stop_old_channel(service)
    page_token = get_start_page_token(service)
    response = register_webhook(service, page_token)
    save_config(response, page_token)
    
    # Print final instructions
    print_final_instructions(page_token)


if __name__ == "__main__":
    main()

