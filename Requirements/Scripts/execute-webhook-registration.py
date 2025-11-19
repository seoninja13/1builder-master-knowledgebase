#!/usr/bin/env python3
"""
Activate and execute the webhook registration workflow in n8n
"""

import requests
import json
import time

N8N_API_URL = "https://n8n.srv972609.hstgr.cloud/api/v1"
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwYWEzZjM5NC00MjU4LTQ1NDQtODQ4OC05NjBkMThiYWNhNmQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzNDMxOTAyfQ.hveLE5837H1WJ3pRnp6pH_NMdsHJoFZnGtIXXTE3J_A"
WORKFLOW_ID = "HQk08RRZe1MeuzlP"

headers = {
    'X-N8N-API-KEY': N8N_API_KEY,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def activate_workflow():
    """Activate the workflow"""
    print("Activating workflow...")
    
    url = f"{N8N_API_URL}/workflows/{WORKFLOW_ID}"
    response = requests.patch(url, headers=headers, json={"active": True})
    
    if response.status_code == 200:
        print("✅ Workflow activated\n")
        return True
    else:
        print(f"❌ Failed to activate: {response.status_code}")
        print(f"   Response: {response.text}\n")
        return False

def execute_workflow():
    """Execute the workflow manually"""
    print("Executing workflow...")
    
    url = f"{N8N_API_URL}/workflows/{WORKFLOW_ID}/execute"
    response = requests.post(url, headers=headers, json={})
    
    if response.status_code in [200, 201]:
        data = response.json()
        execution_id = data.get('data', {}).get('executionId')
        print(f"✅ Workflow executed! Execution ID: {execution_id}\n")
        return execution_id
    else:
        print(f"❌ Failed to execute: {response.status_code}")
        print(f"   Response: {response.text}\n")
        return None

def get_execution_result(execution_id):
    """Get the execution result"""
    print(f"Fetching execution result...")
    
    # Wait a bit for execution to complete
    time.sleep(3)
    
    url = f"{N8N_API_URL}/executions/{execution_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check if execution finished
        finished = data.get('data', {}).get('finished', False)
        status = data.get('data', {}).get('status', 'unknown')
        
        print(f"Status: {status}")
        print(f"Finished: {finished}\n")
        
        if finished and status == 'success':
            # Extract the webhook registration response
            result_data = data.get('data', {}).get('resultData', {})
            run_data = result_data.get('runData', {})
            
            # Get the Register Webhook node output
            if 'Register Webhook' in run_data:
                webhook_data = run_data['Register Webhook'][0]['data']['main'][0][0]['json']
                
                print("="*70)
                print("WEBHOOK REGISTERED SUCCESSFULLY!")
                print("="*70 + "\n")
                print(f"Channel ID: {webhook_data.get('id')}")
                print(f"Resource ID: {webhook_data.get('resourceId')}")
                print(f"Resource URI: {webhook_data.get('resourceUri')}")
                print(f"Expiration: {webhook_data.get('expiration')}\n")
                
                # Get the pageToken from Get Page Token node
                if 'Get Page Token' in run_data:
                    page_token_data = run_data['Get Page Token'][0]['data']['main'][0][0]['json']
                    page_token = page_token_data.get('startPageToken')
                    print(f"Page Token: {page_token}\n")
                    
                    print("NEXT STEPS:")
                    print(f"1. Update the main webhook workflow pageToken to: {page_token}")
                    print("2. Upload a test file to Google Drive")
                    print("3. Check n8n executions within 1-2 minutes")
                    print("4. You should see a NEW execution with actual file data!\n")
                    
                    return {
                        'channelId': webhook_data.get('id'),
                        'resourceId': webhook_data.get('resourceId'),
                        'pageToken': page_token
                    }
            else:
                print("⚠️  Could not find webhook registration data in execution")
                print(f"Available nodes: {list(run_data.keys())}\n")
        else:
            print(f"❌ Execution failed or not finished")
            print(f"   Full response: {json.dumps(data, indent=2)}\n")
    else:
        print(f"❌ Failed to get execution: {response.status_code}")
        print(f"   Response: {response.text}\n")
    
    return None

def main():
    print("\n" + "="*70)
    print("EXECUTE WEBHOOK REGISTRATION WORKFLOW")
    print("="*70 + "\n")
    
    # Activate workflow
    if not activate_workflow():
        return
    
    # Execute workflow
    execution_id = execute_workflow()
    if not execution_id:
        return
    
    # Get result
    result = get_execution_result(execution_id)
    
    if result:
        # Save to files
        from pathlib import Path
        import datetime
        
        channel_file = Path(__file__).parent.parent / "Credentials" / "drive-webhook-channel.json"
        page_token_file = Path(__file__).parent.parent / "Credentials" / "drive-page-token.json"
        
        channel_data = {
            'channelId': result['channelId'],
            'resourceId': result['resourceId'],
            'pageToken': result['pageToken'],
            'webhookUrl': 'https://n8n.srv972609.hstgr.cloud/webhook/drive-notifications',
            'registeredAt': datetime.datetime.now().isoformat(),
            'authType': 'oauth_user'
        }
        
        with open(channel_file, 'w') as f:
            json.dump(channel_data, f, indent=2)
        
        with open(page_token_file, 'w') as f:
            json.dump({
                'pageToken': result['pageToken'],
                'updatedAt': datetime.datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"✅ Saved configuration files\n")

if __name__ == "__main__":
    main()

