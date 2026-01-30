"""
Sample Test Queries for RAGAS Evaluation.

Pre-defined test queries with optional ground truth answers
for comprehensive RAG evaluation.
"""

# Test queries without ground truth (for basic metrics)
BASIC_TEST_QUERIES = [
    "Find clients with high income and education level",
    "Show me clients who have defaulted on loans",
    "Retrieve information about clients with low credit amounts",
    "Find clients with many previous loan applications",
    "Show clients with overdue payments in their history",
    "List clients with good credit history and stable employment",
    "Find young clients under 30 years old",
    "Show clients with large families",
    "Retrieve information about clients with annuity payments",
    "Find clients with multiple credit lines"
]

# Test queries with ground truth (for full metrics)
TEST_QUERIES_WITH_GROUND_TRUTH = [
    {
        "question": "Find clients with high income and education level",
        "ground_truth": "Clients with income above 200,000 and higher education typically have stable financial profiles. These clients generally have lower default rates and better credit histories.",
        "category": "profile_search"
    },
    {
        "question": "Show me clients who have defaulted on loans",
        "ground_truth": "Defaulted clients have TARGET=1 in their records, indicating they experienced payment difficulties (90+ days past due) on previous loans. These clients represent higher credit risk.",
        "category": "risk_assessment"
    },
    {
        "question": "What are the characteristics of high-risk clients?",
        "ground_truth": "High-risk clients typically have one or more of the following: previous payment difficulties (TARGET=1), low income relative to credit amount, multiple previous loan applications, history of overdue payments, unstable employment, or high debt-to-income ratios.",
        "category": "risk_assessment"
    },
    {
        "question": "Find clients with good credit history",
        "ground_truth": "Clients with good credit history have TARGET=0, no previous payment difficulties, consistent employment history, stable income, and low or no overdue days on previous credits. They typically have a positive payment track record.",
        "category": "profile_search"
    },
    {
        "question": "What factors indicate loan default risk?",
        "ground_truth": "Key default risk indicators include: previous payment difficulties, low income-to-credit ratio, unemployment or unstable employment, young age combined with high loan amounts, multiple rejected applications, high number of previous enquiries, and history of overdue payments.",
        "category": "risk_assessment"
    },
    {
        "question": "Show clients with previous loan applications",
        "ground_truth": "Clients with previous loan applications have records in the previous_application table. Multiple applications, especially if rejected, can indicate financial stress or difficulty obtaining credit.",
        "category": "history_search"
    },
    {
        "question": "Find clients with overdue payment history",
        "ground_truth": "Clients with overdue payments have records in installments_payments showing days past due (DPD) greater than zero. Frequent or long overdue periods indicate payment difficulties and higher risk.",
        "category": "risk_assessment"
    },
    {
        "question": "What information is available about client employment?",
        "ground_truth": "Employment information includes organization type, years employed, occupation type, and employment status. Stable employment with longer tenure typically correlates with lower default risk.",
        "category": "profile_search"
    },
    {
        "question": "How can I identify clients with financial difficulties?",
        "ground_truth": "Financial difficulties are indicated by: TARGET=1 (payment difficulties), overdue payments in installment history, multiple rejected applications, low income relative to obligations, high debt ratios, and unstable employment or income sources.",
        "category": "risk_assessment"
    },
    {
        "question": "What is the relationship between income and default?",
        "ground_truth": "Lower income clients generally have higher default rates, especially when combined with high credit amounts. However, income stability and debt-to-income ratio are better predictors than absolute income level alone.",
        "category": "analysis"
    }
]

# Category descriptions
CATEGORY_DESCRIPTIONS = {
    "profile_search": "Queries about finding clients based on demographic or financial profiles",
    "risk_assessment": "Queries about evaluating credit risk and default probability",
    "history_search": "Queries about client historical data and previous applications",
    "analysis": "Queries about understanding relationships and patterns in the data"
}


def get_queries_by_category(category: str) -> list:
    """
    Get test queries filtered by category.
    
    Args:
        category: Category name
    
    Returns:
        List of test cases for that category
    """
    return [q for q in TEST_QUERIES_WITH_GROUND_TRUTH if q["category"] == category]


def get_all_categories() -> list:
    """Get list of all available categories."""
    return list(CATEGORY_DESCRIPTIONS.keys())
