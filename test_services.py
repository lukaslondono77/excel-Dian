#!/usr/bin/env python3
"""
Test script for Excel to DIAN services
Run this script to verify all services are working correctly
"""

import requests
import json
import time
from datetime import datetime

# Service URLs
GATEWAY_URL = "http://localhost:8000"
EXCEL_URL = "http://localhost:8001"
PDF_URL = "http://localhost:8002"

# Mock JWT token for testing (generated with the same secret as in docker-compose)
MOCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsIm5hbWUiOiJKb2huIERvZSIsImlhdCI6MTUxNjIzOTAyMn0.30I60qO4HuyGnuV7rKz11mM427u6UMvceAHw2ayVXi0"

def test_health_endpoints():
    """Test health endpoints for all services"""
    print("🔍 Testing health endpoints...")
    
    services = [
        ("Gateway", GATEWAY_URL),
        ("Excel Service", EXCEL_URL),
        ("PDF Service", PDF_URL)
    ]
    
    for name, url in services:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Healthy")
            else:
                print(f"❌ {name}: Unhealthy (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")

def test_gateway_workflow():
    """Test the complete workflow through the gateway"""
    print("\n🔄 Testing gateway workflow...")
    
    # Mock Excel data
    mock_excel_data = {
        "header": ["Account", "Description", "Debit", "Credit", "Balance"],
        "data": [
            ["1100", "Cash", "1000", "", "1000"],
            ["1200", "Accounts Receivable", "500", "", "500"],
            ["1300", "Inventory", "2000", "", "2000"],
            ["2100", "Accounts Payable", "", "1500", "-1500"],
            ["3100", "Capital", "", "2000", "-2000"]
        ],
        "total_rows": 5,
        "columns": 5
    }
    
    try:
        # Test workflow endpoint
        workflow_data = {
            "data": mock_excel_data,
            "file_id": "test-file-123",
            "filename": "test_libro_mayor.xlsx",
            "token": MOCK_TOKEN
        }
        
        response = requests.post(
            f"{GATEWAY_URL}/process_excel_to_pdf",
            json=workflow_data,
            headers={"Authorization": f"Bearer {MOCK_TOKEN}"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Gateway workflow test passed")
            print(f"   - Workflow ID: {result.get('workflow_id', 'N/A')}")
            print(f"   - PDF URL: {result.get('pdf_data', {}).get('pdf_url', 'N/A')}")
        else:
            print(f"❌ Gateway workflow test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Gateway workflow test error: {str(e)}")

def test_workflow_history():
    """Test workflow history endpoint"""
    print("\n📊 Testing workflow history...")
    
    try:
        response = requests.get(
            f"{GATEWAY_URL}/workflow-history",
            headers={"Authorization": f"Bearer {MOCK_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            workflows = result.get('workflows', [])
            print(f"✅ Workflow history test passed - Found {len(workflows)} workflows")
        else:
            print(f"❌ Workflow history test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Workflow history test error: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Excel to DIAN - Service Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Wait a moment for services to be ready
    print("\n⏳ Waiting for services to be ready...")
    time.sleep(5)
    
    # Run tests
    test_health_endpoints()
    test_gateway_workflow()
    test_workflow_history()
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")
    print("\n📝 Next steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Upload an Excel file with accounting data")
    print("3. Generate a DIAN-compliant PDF report")
    print("4. Download and verify the generated PDF")

if __name__ == "__main__":
    main() 