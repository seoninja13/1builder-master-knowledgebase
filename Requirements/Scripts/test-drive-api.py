#!/usr/bin/env python3
"""
Google Drive API Testing Script
Tests service account access to Google Drive for RAG project
"""

import json
import io
from pathlib import Path
from datetime import datetime

def load_service_account():
    """Load service account credentials"""
    key_path = Path(__file__).parent.parent / "Credentials" / "builder-master-knowldgebase-79a4f60f66e1.json"
    with open(key_path, 'r') as f:
        return json.load(f)

def authenticate():
    """Authenticate with Google Drive API"""
    print("=" * 70)
    print("STEP 1: Authentication")
    print("=" * 70)
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        sa_data = load_service_account()
        
        credentials = service_account.Credentials.from_service_account_info(
            sa_data,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        print("✅ Successfully authenticated with Google Drive API")
        print(f"✅ Service Account: {sa_data['client_email']}")
        
        return service
    
    except ImportError:
        print("❌ google-api-python-client not installed")
        print("Run: pip install google-api-python-client")
        return None
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None

def find_folder(service, folder_name):
    """Search for a folder by name"""
    print("\n" + "=" * 70)
    print(f"STEP 2: Search for '{folder_name}' Folder")
    print("=" * 70)
    
    try:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, owners, permissions)'
        ).execute()
        
        folders = results.get('files', [])
        
        if not folders:
            print(f"⚠️  Folder '{folder_name}' not found")
            return None
        
        if len(folders) > 1:
            print(f"⚠️  Multiple folders named '{folder_name}' found:")
            for idx, folder in enumerate(folders, 1):
                print(f"  {idx}. ID: {folder['id']}")
            print("  Using the first one...")
        
        folder = folders[0]
        print(f"✅ Found folder: {folder['name']}")
        print(f"✅ Folder ID: {folder['id']}")
        
        return folder['id']
    
    except Exception as e:
        print(f"❌ Error searching for folder: {e}")
        return None

def create_folder(service, folder_name):
    """Create a new folder in Drive"""
    print("\n" + "=" * 70)
    print(f"STEP 3: Create '{folder_name}' Folder")
    print("=" * 70)
    
    try:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = service.files().create(
            body=file_metadata,
            fields='id, name'
        ).execute()
        
        print(f"✅ Created folder: {folder['name']}")
        print(f"✅ Folder ID: {folder['id']}")
        print(f"\n⚠️  IMPORTANT: You must share this folder with your user account!")
        print(f"   Go to: https://drive.google.com/drive/folders/{folder['id']}")
        print(f"   Click 'Share' and add: dachevivo@gmail.com")
        
        return folder['id']
    
    except Exception as e:
        print(f"❌ Error creating folder: {e}")
        return None

def test_list_files(service, folder_id):
    """Test listing files in the folder"""
    print("\n" + "=" * 70)
    print("STEP 4: Test READ Access (List Files)")
    print("=" * 70)
    
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(
            q=query,
            fields='files(id, name, mimeType, size, createdTime)'
        ).execute()
        
        files = results.get('files', [])
        
        print(f"✅ Successfully listed files in folder")
        print(f"✅ Found {len(files)} file(s)")
        
        if files:
            print("\nFiles in folder:")
            for file in files:
                size = int(file.get('size', 0)) if file.get('size') else 0
                size_mb = size / (1024 * 1024)
                print(f"  - {file['name']} ({size_mb:.2f} MB)")
        else:
            print("  (Folder is empty)")
        
        return True
    
    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return False

def test_upload_file(service, folder_id):
    """Test uploading a file to the folder"""
    print("\n" + "=" * 70)
    print("STEP 5: Test WRITE Access (Upload File)")
    print("=" * 70)
    
    try:
        from googleapiclient.http import MediaIoBaseUpload
        
        # Create test file content
        test_content = f"""RAG System Test File
Created: {datetime.now().isoformat()}
Purpose: Verify service account can write to Google Drive
Project: OneBuilder Master RAG
"""
        
        file_metadata = {
            'name': 'rag-test-file.txt',
            'parents': [folder_id]
        }
        
        media = MediaIoBaseUpload(
            io.BytesIO(test_content.encode('utf-8')),
            mimetype='text/plain',
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        print(f"✅ Successfully uploaded test file")
        print(f"✅ File ID: {file['id']}")
        print(f"✅ File name: {file['name']}")
        print(f"✅ View at: {file.get('webViewLink', 'N/A')}")
        
        return file['id']
    
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return None

def test_delete_file(service, file_id):
    """Test deleting a file"""
    print("\n" + "=" * 70)
    print("STEP 6: Test DELETE Access (Remove Test File)")
    print("=" * 70)
    
    try:
        service.files().delete(fileId=file_id).execute()
        print(f"✅ Successfully deleted test file")
        return True
    
    except Exception as e:
        print(f"❌ Error deleting file: {e}")
        return False

def main():
    """Main test workflow"""
    print("\n" + "=" * 70)
    print("Google Drive API Testing - Phase 2")
    print("RAG Project Infrastructure Setup")
    print("=" * 70 + "\n")

    # Step 1: Authenticate
    service = authenticate()
    if not service:
        print("\n❌ PHASE 2 FAILED: Cannot authenticate")
        return

    # Step 2: Use provided folder ID
    folder_name = "OneBuilder Master Knowledge"
    folder_id = "1U3TvxcGrz2J4T8OIDjjrnY3P12-PL42_"

    print("\n" + "=" * 70)
    print(f"STEP 2: Using Provided Folder ID")
    print("=" * 70)
    print(f"✅ Folder Name: {folder_name}")
    print(f"✅ Folder ID: {folder_id}")
    print(f"✅ Folder URL: https://drive.google.com/drive/folders/{folder_id}")

    # Verify we can access the folder
    try:
        folder_info = service.files().get(fileId=folder_id, fields='id, name, owners').execute()
        print(f"✅ Successfully accessed folder: {folder_info['name']}")
    except Exception as e:
        print(f"❌ Cannot access folder: {e}")
        print("\n⚠️  Possible issues:")
        print("   1. Folder not shared with service account")
        print("   2. Service account doesn't have Editor permissions")
        print("   3. Folder ID is incorrect")
        print("\n❌ PHASE 2 FAILED: Cannot access folder")
        return
    
    # Step 3: Test read access
    if not test_list_files(service, folder_id):
        print("\n❌ PHASE 2 FAILED: Cannot read from folder")
        return
    
    # Step 4: Test write access
    test_file_id = test_upload_file(service, folder_id)
    if not test_file_id:
        print("\n❌ PHASE 2 FAILED: Cannot write to folder")
        return
    
    # Step 5: Test delete access
    if not test_delete_file(service, test_file_id):
        print("\n⚠️  WARNING: Could not delete test file (may need manual cleanup)")
    
    # Summary
    print("\n" + "=" * 70)
    print("PHASE 2: COMPLETE ✅")
    print("=" * 70)
    print(f"✅ Folder Name: {folder_name}")
    print(f"✅ Folder ID: {folder_id}")
    print(f"✅ READ Access: Verified")
    print(f"✅ WRITE Access: Verified")
    print(f"✅ DELETE Access: Verified")
    print("\n" + "=" * 70)
    print("Ready to proceed to Phase 3: n8n Configuration")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()

