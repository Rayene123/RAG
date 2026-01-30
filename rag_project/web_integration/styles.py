"""
Custom CSS styling for Decision Shadows web application
"""

CSS_STYLES = """
<style>
    /* Decision Shadows color palette */
    :root {
        --primary: #eab308;
        --success: #16a34a;
        --warning: #ea580c;
        --error: #dc2626;
        --info: #0891b2;
        --bg-light: #f8fafc;
        --border: #cbd5e1;
        --text-primary: #0f172a;
        --text-secondary: #475569;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #eab308 0%, #f59e0b 100%);
        padding: 25px 30px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(234, 179, 8, 0.25);
        color: white;
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 32px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .header-container p {
        margin: 8px 0 0 0;
        font-size: 13px;
        opacity: 0.92;
        font-weight: 500;
    }
    
    /* Section headers */
    .section-header {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #E5E7EB;
        color: #1F2937;
    }
    
    /* Card styling */
    .result-card {
        background: white;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #eab308;
    }
    
    .result-title {
        font-size: 15px;
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 8px;
    }
    
    .result-excerpt {
        font-size: 13px;
        color: #6B7280;
        line-height: 1.6;
        margin-bottom: 10px;
    }
    
    .result-meta {
        font-size: 12px;
        color: #9CA3AF;
    }
    
    .relevance-score {
        display: inline-block;
        background: #10B981;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Upload area */
    .upload-box {
        border: 2px dashed #eab308;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background: #fef9e7;
        margin-bottom: 15px;
    }
    
    /* Document list */
    .doc-item {
        background: #F9FAFB;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
    }
    
    .doc-status {
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .status-indexed {
        background: #D1FAE5;
        color: #065F46;
    }
    
    .status-processing {
        background: #FEF3C7;
        color: #92400E;
    }
    
    /* Response area */
    .response-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        margin-bottom: 15px;
    }
    
    .response-text {
        font-size: 14px;
        line-height: 1.8;
        color: #1F2937;
    }
    
    /* Info panel */
    .info-card {
        background: #F9FAFB;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 12px;
        border-left: 4px solid #eab308;
    }
    
    .info-label {
        font-size: 12px;
        color: #6B7280;
        margin-bottom: 5px;
        font-weight: 600;
    }
    
    .info-value {
        font-size: 18px;
        font-weight: 700;
        color: #1F2937;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #eab308 0%, #d97706 100%);
        color: white;
        border: none;
        font-weight: 600;
        border-radius: 8px;
        padding: 10px 20px;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(234, 179, 8, 0.35);
    }
    
    /* Shadow decision badges */
    .shadow-approve {
        background: #d1fae5;
        border-left: 4px solid #16a34a;
        color: #065f46;
    }
    
    .shadow-reject {
        background: #fee2e2;
        border-left: 4px solid #dc2626;
        color: #7f1d1d;
    }
    
    .shadow-conditional {
        background: #fef3c7;
        border-left: 4px solid #ea580c;
        color: #78350f;
    }
    
    .shadow-defer {
        background: #fef9e7;
        border-left: 4px solid #eab308;
        color: #713f12;
    }
    
    /* Risk/Bias indicators */
    .risk-high {
        background: #fecaca;
        color: #7f1d1d;
    }
    
    .risk-medium {
        background: #fcd34d;
        color: #78350f;
    }
    
    .risk-low {
        background: #86efac;
        color: #166534;
    }
    
    .bias-indicator {
        padding: 10px 12px;
        border-radius: 6px;
        font-size: 13px;
        margin-bottom: 10px;
    }
    
    /* Comparison card */
    .comparison-card {
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
        background: white;
    }
    
    .comparison-card:hover {
        border-color: #eab308;
        box-shadow: 0 4px 12px rgba(234, 179, 8, 0.15);
    }
    
    .comparison-header {
        font-weight: 600;
        margin-bottom: 8px;
        color: #0f172a;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #E5E7EB;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #eab308;
        box-shadow: 0 0 0 3px rgba(234, 179, 8, 0.15);
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #6B7280;
    }
    
    .empty-state-icon {
        font-size: 48px;
        margin-bottom: 15px;
    }
    
    /* Loading animation */
    .loading-text {
        display: inline-block;
    }
    
    /* Divider */
    .divider {
        height: 1px;
        background: #E5E7EB;
        margin: 20px 0;
    }
    
    /* Tips section */
    .tip-item {
        background: #FEF3C7;
        border-left: 3px solid #F59E0B;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 10px;
        font-size: 13px;
        color: #78350F;
    }
</style>
"""
