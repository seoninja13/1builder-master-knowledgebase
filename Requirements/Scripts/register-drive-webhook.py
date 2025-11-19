#!/usr/bin/env python3
"""
Google Drive Push Notification Webhook Registration Script
Registers a push notification channel with Google Drive API to monitor folder changes

Project: 1BuilderRAG
Folder ID: 1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_
Webhook URL: https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications
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
FOLDER_ID = "1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_"
WEBHOOK_URL = "https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications"
SERVICE_ACCOUNT_FILE = Path(__file__).parent.parent / "Credentials" / "builder-master-knowldgebase-79a4f60f66e1.json"
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


def register_webhook(credentials):
    """Register push notification channel with Google Drive API"""
    try:
        service = build('drive', 'v3', credentials=credentials)
        
        # Generate unique channel ID
        channel_id = f"1builderrag-{uuid.uuid4()}"
        
        # Channel configuration
        body = {
            'id': channel_id,
            'type': 'web_hook',
            'address': WEBHOOK_URL,
            'expiration': int((datetime.now() + timedelta(days=7)).timestamp() * 1000)  # 7 days from now
        }
        
        print("\n" + "="*70)
        print("REGISTERING GOOGLE DRIVE PUSH NOTIFICATION CHANNEL")
        print("="*70)
        print(f"Folder ID: {FOLDER_ID}")
        print(f"Webhook URL: {WEBHOOK_URL}")
        print(f"Channel ID: {channel_id}")
        print(f"Expiration: {datetime.fromtimestamp(body['expiration']/1000).isoformat()}")
        print("="*70 + "\n")
        
        # Register the channel
        response = service.files().watch(
            fileId=FOLDER_ID,
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
        
        # Save channel info for renewal
        channel_info = {
            'channel_id': response.get('id'),
            'resource_id': response.get('resourceId'),
            'resource_uri': response.get('resourceUri'),
            'expiration': response.get('expiration'),
            'expiration_datetime': datetime.fromtimestamp(int(response.get('expiration'))/1000).isoformat(),
            'folder_id': FOLDER_ID,
            'webhook_url': WEBHOOK_URL,
            'registered_at': datetime.now().isoformat()
        }
        
        channel_file = Path(__file__).parent.parent / "Credentials" / "drive-webhook-channel.json"
        with open(channel_file, 'w') as f:
            json.dump(channel_info, f, indent=2)
        
        print(f"✅ Channel info saved to: {channel_file}")
        
        return response
        
    except HttpError as e:
        print(f"❌ HTTP ERROR: {e}")
        print(f"Error details: {e.error_details}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)


def stop_webhook(channel_id, resource_id):
    """Stop an existing push notification channel"""
    credentials = load_service_account()
    
    try:
        service = build('drive', 'v3', credentials=credentials)
        
        body = {
            'id': channel_id,
            'resourceId': resource_id
        }
        
        service.channels().stop(body=body).execute()
        print(f"✅ Channel stopped: {channel_id}")
        
    except HttpError as e:
        print(f"❌ ERROR stopping channel: {e}")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("1BUILDERRAG - GOOGLE DRIVE WEBHOOK REGISTRATION")
    print("="*70 + "\n")
    
    # Load credentials
    credentials = load_service_account()
    
    # Register webhook
    register_webhook(credentials)
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Verify n8n webhook workflow is active")
    print("2. Upload a test file to Google Drive folder")
    print("3. Check n8n execution history for webhook trigger")
    print("4. Monitor channel expiration (renew before expiry)")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

