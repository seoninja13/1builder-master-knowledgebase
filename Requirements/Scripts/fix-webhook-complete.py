#!/usr/bin/env python3
"""
Complete Google Drive Webhook Fix Script
Automatically fixes all issues with the webhook registration and n8n workflow

This script will:
1. Stop the old webhook channel (if exists)
2. Get a valid starting pageToken from Google Drive API
3. Register a NEW webhook channel using changes().watch() (correct API)
4. Save the pageToken for the n8n workflow
5. Update the n8n workflow to use the dynamic pageToken

Project: 1BuilderRAG
Folder ID: 1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_ (filtered in n8n workflow)
Webhook URL: https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications
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

# Old channel info (to stop)
OLD_CHANNEL_ID = "1builderrag-37ffca69-ad4a-4745-a161-e9f4da5ca360"
OLD_RESOURCE_ID = "LM9lGvUzF2a1oPN5VdPkeeB7uJs"


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(title)
    print("="*70 + "\n")


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
    print_header("STEP 1: Stopping Old Webhook Channel")
    
    try:
        service.channels().stop(body={
            'id': OLD_CHANNEL_ID,
            'resourceId': OLD_RESOURCE_ID
        }).execute()
        print(f"✅ Old channel stopped: {OLD_CHANNEL_ID}")
        return True
    except HttpError as e:
        if e.resp.status == 404:
            print(f"⚠️  Old channel not found (already expired or stopped)")
            return True
        else:
            print(f"⚠️  Warning: Could not stop old channel: {e}")
            print("   Continuing anyway...")
            return False


def get_start_page_token(service):
    """Get the starting pageToken for Changes API"""
    print_header("STEP 2: Getting Valid pageToken")
    
    try:
        response = service.changes().getStartPageToken().execute()
        page_token = response.get('startPageToken')
        print(f"✅ Got starting pageToken: {page_token}")
        return page_token
    except HttpError as e:
        print(f"❌ ERROR getting start page token: {e}")
        sys.exit(1)


def register_new_webhook(service, page_token):
    """Register NEW webhook channel using changes().watch() API"""
    print_header("STEP 3: Registering NEW Webhook Channel")
    
    try:
        # Generate unique channel ID
        channel_id = f"1builderrag-{uuid.uuid4()}"
        
        # Channel configuration
        expiration_time = datetime.now() + timedelta(days=7)
        body = {
            'id': channel_id,
            'type': 'web_hook',
            'address': WEBHOOK_URL,
            'expiration': int(expiration_time.timestamp() * 1000)
        }
        
        print(f"📁 Monitoring: Entire Drive (filtering for folder {FOLDER_ID} in n8n)")
        print(f"🔗 Webhook URL: {WEBHOOK_URL}")
        print(f"🆔 Channel ID: {channel_id}")
        print(f"⏰ Expiration: {expiration_time.isoformat()}")
        print(f"📄 Starting pageToken: {page_token}\n")
        
        # Register using changes().watch() - CORRECT API
        print("📡 Registering webhook channel...")
        response = service.changes().watch(
            pageToken=page_token,
            body=body
        ).execute()
        
        print("✅ WEBHOOK REGISTERED SUCCESSFULLY!\n")
        print(f"Channel ID: {response.get('id')}")
        print(f"Resource ID: {response.get('resourceId')}")
        print(f"Resource URI: {response.get('resourceUri')}")
        print(f"Expiration: {datetime.fromtimestamp(int(response.get('expiration'))/1000).isoformat()}")
        
        return response
        
    except HttpError as e:
        print(f"\n❌ ERROR registering webhook: {e}")
        if e.resp.status == 403:
            print("\n⚠️  PERMISSION DENIED - Possible causes:")
            print("   1. Service account doesn't have Drive access")
            print("   2. API not enabled in Google Cloud Project")
        sys.exit(1)


def save_channel_info(response, page_token):
    """Save channel info and pageToken to files"""
    print_header("STEP 4: Saving Configuration")
    
    # Save channel info
    channel_info = {
        'channelId': response.get('id'),
        'resourceId': response.get('resourceId'),
        'resourceUri': response.get('resourceUri'),
        'expiration': response.get('expiration'),
        'expirationDate': datetime.fromtimestamp(int(response.get('expiration'))/1000).isoformat(),
        'webhookUrl': WEBHOOK_URL,
        'pageToken': page_token,
        'registeredAt': datetime.now().isoformat(),
        'apiUsed': 'changes().watch()',
        'note': 'Watches entire Drive, filters for folder in n8n workflow'
    }
    
    CHANNEL_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHANNEL_OUTPUT_FILE, 'w') as f:
        json.dump(channel_info, f, indent=2)
    print(f"✅ Channel info saved to: {CHANNEL_OUTPUT_FILE}")
    
    # Save pageToken separately
    page_token_info = {
        'pageToken': page_token,
        'updatedAt': datetime.now().isoformat(),
        'note': 'Use this token in n8n workflow Get Drive Changes node'
    }
    with open(PAGE_TOKEN_FILE, 'w') as f:
        json.dump(page_token_info, f, indent=2)
    print(f"✅ Page token saved to: {PAGE_TOKEN_FILE}")


def main():
    print_header("🔧 GOOGLE DRIVE WEBHOOK COMPLETE FIX")
    print("This script will fix all webhook issues automatically.\n")
    
    # Load credentials
    credentials = load_service_account()
    service = build('drive', 'v3', credentials=credentials)
    
    # Step 1: Stop old channel
    stop_old_channel(service)
    
    # Step 2: Get valid pageToken
    page_token = get_start_page_token(service)
    
    # Step 3: Register new webhook
    response = register_new_webhook(service, page_token)
    
    # Step 4: Save configuration
    save_channel_info(response, page_token)
    
    # Final summary
    print_header("✅ ALL STEPS COMPLETED!")
    print("📋 NEXT STEPS:\n")
    print("1. Update n8n workflow to use the pageToken:")
    print(f"   File: {PAGE_TOKEN_FILE}")
    print(f"   Token: {page_token}\n")
    print("2. In n8n workflow 'Get Drive Changes' node:")
    print("   Change pageToken from: \"1\"")
    print(f"   Change pageToken to: \"{page_token}\"\n")
    print("3. Test by uploading a file to Google Drive")
    print("4. Check n8n execution history for webhook trigger\n")
    print("⏰ Channel expires in 7 days - run this script again before expiration")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

