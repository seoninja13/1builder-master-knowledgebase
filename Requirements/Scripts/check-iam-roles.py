#!/usr/bin/env python3
"""
Check IAM roles assigned to the service account
"""

import json
from pathlib import Path

def load_service_account():
    """Load service account data"""
    key_path = Path(__file__).parent.parent / "Credentials" / "builder-master-knowldgebase-79a4f60f66e1.json"
    with open(key_path, 'r') as f:
        return json.load(f)

def check_iam_roles():
    """Check IAM roles for the service account"""
    sa_data = load_service_account()
    project_id = sa_data['project_id']
    sa_email = sa_data['client_email']
    
    print("=" * 70)
    print("IAM Roles Check")
    print("=" * 70)
    print(f"Project: {project_id}")
    print(f"Service Account: {sa_email}")
    print("=" * 70)
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        
        # Authenticate
        credentials = service_account.Credentials.from_service_account_info(
            sa_data,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        credentials.refresh(Request())
        
        # Get IAM policy
        service = build('cloudresourcemanager', 'v1', credentials=credentials)
        policy = service.projects().getIamPolicy(
            resource=project_id,
            body={}
        ).execute()
        
        # Find roles for this service account
        sa_roles = []
        for binding in policy.get('bindings', []):
            members = binding.get('members', [])
            sa_member = f"serviceAccount:{sa_email}"
            if sa_member in members:
                sa_roles.append(binding['role'])
        
        print("\n✅ Current IAM Roles:")
        if sa_roles:
            for role in sa_roles:
                print(f"  - {role}")
        else:
            print("  ⚠️  No roles found (may need to check manually)")
        
        # Recommended roles for RAG project
        print("\n📋 Recommended Roles for RAG Project:")
        recommended = [
            "roles/drive.file",  # Access to Drive files
            "roles/aiplatform.user",  # Vertex AI / Gemini access
            "roles/serviceusage.serviceUsageConsumer",  # API usage
        ]
        
        for role in recommended:
            status = "✅" if role in sa_roles else "❌"
            print(f"  {status} {role}")
        
        print("\n" + "=" * 70)
        print("To add missing roles, run:")
        print("=" * 70)
        for role in recommended:
            if role not in sa_roles:
                print(f"gcloud projects add-iam-policy-binding {project_id} \\")
                print(f"  --member='serviceAccount:{sa_email}' \\")
                print(f"  --role='{role}'")
                print()
    
    except ImportError:
        print("❌ Required libraries not installed")
        print("Run: pip install google-api-python-client")
    except Exception as e:
        print(f"❌ Error checking IAM roles: {e}")
        print("\nManual check required:")
        print(f"1. Go to: https://console.cloud.google.com/iam-admin/iam?project={project_id}")
        print(f"2. Find: {sa_email}")
        print("3. Verify it has these roles:")
        print("   - Drive File Access (roles/drive.file)")
        print("   - Vertex AI User (roles/aiplatform.user)")
        print("   - Service Usage Consumer (roles/serviceusage.serviceUsageConsumer)")

if __name__ == "__main__":
    check_iam_roles()

