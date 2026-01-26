"""
Create a sample PDF file with client financial profile structure for testing.
"""

from fpdf import FPDF
from pathlib import Path
import os

class ClientProfilePDF(FPDF):
    """Custom PDF class for client financial profiles - Bank statement style"""
    
    def header(self):
        """Add professional header to each page"""
        # Top border
        self.set_draw_color(0, 51, 102)  # Dark blue
        self.set_line_width(0.5)
        self.line(10, 10, 200, 10)
        
        # Institution header
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, 'FINANCIAL SERVICES CORPORATION', 0, 1, 'C')
        
        self.set_font('Arial', '', 9)
        self.set_text_color(80, 80, 80)
        self.cell(0, 4, 'Credit Analysis Department | Document Generated: 2025-01-03', 0, 1, 'C')
        
        self.set_draw_color(0, 51, 102)
        self.line(10, 25, 200, 25)
        self.ln(8)
    
    def footer(self):
        """Add footer with page number"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Confidential Document', 0, 0, 'C')
    
    def add_section_header(self, title):
        """Add a section header with background"""
        self.set_fill_color(230, 240, 250)  # Light blue background
        self.set_font('Arial', 'B', 11)
        self.set_text_color(0, 51, 102)
        self.cell(0, 8, title, 0, 1, 'L', True)
        self.ln(2)
    
    def add_info_row(self, label, value, is_bold=False):
        """Add a formatted information row"""
        self.set_font('Arial', '', 9)
        self.set_text_color(60, 60, 60)
        self.cell(80, 6, label, 0, 0)
        
        if is_bold:
            self.set_font('Arial', 'B', 9)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, value, 0, 1)
    
    def add_table_row(self, col1, col2, col3=None, col4=None, is_header=False):
        """Add a table row with 2-4 columns"""
        if is_header:
            self.set_fill_color(200, 220, 240)
            self.set_font('Arial', 'B', 9)
            self.set_text_color(0, 51, 102)
        else:
            self.set_fill_color(245, 245, 245)
            self.set_font('Arial', '', 9)
            self.set_text_color(0, 0, 0)
        
        if col4:  # 4 columns
            self.cell(45, 6, col1, 1, 0, 'L', True)
            self.cell(45, 6, col2, 1, 0, 'R', True)
            self.cell(45, 6, col3, 1, 0, 'L', True)
            self.cell(45, 6, col4, 1, 1, 'R', True)
        elif col3:  # 3 columns
            self.cell(60, 6, col1, 1, 0, 'L', True)
            self.cell(60, 6, col2, 1, 0, 'R', True)
            self.cell(60, 6, col3, 1, 1, 'R', True)
        else:  # 2 columns
            self.cell(90, 6, col1, 1, 0, 'L', True)
            self.cell(90, 6, col2, 1, 1, 'R', True)


def create_client_profile_pdf():
    """Create a PDF with the client financial profile structure"""
    
    # Create output directory
    output_dir = Path("embeddings/pdf/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize PDF
    pdf = ClientProfilePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # Document title and reference
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, 'CLIENT FINANCIAL PROFILE', 0, 1, 'C')
    pdf.ln(3)
    
    # Client ID and Document Info Box
    pdf.set_fill_color(240, 248, 255)
    pdf.rect(10, pdf.get_y(), 190, 22, 'F')
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'Client ID: 100021', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 5, 'Document Type: Client Financial Profile', 0, 1, 'C')
    pdf.cell(0, 5, 'Data Coverage Period: 2015-2024', 0, 1, 'C')
    pdf.ln(8)
    
    # PERSONAL INFORMATION
    pdf.add_section_header('PERSONAL INFORMATION')
    pdf.add_info_row('Age:', '26 years')
    pdf.add_info_row('Gender:', 'F')
    pdf.add_info_row('Education Level:', 'Secondary / secondary special')
    pdf.add_info_row('Family Status:', 'Married')
    pdf.add_info_row('Number of Children:', '1')
    pdf.add_info_row('Household Size:', '3')
    pdf.add_info_row('Housing Type:', 'House / apartment')
    pdf.ln(5)
    
    # ASSETS & OWNERSHIP
    pdf.add_section_header('ASSETS & OWNERSHIP')
    pdf.add_table_row('Asset Type', 'Status', is_header=True)
    pdf.add_table_row('Real Estate', 'Yes')
    pdf.add_table_row('Vehicle', 'No')
    pdf.ln(5)
    
    # EMPLOYMENT & INCOME
    pdf.add_section_header('EMPLOYMENT & INCOME')
    pdf.add_info_row('Income Type:', 'Working')
    pdf.add_info_row('Occupation:', 'Laborers')
    pdf.add_info_row('Years Employed:', '0')
    pdf.add_info_row('Annual Income:', '$81,000', is_bold=True)
    pdf.ln(5)
    
    # CURRENT LOAN APPLICATION
    pdf.add_section_header('CURRENT LOAN APPLICATION')
    pdf.add_table_row('Description', 'Amount', is_header=True)
    pdf.add_table_row('Contract Type: Revolving loans', '')
    pdf.add_table_row('Requested Credit Amount', '$270,000')
    pdf.add_table_row('Monthly Annuity', '$13,500')
    pdf.add_table_row('Goods Price', '$270,000')
    pdf.ln(5)
    
    # PREVIOUS LOAN APPLICATIONS
    pdf.add_section_header('PREVIOUS LOAN APPLICATIONS')
    pdf.add_table_row('Metric', 'Value', is_header=True)
    pdf.add_table_row('Average Previous Credit Amount', '$153,616')
    pdf.add_table_row('Average Previous Annuity', '$10,686')
    pdf.add_table_row('Approval Rate', '100.0%')
    pdf.add_table_row('Rejection Rate', '0.0%')
    pdf.ln(5)
    
    # CREDIT HISTORY & PAYMENT BEHAVIOR
    pdf.add_section_header('CREDIT HISTORY & PAYMENT BEHAVIOR')
    pdf.add_table_row('Metric', 'Value', is_header=True)
    pdf.add_table_row('Active External Credits', '0')
    pdf.add_table_row('Total External Credit Amount', '$0')
    pdf.add_table_row('Total Outstanding Debt', '$0')
    pdf.add_table_row('Average Payment Delay', '-12.3 days (early payments)')
    pdf.add_table_row('Payment Completion Ratio', '100.0%')
    pdf.add_table_row('Current Overdue Days', '0')
    pdf.add_table_row('Historical Maximum Overdue Days', '0')
    pdf.add_table_row('Total Credit Prolongations', '0')
    pdf.add_table_row('Current Overdue Amount', '$0')
    pdf.ln(5)
    
    
    # Save PDF
    output_path = output_dir / "client_100021_financial_profile.pdf"
    pdf.output(str(output_path))
    
    print(f"✅ Created PDF: {output_path}")
    print(f"   File size: {output_path.stat().st_size:,} bytes")
    
    return output_path


def create_multiple_sample_pdfs():
    """Create multiple sample PDFs with different client profiles"""
    
    output_dir = Path("embeddings/pdf/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample data for different clients
    clients = [
        {
            'id': 100030,
            'age': 35,
            'gender': 'M',
            'education': 'Higher education',
            'family_status': 'Single',
            'children': 0,
            'household_size': 1,
            'housing': 'Rented apartment',
            'owns_realty': 'No',
            'owns_car': 'Yes',
            'income_type': 'Commercial associate',
            'occupation': 'Managers',
            'years_employed': 5,
            'annual_income': 120000,
            'contract_type': 'Cash loans',
            'credit_amount': 450000,
            'annuity': 25000,
            'goods_price': 450000,
            'prev_credit': 200000,
            'prev_annuity': 15000,
            'approval_rate': 80.0,
            'rejection_rate': 20.0,
            'active_credits': 2,
            'external_credit': 350000,
            'outstanding_debt': 100000,
            'payment_delay': 5.2,
            'payment_ratio': 95.5,
            'overdue_days': 0,
            'max_overdue_days': 15,
            'prolongations': 1,
            'overdue_amount': 0,
        },
        {
            'id': 100033,
            'age': 42,
            'gender': 'F',
            'education': 'Secondary / secondary special',
            'family_status': 'Civil marriage',
            'children': 2,
            'household_size': 4,
            'housing': 'House / apartment',
            'owns_realty': 'Yes',
            'owns_car': 'Yes',
            'income_type': 'Working',
            'occupation': 'Core staff',
            'years_employed': 8,
            'annual_income': 95000,
            'contract_type': 'Cash loans',
            'credit_amount': 320000,
            'annuity': 18000,
            'goods_price': 320000,
            'prev_credit': 180000,
            'prev_annuity': 12000,
            'approval_rate': 100.0,
            'rejection_rate': 0.0,
            'active_credits': 1,
            'external_credit': 250000,
            'outstanding_debt': 50000,
            'payment_delay': -3.5,
            'payment_ratio': 100.0,
            'overdue_days': 0,
            'max_overdue_days': 0,
            'prolongations': 0,
            'overdue_amount': 0,
        }
    ]
    
    created_files = []
    
    for client in clients:
        pdf = ClientProfilePDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)
        
        # Document title and reference
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, 'CLIENT FINANCIAL PROFILE', 0, 1, 'C')
        pdf.ln(3)
        
        # Client ID and Document Info Box
        pdf.set_fill_color(240, 248, 255)
        pdf.rect(10, pdf.get_y(), 190, 22, 'F')
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, f"Client ID: {client['id']}", 0, 1, 'C')
        
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 5, 'Document Type: Client Financial Profile', 0, 1, 'C')
        pdf.cell(0, 5, 'Data Coverage Period: 2015-2024', 0, 1, 'C')
        pdf.ln(8)
        
        # PERSONAL INFORMATION
        pdf.add_section_header('PERSONAL INFORMATION')
        pdf.add_info_row('Age:', f"{client['age']} years")
        pdf.add_info_row('Gender:', client['gender'])
        pdf.add_info_row('Education Level:', client['education'])
        pdf.add_info_row('Family Status:', client['family_status'])
        pdf.add_info_row('Number of Children:', str(client['children']))
        pdf.add_info_row('Household Size:', str(client['household_size']))
        pdf.add_info_row('Housing Type:', client['housing'])
        pdf.ln(5)
        
        # ASSETS & OWNERSHIP
        pdf.add_section_header('ASSETS & OWNERSHIP')
        pdf.add_table_row('Asset Type', 'Status', is_header=True)
        pdf.add_table_row('Real Estate', client['owns_realty'])
        pdf.add_table_row('Vehicle', client['owns_car'])
        pdf.ln(5)
        
        # EMPLOYMENT & INCOME
        pdf.add_section_header('EMPLOYMENT & INCOME')
        pdf.add_info_row('Income Type:', client['income_type'])
        pdf.add_info_row('Occupation:', client['occupation'])
        pdf.add_info_row('Years Employed:', str(client['years_employed']))
        pdf.add_info_row('Annual Income:', f"${client['annual_income']:,}", is_bold=True)
        pdf.ln(5)
        
        # CURRENT LOAN APPLICATION
        pdf.add_section_header('CURRENT LOAN APPLICATION')
        pdf.add_table_row('Description', 'Amount', is_header=True)
        pdf.add_table_row(f"Contract Type: {client['contract_type']}", '')
        pdf.add_table_row('Requested Credit Amount', f"${client['credit_amount']:,}")
        pdf.add_table_row('Monthly Annuity', f"${client['annuity']:,}")
        pdf.add_table_row('Goods Price', f"${client['goods_price']:,}")
        pdf.ln(5)
        
        # PREVIOUS LOAN APPLICATIONS
        pdf.add_section_header('PREVIOUS LOAN APPLICATIONS')
        pdf.add_table_row('Metric', 'Value', is_header=True)
        pdf.add_table_row('Average Previous Credit Amount', f"${client['prev_credit']:,}")
        pdf.add_table_row('Average Previous Annuity', f"${client['prev_annuity']:,}")
        pdf.add_table_row('Approval Rate', f"{client['approval_rate']}%")
        pdf.add_table_row('Rejection Rate', f"{client['rejection_rate']}%")
        pdf.ln(5)
        
        # CREDIT HISTORY & PAYMENT BEHAVIOR
        pdf.add_section_header('CREDIT HISTORY & PAYMENT BEHAVIOR')
        payment_note = ' (early payments)' if client['payment_delay'] < 0 else ''
        pdf.add_table_row('Metric', 'Value', is_header=True)
        pdf.add_table_row('Active External Credits', str(client['active_credits']))
        pdf.add_table_row('Total External Credit Amount', f"${client['external_credit']:,}")
        pdf.add_table_row('Total Outstanding Debt', f"${client['outstanding_debt']:,}")
        pdf.add_table_row('Average Payment Delay', f"{client['payment_delay']:.1f} days{payment_note}")
        pdf.add_table_row('Payment Completion Ratio', f"{client['payment_ratio']}%")
        pdf.add_table_row('Current Overdue Days', str(client['overdue_days']))
        pdf.add_table_row('Historical Maximum Overdue Days', str(client['max_overdue_days']))
        pdf.add_table_row('Total Credit Prolongations', str(client['prolongations']))
        pdf.add_table_row('Current Overdue Amount', f"${client['overdue_amount']:,}")
        pdf.ln(5)
        
        # RISK ASSESSMENT (Status will be determined by agents later)
        pdf.add_section_header('RISK ASSESSMENT')
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, 'Status: To be determined by risk assessment agent', 0, 1)
        pdf.ln(2)
        
        # Save PDF
        output_path = output_dir / f"client_{client['id']}_financial_profile.pdf"
        pdf.output(str(output_path))
        created_files.append(output_path)
        
        print(f"✅ Created PDF: {output_path.name} ({output_path.stat().st_size:,} bytes)")
    
    return created_files


if __name__ == "__main__":
    print("Creating sample PDF files...\n")
    
    # Create the main sample
    create_client_profile_pdf()
    
    print("\nCreating additional sample PDFs...\n")
    # Create additional samples
    create_multiple_sample_pdfs()
    
    print("\n✅ All PDF files created successfully!")
    print("\nYou can now run: python test_transformer_output.py")
