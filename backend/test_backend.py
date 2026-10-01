import os
import sys

# Add backend directory to sys.path
backend_dir = r"C:\Users\samee\.gemini\antigravity\scratch\billing-system\backend"
sys.path.insert(0, backend_dir)

from app import app, init_db
from models import db, User, Bill

def run_tests():
    print("Testing Backend API & Database...")
    with app.app_context():
        init_db()

        client = app.test_client()

        # 1. Test Login with seeded admin
        login_res = client.post('/api/login', json={'username': 'admin', 'password': 'admin123'})
        print(f"Login Response [{login_res.status_code}]:", login_res.get_json())
        assert login_res.status_code == 200, "Admin login failed"

        # 2. Test Bill Creation
        sample_bill = {
            "customer_name": "Test Customer Inc",
            "customer_email": "test@customer.com",
            "customer_phone": "123-456-7890",
            "customer_address": "123 Test Avenue, Testville",
            "tax_rate": 10.0,
            "items": [
                {"name": "Web Application Development", "qty": 1, "unit_price": 1200.0},
                {"name": "Server Deployment & Setup", "qty": 2, "unit_price": 150.0}
            ],
            "notes": "Thank you for your business!"
        }
        bill_res = client.post('/api/bills', json=sample_bill)
        print(f"Create Bill Response [{bill_res.status_code}]:", bill_res.get_json())
        assert bill_res.status_code == 201, "Bill creation failed"

        bill_data = bill_res.get_json()['bill']
        bill_id = bill_data['id']
        invoice_num = bill_data['invoice_number']

        # 3. Test Bill Retrieval
        get_res = client.get('/api/bills')
        print(f"Get Bills Response [{get_res.status_code}]: Found {len(get_res.get_json())} bills")
        assert len(get_res.get_json()) >= 1, "No bills found"

        # 4. Test PDF Download endpoint
        download_res = client.get(f'/api/bills/{bill_id}/download')
        print(f"Download PDF Response [{download_res.status_code}]: Content-Type={download_res.content_type}, Size={len(download_res.data)} bytes")
        assert download_res.status_code == 200, "PDF download endpoint failed"
        assert download_res.content_type == 'application/pdf', "Not a PDF"
        assert len(download_res.data) > 1000, "PDF file seems too small"

        print("\nAll Backend tests passed successfully!")

if __name__ == '__main__':
    run_tests()
