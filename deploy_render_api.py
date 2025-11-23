#!/usr/bin/env python3
"""
Render Deployment Script via REST API
Deploys both API and UI services to Render
"""

import requests
import json
import time

API_KEY = "SEH5-JUG1-3T3M-FPL7"
REPO = "https://github.com/JamesJokDutAkuei/MLOP.git"
BASE_URL = "https://api.render.com/v1"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_owner_id():
    """Get the owner ID from the API key"""
    resp = requests.get(f"{BASE_URL}/owners", headers=HEADERS)
    if resp.status_code == 200:
        owners = resp.json()
        if owners:
            return owners[0]['id']
    return None

def create_service(name, dockerfile_path, env_vars):
    """Create a service on Render"""
    print(f"\n📍 Creating {name}...")
    
    owner_id = get_owner_id()
    if not owner_id:
        print(f"❌ Could not get owner ID")
        return None
    
    payload = {
        "type": "web_service",
        "name": name,
        "ownerId": owner_id,
        "repo": REPO,
        "branch": "main",
        "region": "oregon",
        "plan": "free",
        "dockerfile": dockerfile_path,
        "envVars": [{"key": k, "value": v} for k, v in env_vars.items()],
        "autoDeploy": True
    }
    
    resp = requests.post(f"{BASE_URL}/services", json=payload, headers=HEADERS)
    
    if resp.status_code in [200, 201]:
        service = resp.json()
        print(f"✅ {name} created! Service ID: {service.get('id')}")
        return service
    else:
        print(f"❌ Failed to create {name}")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        return None

def main():
    print("🚀 Deploying to Render via API...")
    print(f"📦 Repository: {REPO}")
    print()
    
    # Deploy API
    api_env = {
        "PORT": "8000",
        "PYTHON_UNBUFFERED": "1"
    }
    api_service = create_service("mlop-api", "deploy/Dockerfile.api", api_env)
    
    if api_service:
        api_url = api_service.get('serviceDetails', {}).get('url', 'pending')
        print(f"🔗 API URL: {api_url}")
    else:
        print("⚠️  Could not create API service")
        return
    
    # Wait a bit
    time.sleep(2)
    
    # Deploy UI
    ui_env = {
        "PORT": "8501",
        "STREAMLIT_SERVER_HEADLESS": "true",
        "GCP_API_URL": api_url,
        "DOCKER_ENV": "true"
    }
    ui_service = create_service("mlop-ui", "deploy/Dockerfile.ui", ui_env)
    
    if ui_service:
        ui_url = ui_service.get('serviceDetails', {}).get('url', 'pending')
        print(f"🔗 UI URL: {ui_url}")
    else:
        print("⚠️  Could not create UI service")
        return
    
    print("\n" + "="*60)
    print("✅ DEPLOYMENT INITIATED!")
    print("="*60)
    print("\n📊 Services will start building in ~2-3 minutes")
    print("\n🌐 Check status at: https://dashboard.render.com")
    print("\n💾 Your live URLs:")
    print(f"   🎨 UI: {ui_url}")
    print(f"   📚 API Docs: {api_url}/docs")
    print()

if __name__ == "__main__":
    main()
