#!/usr/bin/env python3
"""
Register Google Drive webhook using OAuth token from n8n API

This automatically fetches the OAuth token from n8n and uses it to register the webhook.
"""

import json
import os
import requests
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Configuration
CHANNEL_FILE = Path(__file__).parent.parent / "Credentials" / "drive-webhook-channel.json"
PAGE_TOKEN_FILE = Path(__file__).parent.parent / "Credentials" / "drive-page-token.json"
WEBHOOK_URL = "https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications"
N8N_API_URL = "https://n8n.srv972609.hstgr.cloud/api/v1"
N8N_CREDENTIAL_ID = "5H3AyXzw4vMtE0jL"

def get_n8n_api_key():
    """Get n8n API key from environment or prompt user"""
    api_key = os.environ.get('N8N_API_KEY')
    
    if not api_key:
        print("\n" + "="*70)
        print("N8N API KEY REQUIRED")
        print("="*70 + "\n")
        print("To get your n8n API key:")
        print("1. Go to: https://n8n.srv972609.hstgr.cloud/settings/api")
        print("2. Create a new API key if you don't have one")
        print("3. Copy the API key\n")
        
        api_key = input("Paste your n8n API key here: ").strip()
        
        if not api_key:
            raise ValueError("n8n API key is required!")
    
    return api_key

def get_oauth_token_from_n8n(api_key):
    """Fetch OAuth token from n8n credential"""
    print("Fetching OAuth token from n8n...")
    
    headers = {
        'X-N8N-API-KEY': api_key,
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{N8N_API_URL}/credentials/{N8N_CREDENTIAL_ID}",
            headers=headers
        )
        response.raise_for_status()
        
        credential_data = response.json()
        
        # Extract OAuth token data
        oauth_data = credential_data.get('data', {}).get('oauthTokenData', {})
        access_token = oauth_data.get('access_token')
        
        if not access_token:
            raise ValueError("Could not find access_token in n8n credential")
        
        print("✅ Got OAuth token from n8n\n")
        
        # Create credentials object
        creds = Credentials(
            token=access_token,
            refresh_token=oauth_data.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=credential_data.get('data', {}).get('clientId'),
            client_secret=credential_data.get('data', {}).get('clientSecret')
        )
        
        return creds
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to fetch credential from n8n: {e}")
        print(f"   Response: {e.response.text}\n")
        raise
    except Exception as e:
        print(f"❌ Error: {e}\n")
        raise

def main():
    print("\n" + "="*70)
    print("REGISTER WEBHOOK WITH OAUTH (VIA N8N)")
    print("="*70 + "\n")
    
    print("This script will:")
    print("1. Fetch OAuth token from n8n (already authenticated)")
    print("2. Register a webhook for Google Drive changes")
    print("3. Push notifications will work for ALL file uploads!\n")
    
    # Get n8n API key
    api_key = get_n8n_api_key()
    
    # Get OAuth token from n8n
    creds = get_oauth_token_from_n8n(api_key)
    
    # Build Drive service
    try:
        service = build('drive', 'v3', credentials=creds)
        
        # Test the token by getting user info
        about = service.about().get(fields='user').execute()
        user_email = about['user']['emailAddress']
        print(f"✅ Authenticated as: {user_email}\n")
        
    except Exception as e:
        print(f"❌ Failed to authenticate: {e}\n")
        raise
    
    # Stop old webhook if exists
    if CHANNEL_FILE.exists():
        print("Stopping old webhook channel...")
        try:
            with open(CHANNEL_FILE, 'r') as f:
                old_channel = json.load(f)
            
            service.channels().stop(body={
                'id': old_channel['channelId'],
                'resourceId': old_channel['resourceId']
            }).execute()
            print("✅ Old channel stopped\n")
        except Exception as e:
            print(f"⚠️  Could not stop old channel: {e}\n")
    
    # Get fresh pageToken
    print("Getting fresh pageToken...")
    response = service.changes().getStartPageToken().execute()
    page_token = response.get('startPageToken')
    print(f"✅ Got pageToken: {page_token}\n")
    
    # Register new webhook
    print("Registering webhook with OAuth credentials...")
    
    channel_id = f"1builderrag-oauth-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    expiration = int((datetime.now().timestamp() + 7*24*60*60) * 1000)
    
    body = {
        'id': channel_id,
        'type': 'web_hook',
        'address': WEBHOOK_URL,
        'expiration': str(expiration)
    }
    
    try:
        response = service.changes().watch(
            pageToken=page_token,
            body=body
        ).execute()
        
        print("✅ Webhook registered successfully!")
        print(f"   Channel ID: {response['id']}")
        print(f"   Resource ID: {response['resourceId']}")
        print(f"   Expiration: {datetime.fromtimestamp(int(response['expiration'])/1000)}\n")
        
        # Save channel info
        channel_data = {
            'channelId': response['id'],
            'resourceId': response['resourceId'],
            'resourceUri': response['resourceUri'],
            'expiration': response['expiration'],
            'expirationDate': datetime.fromtimestamp(int(response['expiration'])/1000).isoformat(),
            'webhookUrl': WEBHOOK_URL,
            'pageToken': page_token,
            'registeredAt': datetime.now().isoformat(),
            'authType': 'oauth_user'
        }
        
        with open(CHANNEL_FILE, 'w') as f:
            json.dump(channel_data, f, indent=2)
        print(f"✅ Saved to: {CHANNEL_FILE}")
        
        # Save pageToken
        with open(PAGE_TOKEN_FILE, 'w') as f:
            json.dump({
                'pageToken': page_token,
                'updatedAt': datetime.now().isoformat()
            }, f, indent=2)
        print(f"✅ Saved to: {PAGE_TOKEN_FILE}\n")
        
        print("="*70)
        print("SUCCESS!")
        print("="*70 + "\n")
        print("The webhook is now registered with OAuth USER credentials.")
        print("This means push notifications will work for:")
        print(f"  ✅ Files uploaded by YOU ({user_email})")
        print("  ✅ Files uploaded by anyone with access to your Drive")
        print("  ✅ All changes in your personal Google Drive\n")
        
        print("NEXT STEPS:")
        print(f"1. Update n8n workflow pageToken to: {page_token}")
        print("2. Upload a test file to Google Drive")
        print("3. Check n8n executions within 1-2 minutes")
        print("4. You should see a NEW execution with actual file data!\n")
        
    except Exception as e:
        print(f"❌ Failed to register webhook: {e}\n")
        raise

if __name__ == "__main__":
    main()

