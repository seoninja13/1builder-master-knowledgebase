#!/usr/bin/env python3
"""
Check the status of the Google Drive webhook channel
"""

import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# Configuration
SERVICE_ACCOUNT_FILE = Path(__file__).parent.parent / "Credentials" / "builder-master-knowldgebase-79a4f60f66e1.json"
CHANNEL_FILE = Path(__file__).parent.parent / "Credentials" / "drive-webhook-channel.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def main():
    print("\n" + "="*70)
    print("WEBHOOK CHANNEL STATUS CHECK")
    print("="*70 + "\n")
    
    # Load channel info
    with open(CHANNEL_FILE, 'r') as f:
        channel_data = json.load(f)
    
    print("Current Channel Configuration:")
    print(f"  Channel ID: {channel_data['channelId']}")
    print(f"  Resource ID: {channel_data['resourceId']}")
    print(f"  Resource URI: {channel_data['resourceUri']}")
    print(f"  Webhook URL: {channel_data['webhookUrl']}")
    print(f"  Registered: {channel_data['registeredAt']}")
    print(f"  Expires: {channel_data['expirationDate']}")
    print()
    
    # Check expiration
    expiration_ms = int(channel_data['expiration'])
    expiration_dt = datetime.fromtimestamp(expiration_ms / 1000)
    now = datetime.now()
    
    if now > expiration_dt:
        print("❌ CHANNEL EXPIRED!")
        print(f"   Expired at: {expiration_dt}")
        print(f"   Current time: {now}")
        print("\n   You need to re-register the webhook.\n")
        return
    else:
        time_left = expiration_dt - now
        print(f"✅ Channel is still active")
        print(f"   Time remaining: {time_left}")
        print()
    
    # Try to stop and immediately re-register to test connectivity
    print("="*70)
    print("TESTING WEBHOOK CONNECTIVITY")
    print("="*70 + "\n")
    
    credentials = service_account.Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_FILE),
        scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)
    
    print("Attempting to stop the current channel...")
    try:
        service.channels().stop(body={
            'id': channel_data['channelId'],
            'resourceId': channel_data['resourceId']
        }).execute()
        print("✅ Successfully stopped channel (channel was active)\n")
    except Exception as e:
        print(f"⚠️  Could not stop channel: {e}")
        print("   This might mean the channel was already inactive.\n")
    
    # Get a fresh pageToken
    print("Getting fresh pageToken...")
    response = service.changes().getStartPageToken().execute()
    page_token = response.get('startPageToken')
    print(f"✅ Got pageToken: {page_token}\n")
    
    # Re-register webhook
    print("Re-registering webhook with changes().watch()...")
    
    body = {
        'id': f"1builderrag-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        'type': 'web_hook',
        'address': channel_data['webhookUrl'],
        'expiration': str(int((datetime.now().timestamp() + 7*24*60*60) * 1000))
    }
    
    try:
        response = service.changes().watch(
            pageToken=page_token,
            body=body
        ).execute()
        
        print("✅ Webhook re-registered successfully!")
        print(f"   New Channel ID: {response['id']}")
        print(f"   Resource ID: {response['resourceId']}")
        print(f"   Expiration: {datetime.fromtimestamp(int(response['expiration'])/1000)}")
        print()
        
        # Save new channel info
        new_channel_data = {
            'channelId': response['id'],
            'resourceId': response['resourceId'],
            'resourceUri': response['resourceUri'],
            'expiration': response['expiration'],
            'expirationDate': datetime.fromtimestamp(int(response['expiration'])/1000).isoformat(),
            'webhookUrl': channel_data['webhookUrl'],
            'pageToken': page_token,
            'registeredAt': datetime.now().isoformat()
        }
        
        with open(CHANNEL_FILE, 'w') as f:
            json.dump(new_channel_data, f, indent=2)
        
        print(f"✅ Saved new channel info to: {CHANNEL_FILE}")
        print()
        
        print("="*70)
        print("NEXT STEPS")
        print("="*70 + "\n")
        print(f"1. Update n8n workflow pageToken to: {page_token}")
        print("2. Upload a test file to Google Drive")
        print("3. Check n8n executions within 1-2 minutes")
        print()
        print("If you still don't see executions, the issue is likely:")
        print("  - Service account permissions")
        print("  - Network/firewall blocking Google's notifications")
        print("  - Google Drive API quota limits")
        print()
        
    except Exception as e:
        print(f"❌ Failed to register webhook: {e}")
        print("\nThis suggests a fundamental issue with:")
        print("  - Service account permissions")
        print("  - API access")
        print("  - Webhook URL accessibility")
        print()

if __name__ == "__main__":
    main()

