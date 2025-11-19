#!/usr/bin/env python3
"""
Google Cloud Platform Setup Verification Script
Verifies service account authentication and API enablement for RAG project
"""

import json
import os
import sys
from pathlib import Path

def load_service_account():
    """Load and validate service account JSON key file"""
    key_path = Path(__file__).parent.parent / "Credentials" / "builder-master-knowldgebase-79a4f60f66e1.json"
    
    print("=" * 70)
    print("STEP 1: Service Account Verification")
    print("=" * 70)
    
    if not key_path.exists():
        print(f"❌ ERROR: Service account key file not found at: {key_path}")
        return None
    
    print(f"✅ Service account key file found: {key_path}")
    
    try:
        with open(key_path, 'r') as f:
            sa_data = json.load(f)
        
        # Validate required fields
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in sa_data]
        
        if missing_fields:
            print(f"❌ ERROR: Missing required fields: {missing_fields}")
            return None
        
        print(f"✅ Service account type: {sa_data['type']}")
        print(f"✅ Project ID: {sa_data['project_id']}")
        print(f"✅ Client email: {sa_data['client_email']}")
        print(f"✅ Private key present: {len(sa_data['private_key'])} characters")
        
        return sa_data
    
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in service account file: {e}")
        return None
    except Exception as e:
        print(f"❌ ERROR: Failed to load service account: {e}")
        return None

def check_google_auth_library():
    """Check if google-auth library is installed"""
    print("\n" + "=" * 70)
    print("STEP 2: Python Dependencies Check")
    print("=" * 70)
    
    try:
        import google.auth
        from google.auth import credentials
        from google.auth.transport.requests import Request
        print("✅ google-auth library is installed")
        return True
    except ImportError:
        print("❌ google-auth library is NOT installed")
        print("\nTo install, run:")
        print("  pip install google-auth google-auth-oauthlib google-auth-httplib2")
        return False

def test_authentication(sa_data):
    """Test authentication with service account"""
    print("\n" + "=" * 70)
    print("STEP 3: Authentication Test")
    print("=" * 70)
    
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
        
        # Create credentials from service account
        credentials = service_account.Credentials.from_service_account_info(
            sa_data,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        print("✅ Credentials object created successfully")
        
        # Test token refresh
        credentials.refresh(Request())
        print("✅ Successfully authenticated with Google Cloud")
        print(f"✅ Token expiry: {credentials.expiry}")
        
        return credentials
    
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None

def check_enabled_apis(credentials, project_id):
    """Check which APIs are enabled in the project"""
    print("\n" + "=" * 70)
    print("STEP 4: Enabled APIs Check")
    print("=" * 70)
    
    try:
        from googleapiclient.discovery import build
        
        service = build('serviceusage', 'v1', credentials=credentials)
        
        # List of APIs we need for the RAG project
        required_apis = [
            'drive.googleapis.com',           # Google Drive API
            'generativelanguage.googleapis.com',  # Gemini API
            'aiplatform.googleapis.com',      # Vertex AI (alternative for Gemini)
        ]
        
        print(f"\nChecking APIs for project: {project_id}\n")
        
        results = {}
        for api in required_apis:
            try:
                resource_name = f"projects/{project_id}/services/{api}"
                result = service.services().get(name=resource_name).execute()
                
                state = result.get('state', 'UNKNOWN')
                if state == 'ENABLED':
                    print(f"✅ {api}: ENABLED")
                    results[api] = True
                else:
                    print(f"❌ {api}: {state}")
                    results[api] = False
            
            except Exception as e:
                print(f"⚠️  {api}: Unable to check (may not be enabled or no permission)")
                results[api] = None
        
        return results
    
    except ImportError:
        print("❌ google-api-python-client library is NOT installed")
        print("\nTo install, run:")
        print("  pip install google-api-python-client")
        return None
    except Exception as e:
        print(f"❌ Failed to check APIs: {e}")
        return None

def main():
    """Main verification workflow"""
    print("\n" + "=" * 70)
    print("Google Cloud Platform Setup Verification")
    print("RAG Project - Phase 1")
    print("=" * 70 + "\n")
    
    # Step 1: Load service account
    sa_data = load_service_account()
    if not sa_data:
        print("\n❌ VERIFICATION FAILED: Cannot proceed without valid service account")
        sys.exit(1)
    
    # Step 2: Check dependencies
    if not check_google_auth_library():
        print("\n⚠️  VERIFICATION INCOMPLETE: Install required libraries and re-run")
        sys.exit(1)
    
    # Step 3: Test authentication
    credentials = test_authentication(sa_data)
    if not credentials:
        print("\n❌ VERIFICATION FAILED: Authentication unsuccessful")
        sys.exit(1)
    
    # Step 4: Check enabled APIs
    api_results = check_enabled_apis(credentials, sa_data['project_id'])
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print("✅ Service account key file: VALID")
    print("✅ Authentication: SUCCESS")
    
    if api_results:
        enabled_count = sum(1 for v in api_results.values() if v is True)
        print(f"✅ Enabled APIs: {enabled_count}/{len(api_results)}")
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("1. If any APIs are disabled, enable them in Google Cloud Console")
    print("2. Verify service account has necessary IAM roles")
    print("3. Proceed to Phase 2: n8n Configuration")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()

