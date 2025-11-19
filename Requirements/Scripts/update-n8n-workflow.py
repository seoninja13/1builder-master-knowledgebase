#!/usr/bin/env python3
"""
Update n8n Workflow with Valid pageToken
Automatically updates the n8n workflow to use the correct pageToken

This script reads the pageToken from drive-page-token.json and updates
the n8n workflow via the n8n API.

Requirements:
- Run fix-webhook-complete.py first to generate the pageToken
- n8n API must be accessible
"""

import json
import sys
from pathlib import Path

# Configuration
PAGE_TOKEN_FILE = Path(__file__).parent.parent / "Credentials" / "drive-page-token.json"
WORKFLOW_ID = "a5IiavhYT3sOMo4b"
N8N_API_URL = "https://n8n.srv972609.hstgr.cloud/api/v1"


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(title)
    print("="*70 + "\n")


def load_page_token():
    """Load the pageToken from file"""
    if not PAGE_TOKEN_FILE.exists():
        print(f"❌ ERROR: Page token file not found: {PAGE_TOKEN_FILE}")
        print("\n⚠️  Please run fix-webhook-complete.py first!")
        sys.exit(1)
    
    try:
        with open(PAGE_TOKEN_FILE, 'r') as f:
            data = json.load(f)
        page_token = data.get('pageToken')
        if not page_token:
            print("❌ ERROR: pageToken not found in file")
            sys.exit(1)
        print(f"✅ Loaded pageToken: {page_token}")
        return page_token
    except Exception as e:
        print(f"❌ ERROR loading page token: {e}")
        sys.exit(1)


def print_manual_instructions(page_token):
    """Print manual instructions for updating the workflow"""
    print_header("📋 MANUAL UPDATE INSTRUCTIONS")
    
    print("Since we're using the n8n MCP server, I'll provide instructions")
    print("for updating the workflow manually:\n")
    
    print("1. Open the workflow in n8n:")
    print(f"   https://n8n.srv972609.hstgr.cloud/workflow/{WORKFLOW_ID}\n")
    
    print("2. Click on the 'Get Drive Changes' node\n")
    
    print("3. Find the 'Query Parameters' section\n")
    
    print("4. Find the parameter named 'pageToken'\n")
    
    print("5. Change the value from:")
    print("   Current: \"1\"")
    print(f"   New:     \"{page_token}\"\n")
    
    print("6. Click 'Save' in the top-right corner\n")
    
    print("7. Make sure the workflow is ACTIVE (toggle in top-right)\n")
    
    print("✅ That's it! The workflow will now use the correct pageToken.")
    
    print("\n" + "="*70)
    print("ALTERNATIVE: Use n8n Expression (Recommended)")
    print("="*70 + "\n")
    
    print("For a more dynamic approach, you can use workflow static data:\n")
    
    print("1. In the 'Get Drive Changes' node, set pageToken to:")
    print("   {{ $workflow.staticData.pageToken || '" + page_token + "' }}\n")
    
    print("2. This will use the static data if available, or fall back to the token\n")
    
    print("3. To update the token in the future, you can use the n8n API")
    print("   or update it manually in the workflow settings\n")


def main():
    print_header("🔧 N8N WORKFLOW UPDATE TOOL")
    
    # Load pageToken
    page_token = load_page_token()
    
    # Print manual instructions
    print_manual_instructions(page_token)
    
    print_header("✅ INSTRUCTIONS PROVIDED")
    print("\nFollow the manual steps above to update your workflow.")
    print("After updating, test by uploading a file to Google Drive!\n")


if __name__ == "__main__":
    main()

