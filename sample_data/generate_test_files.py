import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Generate sample DIAN-compliant data files"""
    
    # Sample data for Colombian accounting
    cuentas = [
        "1100", "1200", "1300", "1400", "2100", "2200", "3100", "3200", "4100", "5100", "5200", "5300"
    ]
    
    nits = [
        "900123456-7", "800987654-3", "700456789-1", "600321654-9", "500789123-4",
        "400654321-8", "300147258-6", "200963852-1", "100852963-7", "900741852-3"
    ]
    
    tipos_documento = [
        "Factura", "Recibo de Caja", "Comprobante de Egreso", "Nota Crédito", "Nota Débito",
        "Ticket POS", "Factura de Exportación", "Factura de Importación"
    ]
    
    # Generate data for 2023
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    # File 1: Sales transactions (Jan-Jun 2023)
    sales_data = []
    for i in range(500):
        fecha = start_date + timedelta(days=random.randint(0, 180))
        valor = random.uniform(10000, 5000000)
        cuenta = random.choice(["4100", "1200", "1100"])
        nit = random.choice(nits)
        tipo = random.choice(["Factura", "Ticket POS", "Factura de Exportación"])
        
        sales_data.append({
            'FECHA': fecha.strftime('%d/%m/%Y'),
            'VALOR': round(valor, 2),
            'CUENTA': cuenta,
            'NIT': nit,
            'TIPO_DOCUMENTO': tipo
        })
    
    df_sales = pd.DataFrame(sales_data)
    df_sales.to_excel('sales_transactions_2023.xlsx', index=False)
    print("Generated: sales_transactions_2023.xlsx")
    
    # File 2: Purchase transactions (Mar-Sep 2023)
    purchase_data = []
    for i in range(400):
        fecha = datetime(2023, 3, 1) + timedelta(days=random.randint(0, 180))
        valor = random.uniform(50000, 3000000)
        cuenta = random.choice(["5100", "5200", "2100", "2200"])
        nit = random.choice(nits)
        tipo = random.choice(["Factura", "Comprobante de Egreso", "Factura de Importación"])
        
        purchase_data.append({
            'FECHA': fecha.strftime('%d/%m/%Y'),
            'VALOR': round(valor, 2),
            'CUENTA': cuenta,
            'NIT': nit,
            'TIPO_DOCUMENTO': tipo
        })
    
    df_purchases = pd.DataFrame(purchase_data)
    df_purchases.to_excel('purchase_transactions_2023.xlsx', index=False)
    print("Generated: purchase_transactions_2023.xlsx")
    
    # File 3: Mixed transactions (Jul-Dec 2023)
    mixed_data = []
    for i in range(600):
        fecha = datetime(2023, 7, 1) + timedelta(days=random.randint(0, 180))
        valor = random.uniform(15000, 4000000)
        cuenta = random.choice(cuentas)
        nit = random.choice(nits)
        tipo = random.choice(tipos_documento)
        
        mixed_data.append({
            'FECHA': fecha.strftime('%d/%m/%Y'),
            'VALOR': round(valor, 2),
            'CUENTA': cuenta,
            'NIT': nit,
            'TIPO_DOCUMENTO': tipo
        })
    
    df_mixed = pd.DataFrame(mixed_data)
    df_mixed.to_excel('mixed_transactions_2023.xlsx', index=False)
    print("Generated: mixed_transactions_2023.xlsx")
    
    # File 4: CSV format with different column names
    csv_data = []
    for i in range(300):
        fecha = datetime(2023, 4, 1) + timedelta(days=random.randint(0, 240))
        valor = random.uniform(20000, 2500000)
        cuenta = random.choice(cuentas)
        nit = random.choice(nits)
        tipo = random.choice(tipos_documento)
        
        csv_data.append({
            'date': fecha.strftime('%Y-%m-%d'),
            'amount': round(valor, 2),
            'account_code': cuenta,
            'third_party_id': nit,
            'document_type': tipo
        })
    
    df_csv = pd.DataFrame(csv_data)
    df_csv.to_csv('transactions_2023.csv', index=False)
    print("Generated: transactions_2023.csv")
    
    # Print summary statistics
    print("\n=== Generated Test Files Summary ===")
    print("1. sales_transactions_2023.xlsx - 500 transactions (Jan-Jun)")
    print("2. purchase_transactions_2023.xlsx - 400 transactions (Mar-Sep)")
    print("3. mixed_transactions_2023.xlsx - 600 transactions (Jul-Dec)")
    print("4. transactions_2023.csv - 300 transactions (Apr-Dec)")
    print("\nTotal: 1,800 transactions across 4 files")
    print("Date range: January 1, 2023 to December 31, 2023")
    print("Files contain overlapping dates for testing date filtering")

if __name__ == "__main__":
    generate_sample_data() 