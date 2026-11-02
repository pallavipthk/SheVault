"""
SHEVAULT AI - Data Models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: Optional[str] = "Student"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: str

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

class OpportunityAnalysisRequest(BaseModel):
    opportunity_type: str = "Job" # Job, Internship, Scholarship, Freelance, Business Opportunity, Other
    organization_name: Optional[str] = ""
    website_url: Optional[str] = ""
    message_text: Optional[str] = ""
    demo_preset_id: Optional[str] = None

class EvidenceItem(BaseModel):
    id: str
    title: str
    risk_category: str # "Identity Risk", "Payment Trap", "Impersonation", "Urgency/Coercion", "Unverified Domain"
    severity: str # "high", "medium", "low"
    description: str
    why_it_matters: str
    source_snippet: Optional[str] = None
    uncertainty_note: str

class IdentityItem(BaseModel):
    name: str # e.g. "Aadhaar Card", "PAN Card", "Bank Account", "OTP"
    detected: bool
    sensitivity: str # "Very High", "High", "Medium", "Low"
    reason: str
    recommended_action: str

class ModuleStatus(BaseModel):
    status: str # "safe", "caution", "danger"
    headline: str
    summary: str
    key_signals: List[str]

class BlackBoxQuadrant(BaseModel):
    risk_signals: List[Dict[str, str]]
    positive_signals: List[Dict[str, str]]
    missing_information: List[Dict[str, str]]
    recommended_verification: List[Dict[str, str]]
    why_this_matters: str

class TrustProfileResult(BaseModel):
    id: str
    opportunity_type: str
    organization_name: str
    website_url: Optional[str] = ""
    overall_risk_level: str # "LOW CONCERN" (Green), "NEEDS REVIEW" (Yellow), "HIGH RISK" (Red)
    overall_risk_badge: str # "🟢 LOW CONCERN", "🟡 NEEDS REVIEW", "🔴 HIGH RISK"
    trust_score: int # 0 to 100
    score_explanation: str
    is_live_ai: bool
    analysis_mode_label: str # "AI Analysis" or "Smart Trust Analysis Engine"

    # The 5 Modules Behind the Scenes
    modules: Dict[str, ModuleStatus]

    # Detailed Evidence
    evidence_list: List[EvidenceItem]

    # Opportunity Black Box
    black_box: Optional[Dict[str, Any]] = None

    # Safe Opportunity QR Payload
    safe_qr_payload: Optional[Dict[str, Any]] = None

    # Identity Firewall
    identity_firewall: List[IdentityItem]

    # Website & Organization Checks
    website_analysis: Optional[Dict[str, Any]] = None
    organization_check: Optional[Dict[str, Any]] = None

    # Document Intelligence
    document_intelligence: Optional[Dict[str, Any]] = None

    # Safety Matrix & Checklist
    before_you_share_questions: List[str]
    safe_sharing_table: List[Dict[str, str]]

    # Next Actions
    recommended_actions: List[str]
    safe_communication_script: Optional[str] = None
    created_at: str

# ----------------- ADVANCED NEW FEATURE MODELS ----------------- #

class RecruiterPassRequest(BaseModel):
    recruiter_name: Optional[str] = "Recruiter"
    company_name: Optional[str] = ""
    claimed_company: Optional[str] = ""
    recruiter_email: Optional[str] = ""
    company_website: Optional[str] = ""
    contact_platform: Optional[str] = "LinkedIn InMail"
    platform_channel: Optional[str] = "LinkedIn InMail"
    role_offered: Optional[str] = "Software Engineer"
    documents_requested: Optional[str] = ""
    registration_fee_demanded: Optional[bool] = False
    fee_demanded: Optional[bool] = False
    job_url: Optional[str] = ""
    linkedin_url: Optional[str] = ""
    contact_number: Optional[str] = ""
    job_description: Optional[str] = ""

class RecruiterPassResult(BaseModel):
    id: str
    recruiter_name: str
    organization_name: str
    platform_channel: str
    role_offered: str
    verification_status: str
    pass_badge: str
    authenticity_score: int
    summary: str
    safe_action: str
    verified_signals: List[str]
    user_should_verify: List[str]
    risk_signals: List[str]
    created_at: str

class EmergencyExposureRequest(BaseModel):
    selected_exposure: Optional[List[str]] = []
    exposure_types: Optional[List[str]] = []
    incident_type: Optional[str] = "Information shared"
    entity_name: Optional[str] = ""
    approximate_amount_lost: Optional[str] = ""
    incident_context: Optional[str] = ""
    details: Optional[str] = ""

class EmergencyChecklistItem(BaseModel):
    id: str
    category: str # "Priority", "Containment", "Security", "Documentation", "Reporting"
    title: str
    instructions: str
    criticality: str # "critical", "high", "medium"
    completed: bool = False
    action_link: Optional[str] = None
    action_label: Optional[str] = None

class EmergencyResponsePlan(BaseModel):
    incident_id: str
    urgency_badge: str
    title: str
    summary: str
    anti_recovery_warning: str
    checklist: List[EmergencyChecklistItem]
    quick_dial_actions: List[Dict[str, str]]
    created_at: str


# ----------------- CAMPUS SHEVAULT MODE MODELS ----------------- #

class CampusVerificationRequest(BaseModel):
    college_name: str
    company_name: str
    placement_officer_name: Optional[str] = "Placement Cell Coordinator"
    role_offered: Optional[str] = "Internship / Full-Time Role"
    drive_title: Optional[str] = "Campus Placement Drive"
    recruiter_email: Optional[str] = ""
    company_website: Optional[str] = ""
    communication_mode: Optional[str] = "Official Placement Cell Portal"
    zero_fee_placement_policy: Optional[bool] = True
    original_document_retention_policy: Optional[bool] = True
    opportunity_details: Optional[str] = ""
    stipend_amount: Optional[str] = ""
    has_training_fee: Optional[bool] = False
    requires_original_docs: Optional[bool] = False
    drive_details: Optional[str] = ""

class CampusVerificationResult(BaseModel):
    id: str
    certificate_id: str
    college_name: str
    placement_officer_name: str
    company_name: str
    role_offered: str
    clearance_status: str
    clearance_badge: str
    trust_score: int
    audit_summary: str
    student_notice_template: str
    pipeline_steps: List[Dict[str, Any]]
    placement_advisories: List[str]
    risk_factors: List[str]
    verification_date: str
    created_at: str
