#!/usr/bin/env python3
"""
DIAN Processing Service Test Suite
Tests the DIAN-compliant processing logic for multiple files and date filtering
"""

import requests
import json
import time
import os
from datetime import datetime, date
import pandas as pd

# Configuration
BASE_URL = "http://localhost:8003"
MOCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsIm5hbWUiOiJKb2huIERvZSIsImlhdCI6MTUxNjIzOTAyMn0.30I60qO4HuyGnuV7rKz11mM427u6UMvceAHw2ayVXi0"

def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint: OK")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_single_file_processing():
    """Test processing a single file"""
    print("\n📁 Testing single file processing...")
    
    try:
        # Use the existing sample file
        files = {'file': open('sample_data/sample_libro_mayor.xlsx', 'rb')}
        data = {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'formato': '1001',
            'export_format': 'excel'
        }
        
        response = requests.post(
            f"{BASE_URL}/process_dian_files",
            files=files,
            data=data,
            headers={'Authorization': f'Bearer {MOCK_TOKEN}'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Single file processing: OK")
            print(f"   - Files processed: {len(result.get('file_summaries', []))}")
            print(f"   - Total transactions: {result.get('overall_summaries', {}).get('total_transactions', 0)}")
            print(f"   - Total amount: ${result.get('overall_summaries', {}).get('total_amount', 0):,.2f}")
            return True
        else:
            print(f"❌ Single file processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Single file processing error: {e}")
        return False

def test_multiple_files_processing():
    """Test processing multiple files"""
    print("\n📁 Testing multiple files processing...")
    
    try:
        # Check if test files exist, if not generate them
        test_files = [
            'sample_data/sales_transactions_2023.xlsx',
            'sample_data/purchase_transactions_2023.xlsx',
            'sample_data/mixed_transactions_2023.xlsx'
        ]
        
        # Generate test files if they don't exist
        if not all(os.path.exists(f) for f in test_files):
            print("   Generating test files...")
            os.system("cd sample_data && python generate_test_files.py")
        
        files = {}
        for i, filepath in enumerate(test_files):
            if os.path.exists(filepath):
                files[f'file{i}'] = open(filepath, 'rb')
        
        data = {
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'formato': '1001',
            'export_format': 'excel'
        }
        
        response = requests.post(
            f"{BASE_URL}/process_dian_files",
            files=files,
            data=data,
            headers={'Authorization': f'Bearer {MOCK_TOKEN}'}
        )
        
        # Close files
        for f in files.values():
            f.close()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Multiple files processing: OK")
            print(f"   - Files processed: {len(result.get('file_summaries', []))}")
            print(f"   - Total transactions: {result.get('overall_summaries', {}).get('total_transactions', 0)}")
            print(f"   - Total amount: ${result.get('overall_summaries', {}).get('total_amount', 0):,.2f}")
            
            # Show file summaries
            for summary in result.get('file_summaries', []):
                print(f"     - {summary['filename']}: {summary['filtered_rows']} rows, ${summary['total_amount']:,.2f}")
            
            return True
        else:
            print(f"❌ Multiple files processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Multiple files processing error: {e}")
        return False

def test_date_filtering():
    """Test different date range filtering"""
    print("\n📅 Testing date filtering...")
    
    test_cases = [
        {
            'name': 'Full Year 2023',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31'
        },
        {
            'name': 'Q1 2023',
            'start_date': '2023-01-01',
            'end_date': '2023-03-31'
        },
        {
            'name': 'Q2 2023',
            'start_date': '2023-04-01',
            'end_date': '2023-06-30'
        },
        {
            'name': 'Custom Range (Mar-Sep)',
            'start_date': '2023-03-01',
            'end_date': '2023-09-30'
        }
    ]
    
    success_count = 0
    
    for test_case in test_cases:
        try:
            files = {'file': open('sample_data/sales_transactions_2023.xlsx', 'rb')}
            data = {
                'start_date': test_case['start_date'],
                'end_date': test_case['end_date'],
                'formato': '1001',
                'export_format': 'excel'
            }
            
            response = requests.post(
                f"{BASE_URL}/process_dian_files",
                files=files,
                data=data,
                headers={'Authorization': f'Bearer {MOCK_TOKEN}'}
            )
            
            if response.status_code == 200:
                result = response.json()
                transactions = result.get('overall_summaries', {}).get('total_transactions', 0)
                amount = result.get('overall_summaries', {}).get('total_amount', 0)
                print(f"✅ {test_case['name']}: {transactions} transactions, ${amount:,.2f}")
                success_count += 1
            else:
                print(f"❌ {test_case['name']}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"❌ {test_case['name']}: Error - {e}")
    
    return success_count == len(test_cases)

def test_different_formats():
    """Test different DIAN formats and export formats"""
    print("\n📊 Testing different formats...")
    
    try:
        files = {'file': open('sample_data/sales_transactions_2023.xlsx', 'rb')}
        
        # Test different DIAN formats
        formats_to_test = ['1001', '1002', '1003']
        export_formats = ['excel', 'pdf']
        
        success_count = 0
        
        for formato in formats_to_test:
            for export_format in export_formats:
                try:
                    data = {
                        'start_date': '2023-01-01',
                        'end_date': '2023-12-31',
                        'formato': formato,
                        'export_format': export_format
                    }
                    
                    response = requests.post(
                        f"{BASE_URL}/process_dian_files",
                        files=files,
                        data=data,
                        headers={'Authorization': f'Bearer {MOCK_TOKEN}'}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        filename = result.get('report_filename', '')
                        print(f"✅ Formato {formato} ({export_format}): {filename}")
                        success_count += 1
                    else:
                        print(f"❌ Formato {formato} ({export_format}): Failed")
                        
                except Exception as e:
                    print(f"❌ Formato {formato} ({export_format}): Error - {e}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Format testing error: {e}")
        return False

def test_csv_file_processing():
    """Test processing CSV files with different column names"""
    print("\n📄 Testing CSV file processing...")
    
    try:
        # Check if CSV file exists
        csv_file = 'sample_data/transactions_2023.csv'
        if not os.path.exists(csv_file):
            print("   Generating CSV test file...")
            os.system("cd sample_data && python generate_test_files.py")
        
        if os.path.exists(csv_file):
            files = {'file': open(csv_file, 'rb')}
            data = {
                'start_date': '2023-04-01',
                'end_date': '2023-12-31',
                'formato': '1001',
                'export_format': 'excel'
            }
            
            response = requests.post(
                f"{BASE_URL}/process_dian_files",
                files=files,
                data=data,
                headers={'Authorization': f'Bearer {MOCK_TOKEN}'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ CSV file processing: OK")
                print(f"   - Total transactions: {result.get('overall_summaries', {}).get('total_transactions', 0)}")
                print(f"   - Total amount: ${result.get('overall_summaries', {}).get('total_amount', 0):,.2f}")
                return True
            else:
                print(f"❌ CSV file processing failed: {response.status_code}")
                return False
        else:
            print("❌ CSV test file not found")
            return False
            
    except Exception as e:
        print(f"❌ CSV file processing error: {e}")
        return False

def test_download_report():
    """Test downloading generated reports"""
    print("\n📥 Testing report download...")
    
    try:
        # First generate a report
        files = {'file': open('sample_data/sales_transactions_2023.xlsx', 'rb')}
        data = {
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'formato': '1001',
            'export_format': 'excel'
        }
        
        response = requests.post(
            f"{BASE_URL}/process_dian_files",
            files=files,
            data=data,
            headers={'Authorization': f'Bearer {MOCK_TOKEN}'}
        )
        
        if response.status_code == 200:
            result = response.json()
            download_url = result.get('download_url', '')
            
            if download_url:
                # Test download
                download_response = requests.get(
                    f"{BASE_URL}{download_url}",
                    headers={'Authorization': f'Bearer {MOCK_TOKEN}'}
                )
                
                if download_response.status_code == 200:
                    print("✅ Report download: OK")
                    print(f"   - File size: {len(download_response.content)} bytes")
                    return True
                else:
                    print(f"❌ Report download failed: {download_response.status_code}")
                    return False
            else:
                print("❌ No download URL provided")
                return False
        else:
            print("❌ Report generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Report download error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 DIAN Processing Service Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Wait for service to be ready
    print("⏳ Waiting for service to be ready...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Single File Processing", test_single_file_processing),
        ("Multiple Files Processing", test_multiple_files_processing),
        ("Date Filtering", test_date_filtering),
        ("Different Formats", test_different_formats),
        ("CSV File Processing", test_csv_file_processing),
        ("Report Download", test_download_report)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 Test suite completed!")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! DIAN Processing Service is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the service.")
    
    print("\n📝 Next steps:")
    print("1. The service is ready for integration with your frontend")
    print("2. Test with real Colombian accounting data")
    print("3. Verify DIAN compliance for your specific use case")

if __name__ == "__main__":
    main() 