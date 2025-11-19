#!/usr/bin/env python3
"""
Register Google Drive webhook using OAuth USER credentials (not service account)

This will make push notifications work for files uploaded by the user!
"""

import json
import os
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Configuration
CLIENT_SECRET_FILE = Path(__file__).parent.parent / "Credentials" / "client_secret_856637549932-5dhvok70ire1cgiran7j1pjbn8qei5jc.apps.googleusercontent.com.json"
TOKEN_FILE = Path(__file__).parent.parent / "Credentials" / "oauth_token.pickle"
CHANNEL_FILE = Path(__file__).parent.parent / "Credentials" / "drive-webhook-channel.json"
PAGE_TOKEN_FILE = Path(__file__).parent.parent / "Credentials" / "drive-page-token.json"
WEBHOOK_URL = "https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_oauth_credentials():
    """Get OAuth credentials, refreshing if needed or prompting for auth"""
    creds = None

    # Try to load existing token
    if TOKEN_FILE.exists():
        print("Loading existing OAuth token...")
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, do OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"⚠️  Token refresh failed: {e}")
                print("Will need to re-authenticate...\n")
                creds = None

        if not creds:
            print("\n" + "="*70)
            print("OAUTH AUTHENTICATION REQUIRED")
            print("="*70 + "\n")
            print("A browser window should open automatically.")
            print("If it doesn't, copy the URL from the console and paste it in your browser.")
            print("\nPlease sign in with: dachevivo@gmail.com")
            print("And grant access to Google Drive.\n")
            print("Waiting for authentication...")

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CLIENT_SECRET_FILE), SCOPES)
                creds = flow.run_local_server(port=8080, prompt='consent')
                print("\n✅ Authentication successful!")
            except Exception as e:
                print(f"\n❌ Authentication failed: {e}")
                print("\nTroubleshooting:")
                print("1. Make sure you're signed in to Google with dachevivo@gmail.com")
                print("2. Check if port 8080 is available")
                print("3. Try running the script again\n")
                raise

        # Save the credentials for next time
        print("Saving OAuth token for future use...")
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Token saved\n")

    return creds

def main():
    print("\n" + "="*70)
    print("REGISTER WEBHOOK WITH OAUTH USER CREDENTIALS")
    print("="*70 + "\n")
    
    print("This script will:")
    print("1. Authenticate using OAuth (as the user, not service account)")
    print("2. Register a webhook for Google Drive changes")
    print("3. Push notifications will work for ALL file uploads!\n")
    
    # Get OAuth credentials
    creds = get_oauth_credentials()
    
    print("\n✅ Authenticated successfully!")
    print(f"   Token valid: {creds.valid}")
    print(f"   Token expiry: {creds.expiry}\n")
    
    # Build Drive service
    service = build('drive', 'v3', credentials=creds)
    
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
        
        # Save pageToken
        with open(PAGE_TOKEN_FILE, 'w') as f:
            json.dump({
                'pageToken': page_token,
                'updatedAt': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"✅ Saved configuration files\n")
        
        print("="*70)
        print("SUCCESS!")
        print("="*70 + "\n")
        print("The webhook is now registered with OAuth USER credentials.")
        print("This means push notifications will work for:")
        print("  ✅ Files uploaded by YOU (dachevivo@gmail.com)")
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

