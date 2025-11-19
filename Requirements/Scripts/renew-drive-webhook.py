#!/usr/bin/env python3
"""
Google Drive Push Notification Webhook Renewal Script
Renews an existing push notification channel before it expires

Project: 1BuilderRAG
Usage: python renew-drive-webhook.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from register_drive_webhook import load_service_account, register_webhook, stop_webhook


def load_channel_info():
    """Load existing channel information"""
    channel_file = Path(__file__).parent.parent / "Credentials" / "drive-webhook-channel.json"
    
    if not channel_file.exists():
        print(f"❌ ERROR: Channel info file not found: {channel_file}")
        print("Run register-drive-webhook.py first to create a channel.")
        sys.exit(1)
    
    try:
        with open(channel_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ ERROR loading channel info: {e}")
        sys.exit(1)


def check_expiration(channel_info):
    """Check if channel is expiring soon"""
    expiration_ms = int(channel_info['expiration'])
    expiration_dt = datetime.fromtimestamp(expiration_ms / 1000)
    now = datetime.now()
    time_remaining = expiration_dt - now
    
    print("\n" + "="*70)
    print("CHANNEL EXPIRATION CHECK")
    print("="*70)
    print(f"Channel ID: {channel_info['channel_id']}")
    print(f"Expiration: {expiration_dt.isoformat()}")
    print(f"Time Remaining: {time_remaining}")
    print("="*70 + "\n")
    
    # Renew if less than 24 hours remaining
    if time_remaining.total_seconds() < 86400:  # 24 hours
        print("⚠️  Channel expires in less than 24 hours. Renewing...")
        return True
    else:
        print("✅ Channel is still valid. No renewal needed.")
        return False


def renew_channel():
    """Renew the push notification channel"""
    print("\n" + "="*70)
    print("1BUILDERRAG - GOOGLE DRIVE WEBHOOK RENEWAL")
    print("="*70 + "\n")
    
    # Load existing channel info
    channel_info = load_channel_info()
    
    # Check if renewal is needed
    if not check_expiration(channel_info):
        return
    
    # Load credentials
    credentials = load_service_account()
    
    # Stop old channel
    print("\nStopping old channel...")
    stop_webhook(channel_info['channel_id'], channel_info['resource_id'])
    
    # Register new channel
    print("\nRegistering new channel...")
    register_webhook(credentials)
    
    print("\n✅ CHANNEL RENEWED SUCCESSFULLY!")


def main():
    """Main execution"""
    try:
        renew_channel()
    except KeyboardInterrupt:
        print("\n\n⚠️  Renewal cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

