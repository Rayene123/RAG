"""
Feature Extractor for Query Processing.

Extracts and normalizes key features from PDF text to create 
more focused embeddings that match the stored client representations.
"""

import re
from typing import Dict, Optional


class FeatureExtractor:
    """
    Extracts key features from client profile text to create
    focused query representations.
    """
    
    def extract_key_features(self, text: str) -> str:
        """
        Extract and emphasize key discriminative features from client text.
        
        Priority weighting for loan decisions:
        1. CRITICAL: Payment behavior, debt levels, credit history (10x weight)
        2. HIGH: Income, employment stability, debt ratios (5x weight)
        3. MEDIUM: Family composition, assets (3x weight)
        4. LOW: Demographics (age, gender, education) (1x weight)
        
        Args:
            text: Raw client profile text
        
        Returns:
            Feature-focused text for embedding
        """
        features = []
        
        # === Extract raw values for calculations ===
        income_value = None
        debt_value = None
        external_credit_value = None
        
        # Extract age (LOW priority - 1x)
        age_match = re.search(r'Age:\s*(\d+)\s*years?', text, re.IGNORECASE)
        if age_match:
            age = int(age_match.group(1))
            features.append(f"age {age} years")
        
        # Extract gender (LOW priority - 1x)
        gender_match = re.search(r'Gender:\s*([MF])', text, re.IGNORECASE)
        if gender_match:
            gender = gender_match.group(1)
            features.append(f"gender {gender}")
        
        # Extract education (LOW priority - 1x)
        education_match = re.search(r'Education Level:\s*([^\n]+)', text, re.IGNORECASE)
        if education_match:
            education = education_match.group(1).strip()
            features.append(f"education {education}")
        
        # Extract family status (MEDIUM priority - 2x)
        family_match = re.search(r'Family Status:\s*([^\n]+)', text, re.IGNORECASE)
        if family_match:
            family = family_match.group(1).strip()
            features.extend([f"family status {family}"] * 2)
        
        # Number of children (MEDIUM priority - 3x)
        children_match = re.search(r'Number of Children:\s*(\d+)', text, re.IGNORECASE)
        if children_match:
            children = int(children_match.group(1))
            features.extend([f"{children} children"] * 3)
        
        # Household size (MEDIUM priority - 2x)
        household_match = re.search(r'Household Size:\s*(\d+)', text, re.IGNORECASE)
        if household_match:
            household = int(household_match.group(1))
            features.extend([f"household size {household}"] * 2)
        
        # Extract housing type (MEDIUM priority - 2x)
        housing_match = re.search(r'Housing Type:\s*([^\n]+)', text, re.IGNORECASE)
        if housing_match:
            housing = housing_match.group(1).strip()
            features.extend([f"housing {housing}"] * 2)
        
        # Real estate ownership (MEDIUM priority - 3x)
        realty_match = re.search(r'Owns Real Estate:\s*(Yes|No)', text, re.IGNORECASE)
        if realty_match:
            has_realty = realty_match.group(1).lower() == 'yes'
            realty_text = "owns real estate" if has_realty else "no real estate"
            features.extend([realty_text] * 3)
        
        # Car ownership (MEDIUM priority - 3x)
        car_match = re.search(r'Owns a Car:\s*(Yes|No)', text, re.IGNORECASE)
        if car_match:
            has_car = car_match.group(1).lower() == 'yes'
            car_text = "owns car" if has_car else "no car"
            features.extend([car_text] * 3)
        
        # Car age if available (LOW priority - 1x)
        car_age_match = re.search(r'age:\s*(\d+)\s*years?\)', text, re.IGNORECASE)
        if car_age_match:
            car_age = int(car_age_match.group(1))
            features.append(f"car age {car_age} years")
        
        # Extract income type (MEDIUM priority - 2x)
        income_type_match = re.search(r'Income Type:\s*([^\n]+)', text, re.IGNORECASE)
        if income_type_match:
            income_type = income_type_match.group(1).strip()
            features.extend([f"income type {income_type}"] * 2)
        
        # Extract occupation (MEDIUM priority - 3x)
        occupation_match = re.search(r'Occupation:\s*([^\n]+)', text, re.IGNORECASE)
        if occupation_match:
            occupation = occupation_match.group(1).strip()
            features.extend([f"occupation {occupation}"] * 3)
        
        # ✨ HIGH PRIORITY: Employment years (repeat 5x)
        employment_match = re.search(r'Years Employed:\s*(\d+)', text, re.IGNORECASE)
        if employment_match:
            years = int(employment_match.group(1))
            features.extend([f"employed {years} years"] * 5)
        
        # ✨ HIGH PRIORITY: Extract income (repeat 5x)
        income_match = re.search(r'Annual Income:\s*\$?([\d,]+)', text, re.IGNORECASE)
        if income_match:
            income = income_match.group(1).replace(',', '')
            income_value = int(income)
            features.extend([f"income ${income}"] * 5)
        
        # Extract contract type (MEDIUM priority - 2x)
        contract_match = re.search(r'Contract Type:\s*([^\n]+)', text, re.IGNORECASE)
        if contract_match:
            contract = contract_match.group(1).strip()
            features.extend([f"contract {contract}"] * 2)
        
        # Extract credit amount (MEDIUM priority - 3x)
        credit_match = re.search(r'Requested Credit Amount[:\s]*\$?([\d,]+)', text, re.IGNORECASE)
        if credit_match:
            credit = credit_match.group(1).replace(',', '')
            features.extend([f"requesting ${credit}"] * 3)
        
        # Extract annuity (MEDIUM priority - 3x)
        annuity_match = re.search(r'Monthly Annuity[:\s]*\$?([\d,]+)', text, re.IGNORECASE)
        if annuity_match:
            annuity = annuity_match.group(1).replace(',', '')
            features.extend([f"monthly payment ${annuity}"] * 3)
        
        # Previous credit history (HIGH priority - 4x)
        prev_credit_match = re.search(r'Average Previous Credit Amount[:\s]*\$?([\d,]+)', text, re.IGNORECASE)
        if prev_credit_match:
            prev_credit = prev_credit_match.group(1).replace(',', '')
            features.extend([f"previous credit ${prev_credit}"] * 4)
        
        # ✨ CRITICAL: Approval rate (repeat 8x)
        approval_match = re.search(r'Approval Rate[:\s]*([\d.]+)%', text, re.IGNORECASE)
        if approval_match:
            approval = float(approval_match.group(1))
            features.extend([f"approval rate {approval}%"] * 8)
        
        # ✨ HIGH PRIORITY: Active credits (repeat 5x)
        active_credits_match = re.search(r'Active External Credits[:\s]*(\d+)', text, re.IGNORECASE)
        if active_credits_match:
            active = int(active_credits_match.group(1))
            features.extend([f"{active} active credits"] * 5)
        
        # ✨ HIGH PRIORITY: External credit amount (repeat 5x)
        external_credit_match = re.search(r'Total External Credit Amount[:\s]*\$?([\d,]+)', text, re.IGNORECASE)
        if external_credit_match:
            external = external_credit_match.group(1).replace(',', '')
            external_credit_value = int(external)
            features.extend([f"external credit ${external}"] * 5)
        
        # ✨ CRITICAL: Outstanding debt (repeat 10x)
        debt_match = re.search(r'Total Outstanding Debt[:\s]*\$?([\d,]+)', text, re.IGNORECASE)
        if debt_match:
            debt = debt_match.group(1).replace(',', '')
            debt_value = int(debt)
            features.extend([f"outstanding debt ${debt}"] * 10)
        
        # ✨ HIGH PRIORITY: Historical max overdue amount (repeat 7x)
        max_overdue_amt_match = re.search(r'Historical Maximum Overdue Amount[:\s]*\$?([\d,]+)', text, re.IGNORECASE)
        if max_overdue_amt_match:
            max_overdue_amt = max_overdue_amt_match.group(1).replace(',', '')
            features.extend([f"max overdue amount ${max_overdue_amt}"] * 7)
        
        # ✨ CRITICAL: Payment delay (repeat 10x)
        delay_match = re.search(r'Average Payment Delay[:\s]*(-?[\d.]+)\s*days', text, re.IGNORECASE)
        if delay_match:
            delay = float(delay_match.group(1))
            if delay < 0:
                features.extend([f"early payments {abs(delay)} days"] * 10)
            elif delay == 0:
                features.extend(["on-time payments"] * 10)
            else:
                features.extend([f"late payments {delay} days"] * 10)
        
        # ✨ CRITICAL: Payment completion ratio (repeat 12x)
        completion_match = re.search(r'Payment Completion Ratio[:\s]*([\d.]+)%', text, re.IGNORECASE)
        if completion_match:
            completion = float(completion_match.group(1))
            features.extend([f"payment completion {completion}%"] * 12)
        
        # ✨ CRITICAL: Current overdue (repeat 10x)
        overdue_match = re.search(r'Current Overdue Days[:\s]*(\d+)', text, re.IGNORECASE)
        if overdue_match:
            overdue = int(overdue_match.group(1))
            if overdue > 0:
                features.extend([f"currently overdue {overdue} days"] * 10)
            else:
                features.extend(["no current overdue"] * 10)
        
        # ✨ CRITICAL: Max overdue (repeat 12x - major risk indicator)
        max_overdue_match = re.search(r'Historical Maximum Overdue Days[:\s]*(\d+)', text, re.IGNORECASE)
        if max_overdue_match:
            max_overdue = int(max_overdue_match.group(1))
            if max_overdue > 0:
                features.extend([f"max overdue {max_overdue} days"] * 12)
            else:
                features.extend(["no historical overdue"] * 8)
        
        # ✨ HIGH PRIORITY: Prolongations (repeat 6x)
        prolongations_match = re.search(r'Total Credit Prolongations[:\s]*(\d+)', text, re.IGNORECASE)
        if prolongations_match:
            prolongations = int(prolongations_match.group(1))
            if prolongations > 0:
                features.extend([f"{prolongations} prolongations"] * 6)
            else:
                features.extend(["no prolongations"] * 4)
        
        # ✨✨ CALCULATED FEATURE: Debt-to-Income Ratio (repeat 15x - MOST CRITICAL)
        if income_value and income_value > 0 and debt_value is not None:
            dti_ratio = (debt_value / income_value) * 100
            if dti_ratio == 0:
                features.extend(["debt-to-income 0% no debt"] * 15)
            elif dti_ratio < 20:
                features.extend([f"debt-to-income {dti_ratio:.1f}% low debt"] * 15)
            elif dti_ratio < 40:
                features.extend([f"debt-to-income {dti_ratio:.1f}% moderate debt"] * 15)
            elif dti_ratio < 60:
                features.extend([f"debt-to-income {dti_ratio:.1f}% high debt"] * 15)
            else:
                features.extend([f"debt-to-income {dti_ratio:.1f}% very high debt"] * 15)
        
        # ✨✨ CALCULATED FEATURE: Credit Utilization (repeat 12x)
        if external_credit_value and external_credit_value > 0 and debt_value is not None:
            utilization = (debt_value / external_credit_value) * 100
            if utilization == 0:
                features.extend(["credit utilization 0% fully paid"] * 12)
            elif utilization < 30:
                features.extend([f"credit utilization {utilization:.1f}% low"] * 12)
            elif utilization < 60:
                features.extend([f"credit utilization {utilization:.1f}% moderate"] * 12)
            else:
                features.extend([f"credit utilization {utilization:.1f}% high"] * 12)
        
        # Combine all features
        if not features:
            # Fallback: use first 500 characters of raw text
            return text[:500]
        
        # Join with spaces - repeated features naturally increase weight
        return " ".join(features)
    
    def extract_summary(self, text: str) -> Dict[str, any]:
        """
        Extract structured features as a dictionary.
        Useful for debugging and analysis.
        
        Args:
            text: Raw client profile text
        
        Returns:
            Dictionary of extracted features
        """
        summary = {}
        
        # Extract key fields using same patterns
        age_match = re.search(r'Age:\s*(\d+)', text, re.IGNORECASE)
        if age_match:
            summary['age'] = int(age_match.group(1))
        
        children_match = re.search(r'Number of Children:\s*(\d+)', text, re.IGNORECASE)
        if children_match:
            summary['children'] = int(children_match.group(1))
        
        employment_match = re.search(r'Years Employed:\s*(\d+)', text, re.IGNORECASE)
        if employment_match:
            summary['years_employed'] = int(employment_match.group(1))
        
        debt_match = re.search(r'Total Outstanding Debt[:\s]*\$?([\d,]+)', text, re.IGNORECASE)
        if debt_match:
            summary['outstanding_debt'] = int(debt_match.group(1).replace(',', ''))
        
        completion_match = re.search(r'Payment Completion Ratio[:\s]*([\d.]+)%', text, re.IGNORECASE)
        if completion_match:
            summary['payment_completion'] = float(completion_match.group(1))
        
        realty_match = re.search(r'Owns Real Estate:\s*(Yes|No)', text, re.IGNORECASE)
        if realty_match:
            summary['owns_realty'] = realty_match.group(1).lower() == 'yes'
        
        car_match = re.search(r'Owns a Car:\s*(Yes|No)', text, re.IGNORECASE)
        if car_match:
            summary['owns_car'] = car_match.group(1).lower() == 'yes'
        
        return summary
