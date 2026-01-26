"""
Output formatter for client financial profiles.
Use this to format extracted data into the required structure.
"""

def format_client_profile(data: dict) -> str:
    """
    Format client data into standardized financial profile structure.
    
    Args:
        data: Dictionary containing client information with keys:
            - client_id: Client identifier
            - age, gender, education, family_status, children, household_size, housing
            - owns_realty, owns_car
            - income_type, occupation, years_employed, annual_income
            - contract_type, credit_amount, annuity, goods_price
            - prev_credit_amount, prev_annuity, approval_rate, rejection_rate
            - active_credits, external_credit, outstanding_debt
            - avg_payment_delay, payment_ratio, overdue_days, max_overdue_days
            - prolongations, overdue_amount
            - risk_status, risk_reasoning
    
    Returns:
        Formatted text string
    """
    template = """Client ID: {client_id}
Document Type: Client Financial Profile
Profile Generated On: {generated_on}
Data Coverage Period: {coverage_period}

Personal Information:
- Age: {age} years
- Gender: {gender}
- Education Level: {education}
- Family Status: {family_status}
- Number of Children: {children}
- Household Size: {household_size}
- Housing Type: {housing}

Assets & Ownership:
- Owns Real Estate: {owns_realty}
- Owns a Car: {owns_car}

Employment & Income:
- Income Type: {income_type}
- Occupation: {occupation}
- Years Employed: {years_employed}
- Annual Income: ${annual_income:,.0f}

Current Loan Application:
- Contract Type: {contract_type}
- Requested Credit Amount: ${credit_amount:,.0f}
- Monthly Annuity: ${annuity:,.0f}
- Goods Price: ${goods_price:,.0f}

Previous Loan Applications:
- Average Previous Credit Amount: ${prev_credit_amount:,.0f}
- Average Previous Annuity: ${prev_annuity:,.0f}
- Approval Rate: {approval_rate:.1f}%
- Rejection Rate: {rejection_rate:.1f}%

Credit History & Payment Behavior:
- Active External Credits: {active_credits}
- Total External Credit Amount: ${external_credit:,.0f}
- Total Outstanding Debt: ${outstanding_debt:,.0f}
- Average Payment Delay: {avg_payment_delay:.1f} days{payment_delay_note}
- Payment Completion Ratio: {payment_ratio:.1f}%
- Current Overdue Days: {overdue_days}
- Historical Maximum Overdue Days: {max_overdue_days}
- Total Credit Prolongations: {prolongations}
- Current Overdue Amount: ${overdue_amount:,.0f}

Risk Assessment:
Status: {risk_status}
Reasoning:
{risk_reasoning}
"""
    
    # Add payment delay note
    payment_delay_note = ""
    if data.get('avg_payment_delay', 0) < 0:
        payment_delay_note = " (early payments)"
    
    # Format reasoning as bullet points if it's a list
    risk_reasoning = data.get('risk_reasoning', 'Standard credit profile')
    if isinstance(risk_reasoning, list):
        risk_reasoning = "\n".join([f"- {reason}" for reason in risk_reasoning])
    
    # Fill template
    formatted = template.format(
        client_id=data.get('client_id', 'Unknown'),
        generated_on=data.get('generated_on', '2025-01-03'),
        coverage_period=data.get('coverage_period', '2015–2024'),
        age=data.get('age', 'Unknown'),
        gender=data.get('gender', 'Unknown'),
        education=data.get('education', 'Unknown'),
        family_status=data.get('family_status', 'Unknown'),
        children=data.get('children', 0),
        household_size=data.get('household_size', 0),
        housing=data.get('housing', 'Unknown'),
        owns_realty=data.get('owns_realty', 'Unknown'),
        owns_car=data.get('owns_car', 'Unknown'),
        income_type=data.get('income_type', 'Unknown'),
        occupation=data.get('occupation', 'Unknown'),
        years_employed=data.get('years_employed', 0),
        annual_income=data.get('annual_income', 0),
        contract_type=data.get('contract_type', 'Unknown'),
        credit_amount=data.get('credit_amount', 0),
        annuity=data.get('annuity', 0),
        goods_price=data.get('goods_price', 0),
        prev_credit_amount=data.get('prev_credit_amount', 0),
        prev_annuity=data.get('prev_annuity', 0),
        approval_rate=data.get('approval_rate', 0),
        rejection_rate=data.get('rejection_rate', 0),
        active_credits=data.get('active_credits', 0),
        external_credit=data.get('external_credit', 0),
        outstanding_debt=data.get('outstanding_debt', 0),
        avg_payment_delay=data.get('avg_payment_delay', 0),
        payment_delay_note=payment_delay_note,
        payment_ratio=data.get('payment_ratio', 0),
        overdue_days=data.get('overdue_days', 0),
        max_overdue_days=data.get('max_overdue_days', 0),
        prolongations=data.get('prolongations', 0),
        overdue_amount=data.get('overdue_amount', 0),
        risk_status=data.get('risk_status', 'UNKNOWN'),
        risk_reasoning=risk_reasoning
    )
    
    return formatted.strip()


# Example usage
if __name__ == "__main__":
    sample_data = {
        'client_id': 100021,
        'age': 26,
        'gender': 'F',
        'education': 'Secondary / secondary special',
        'family_status': 'Married',
        'children': 1,
        'household_size': 3,
        'housing': 'House / apartment',
        'owns_realty': 'Yes',
        'owns_car': 'No',
        'income_type': 'Working',
        'occupation': 'Laborers',
        'years_employed': 0,
        'annual_income': 81000,
        'contract_type': 'Revolving loans',
        'credit_amount': 270000,
        'annuity': 13500,
        'goods_price': 270000,
        'prev_credit_amount': 153616,
        'prev_annuity': 10686,
        'approval_rate': 100.0,
        'rejection_rate': 0.0,
        'active_credits': 0,
        'external_credit': 0,
        'outstanding_debt': 0,
        'avg_payment_delay': -12.3,
        'payment_ratio': 100.0,
        'overdue_days': 0,
        'max_overdue_days': 0,
        'prolongations': 0,
        'overdue_amount': 0,
        'risk_status': 'GOOD STANDING',
        'risk_reasoning': [
            'No current overdue payments',
            'Excellent payment completion ratio',
            'Early or on-time payment pattern'
        ]
    }
    
    print(format_client_profile(sample_data))
