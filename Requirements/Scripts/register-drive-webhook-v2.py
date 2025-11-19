#!/usr/bin/env python3
"""
Google Drive Push Notification Webhook Registration Script (v2 - CORRECTED)

CRITICAL FIXES:
1. Watches ENTIRE Drive (not just a folder) - Google Drive API requirement
2. Gets valid starting pageToken for Changes API
3. Stores pageToken for n8n workflow to use

Project: 1BuilderRAG
Monitored Folder: 1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_ (filtered in n8n workflow)
Webhook URL: https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications

IMPORTANT: Domain verification required!
Before running this script, verify n8n.srv972609.hstgr.cloud in Google Search Console:
https://search.google.com/search-console
"""

import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Configuration
FOLDER_ID = "1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_"  # For reference only - not used in watch()
WEBHOOK_URL = "https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications"
SERVICE_ACCOUNT_FILE = Path(__file__).parent.parent / "Credentials" / "builder-master-knowldgebase-79a4f60f66e1.json"
CHANNEL_OUTPUT_FILE = Path(__file__).parent.parent / "Credentials" / "drive-webhook-channel.json"
PAGE_TOKEN_FILE = Path(__file__).parent.parent / "Credentials" / "drive-page-token.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


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


def get_start_page_token(service):
    """Get the starting pageToken for Changes API"""
    try:
        response = service.changes().getStartPageToken().execute()
        page_token = response.get('startPageToken')
        print(f"✅ Got starting pageToken: {page_token}")
        return page_token
    except HttpError as e:
        print(f"❌ ERROR getting start page token: {e}")
        sys.exit(1)


def register_webhook(credentials):
    """Register push notification channel with Google Drive API"""
    try:
        service = build('drive', 'v3', credentials=credentials)
        
        # Get starting pageToken FIRST
        page_token = get_start_page_token(service)
        
        # Generate unique channel ID
        channel_id = f"1builderrag-{uuid.uuid4()}"
        
        # Channel configuration
        expiration_time = datetime.now() + timedelta(days=7)
        body = {
            'id': channel_id,
            'type': 'web_hook',
            'address': WEBHOOK_URL,
            'expiration': int(expiration_time.timestamp() * 1000)  # 7 days from now
        }
        
        print("\n" + "="*70)
        print("REGISTERING GOOGLE DRIVE PUSH NOTIFICATION CHANNEL (v2)")
        print("="*70)
        print(f"⚠️  WATCHING: Entire Drive (not just folder)")
        print(f"📁 Folder Filter: {FOLDER_ID} (applied in n8n workflow)")
        print(f"🔗 Webhook URL: {WEBHOOK_URL}")
        print(f"🆔 Channel ID: {channel_id}")
        print(f"⏰ Expiration: {expiration_time.isoformat()}")
        print(f"📄 Starting pageToken: {page_token}")
        print("="*70 + "\n")
        
        print("⚠️  IMPORTANT: Domain Verification Required!")
        print("   Before this works, you MUST verify the domain in Google Search Console:")
        print("   https://search.google.com/search-console")
        print("   Domain to verify: n8n.srv972609.hstgr.cloud")
        print()
        
        # Register the channel - WATCH ENTIRE DRIVE
        print("📡 Registering webhook channel...")
        response = service.changes().watch(
            pageToken=page_token,  # ✅ Use valid pageToken
            body=body
        ).execute()
        
        print("✅ WEBHOOK REGISTERED SUCCESSFULLY!")
        print("\n" + "="*70)
        print("CHANNEL DETAILS")
        print("="*70)
        print(f"Channel ID: {response.get('id')}")
        print(f"Resource ID: {response.get('resourceId')}")
        print(f"Resource URI: {response.get('resourceUri')}")
        print(f"Expiration: {datetime.fromtimestamp(int(response.get('expiration'))/1000).isoformat()}")
        print("="*70 + "\n")
        
        # Save channel info
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
        print(f"✅ Channel info saved to: {CHANNEL_OUTPUT_FILE}")
        
        # Save pageToken separately for n8n workflow
        page_token_info = {
            'pageToken': page_token,
            'updatedAt': datetime.now().isoformat()
        }
        with open(PAGE_TOKEN_FILE, 'w') as f:
            json.dump(page_token_info, f, indent=2)
        print(f"✅ Page token saved to: {PAGE_TOKEN_FILE}")
        
        return channel_info
        
    except HttpError as e:
        print(f"\n❌ ERROR registering webhook: {e}")
        if e.resp.status == 403:
            print("\n⚠️  PERMISSION DENIED - Possible causes:")
            print("   1. Domain not verified in Google Search Console")
            print("   2. Service account doesn't have Drive access")
            print("   3. API not enabled in Google Cloud Project")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)


def main():
    print("\n" + "="*70)
    print("GOOGLE DRIVE WEBHOOK REGISTRATION (v2 - CORRECTED)")
    print("="*70 + "\n")
    
    # Load credentials
    credentials = load_service_account()
    
    # Register webhook
    channel_info = register_webhook(credentials)
    
    print("\n" + "="*70)
    print("✅ REGISTRATION COMPLETE!")
    print("="*70)
    print("\n📋 NEXT STEPS:")
    print("   1. Verify domain in Google Search Console (if not done)")
    print("   2. Wait 24-48 hours for verification to propagate")
    print("   3. Update n8n workflow to use the pageToken from:")
    print(f"      {PAGE_TOKEN_FILE}")
    print("   4. Upload a test file to Google Drive")
    print("   5. Check n8n execution history for webhook trigger")
    print("\n⏰ Channel expires in 7 days - run renew script before expiration")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

