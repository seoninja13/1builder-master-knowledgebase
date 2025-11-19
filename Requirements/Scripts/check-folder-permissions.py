#!/usr/bin/env python3
"""
Check if the service account has proper access to the Google Drive folder
"""

import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configuration
SERVICE_ACCOUNT_FILE = Path(__file__).parent.parent / "Credentials" / "builder-master-knowldgebase-79a4f60f66e1.json"
FOLDER_ID = "1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def main():
    print("\n" + "="*70)
    print("SERVICE ACCOUNT FOLDER ACCESS CHECK")
    print("="*70 + "\n")
    
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
    
    # Try to get folder metadata
    print("1. Checking folder access...")
    try:
        folder = service.files().get(
            fileId=FOLDER_ID,
            fields='id,name,permissions,owners'
        ).execute()
        
        print(f"✅ Can access folder: {folder.get('name')}")
        print(f"   Folder ID: {folder.get('id')}\n")
        
    except Exception as e:
        print(f"❌ CANNOT access folder!")
        print(f"   Error: {e}\n")
        print("This is likely the issue! The service account needs:")
        print("  1. To be added as a viewer/editor to the folder")
        print("  2. Or the folder needs to be shared with the service account\n")
        return
    
    # Try to list files in the folder
    print("2. Checking if we can list files in the folder...")
    try:
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents",
            fields='files(id,name,mimeType,modifiedTime)',
            pageSize=10
        ).execute()
        
        files = results.get('files', [])
        print(f"✅ Can list files: Found {len(files)} files\n")
        
        if files:
            print("Recent files:")
            for f in files[:5]:
                print(f"  - {f.get('name')} (modified: {f.get('modifiedTime')})")
            print()
        else:
            print("⚠️  No files found in folder\n")
            
    except Exception as e:
        print(f"❌ CANNOT list files!")
        print(f"   Error: {e}\n")
    
    # Check permissions
    print("3. Checking folder permissions...")
    try:
        permissions = service.permissions().list(
            fileId=FOLDER_ID,
            fields='permissions(id,type,role,emailAddress)'
        ).execute()
        
        perms = permissions.get('permissions', [])
        print(f"✅ Found {len(perms)} permission entries:\n")
        
        service_account_has_access = False
        for perm in perms:
            email = perm.get('emailAddress', 'N/A')
            role = perm.get('role', 'N/A')
            perm_type = perm.get('type', 'N/A')
            
            print(f"  - {perm_type}: {email} ({role})")
            
            if email == service_account_email:
                service_account_has_access = True
                print(f"    ✅ SERVICE ACCOUNT HAS ACCESS!")
        
        print()
        
        if not service_account_has_access:
            print("❌ SERVICE ACCOUNT NOT IN PERMISSIONS LIST!")
            print("\nThis is the problem! To fix:")
            print(f"1. Open: https://drive.google.com/drive/folders/{FOLDER_ID}")
            print("2. Right-click → Share")
            print(f"3. Add: {service_account_email}")
            print("4. Give 'Viewer' or 'Editor' access")
            print("5. Click 'Send'\n")
            
    except Exception as e:
        print(f"⚠️  Could not check permissions: {e}")
        print("   (This is normal if you don't have permission to view permissions)\n")
    
    print("="*70)
    print("SUMMARY")
    print("="*70 + "\n")
    print("If the service account CAN access the folder and list files,")
    print("then the webhook SHOULD work for new file uploads.\n")
    print("If the service account CANNOT access the folder,")
    print("you need to share the folder with the service account.\n")

if __name__ == "__main__":
    main()

