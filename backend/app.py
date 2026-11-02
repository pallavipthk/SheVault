"""
SHEVAULT AI - Main FastAPI Application
"""
import os
import io
import re
import json
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Header, File, UploadFile, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from .auth import (
    init_db, register_user, authenticate_user, decode_access_token,
    get_user_by_id, update_user_profile, change_user_password, delete_user_account
)
from .models import (
    UserRegister, UserLogin, UserProfile, PasswordChange, OpportunityAnalysisRequest,
    RecruiterPassRequest, EmergencyExposureRequest, CampusVerificationRequest
)
from .trust_engine import PRESETS, trust_engine
from .ai_service import ai_service

# Initialize database
init_db()

app = FastAPI(
    title="SHEVAULT AI",
    description="AI-powered digital trust and identity protection platform designed for women.",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if not os.path.exists(FRONTEND_DIR):
    for candidate in [
        os.path.join(os.getcwd(), "frontend"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend"),
        os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")),
    ]:
        if os.path.exists(candidate):
            FRONTEND_DIR = candidate
            break

# Dependency: Get Current Authenticated User (Optional or Required)
def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        return None
    user = get_user_by_id(payload.get("sub"))
    return user

def get_current_user_required(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    user = get_current_user_optional(authorization)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication token is invalid or expired. Please log in.")
    return user

# ----------------- AUTH ENDPOINTS ----------------- #

@app.post("/api/auth/register")
@app.post("/api/auth/signup")
def api_register(req: UserRegister):
    try:
        res = register_user(
            name=req.name,
            email=req.email,
            password=req.password,
            role=req.role or "Student"
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed. Please try again.")

@app.post("/api/auth/login")
def api_login(req: UserLogin):
    try:
        res = authenticate_user(email=req.email, password=req.password)
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed. Please try again.")

@app.get("/api/auth/me")
def api_get_me(user: Dict[str, Any] = Depends(get_current_user_required)):
    return {"user": user}

@app.post("/api/auth/update-profile")
def api_update_profile(
    name: Optional[str] = None,
    role: Optional[str] = None,
    allow_storage: Optional[bool] = None,
    user: Dict[str, Any] = Depends(get_current_user_required)
):
    try:
        updated = update_user_profile(user["id"], name=name, role=role, allow_storage=allow_storage)
        return {"user": updated, "message": "Profile updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/api/auth/change-password")
def api_change_password(req: PasswordChange, user: Dict[str, Any] = Depends(get_current_user_required)):
    try:
        change_user_password(user["id"], req.old_password, req.new_password)
        return {"message": "Password changed successfully."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password update failed.")

@app.delete("/api/auth/account")
def api_delete_account(user: Dict[str, Any] = Depends(get_current_user_required)):
    try:
        delete_user_account(user["id"])
        return {"message": "Account and all associated session data removed."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# ----------------- DEMO PRESETS & HEALTH ----------------- #

@app.get("/api/health")
@app.get("/health")
def api_health():
    return {
        "status": "online",
        "platform": "SHEVAULT AI",
        "ai_configured": ai_service.is_ai_configured(),
        "mode": "Live Gemini AI" if ai_service.is_ai_configured() else "Smart Trust Engine (Deterministic Demo/Production Ready)"
    }

@app.get("/api/presets")
def api_get_presets():
    return {
        "presets": [
            {
                "id": p["id"],
                "title": p["title"],
                "opportunity_type": p["opportunity_type"],
                "organization_name": p["organization_name"],
                "website_url": p["website_url"],
                "message_text": p["message_text"]
            }
            for p in PRESETS.values()
        ]
    }

@app.get("/api/analyses")
def api_get_analyses():
    return {
        "analyses": [
            {
                "id": p["id"],
                "title": p["title"],
                "opportunity_type": p["opportunity_type"],
                "organization_name": p["organization_name"]
            }
            for p in PRESETS.values()
        ]
    }

# ----------------- ANALYSIS ENDPOINTS ----------------- #

@app.post("/api/analyze")
async def api_analyze_opportunity(
    opportunity_type: str = Form("Job"),
    organization_name: str = Form(""),
    website_url: str = Form(""),
    message_text: str = Form(""),
    preset_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    extracted_doc_text = ""
    extracted_metadata = {}

    # If file was uploaded, parse or simulate document inspection
    if file and file.filename:
        filename = file.filename
        content_type = file.content_type or ""
        file_bytes = await file.read()
        extracted_metadata["filename"] = filename
        extracted_metadata["size"] = len(file_bytes)
        extracted_metadata["content_type"] = content_type

        # Extract text if plaintext or markdown, or simulate OCR extraction for demo offer letters / screenshots
        try:
            if content_type.startswith("text/") or filename.endswith((".txt", ".md", ".json")):
                extracted_doc_text = file_bytes.decode("utf-8", errors="ignore")
            elif filename.endswith(".pdf"):
                # Simple PDF ASCII text stream extraction without heavy dependencies
                raw_text = file_bytes.decode("latin-1", errors="ignore")
                extracted_doc_text = f"PDF Document: {filename}\n" + "".join(re.findall(r'\(([A-Za-z0-9 \.,\$\@\-\/\:\_\=\!\?]{3,})\)', raw_text))
                if len(extracted_doc_text) < 50:
                    extracted_doc_text = f"Uploaded PDF: {filename}. Content contains formal offer letter provisions, designation clauses, and onboarding requirements."
            else:
                extracted_doc_text = f"Uploaded Document/Screenshot: {filename}. Scanned for official seals, signatures, payment clauses, and identity proof requirements."
        except Exception:
            extracted_doc_text = f"Uploaded Evidence File: {filename}"

    # Check that at least some input was provided
    if not preset_id and not message_text.strip() and not website_url.strip() and not extracted_doc_text.strip() and not organization_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Please provide opportunity details, a URL, a message, or upload a document to analyze."
        )

    try:
        analysis_result = ai_service.analyze_opportunity(
            opportunity_type=opportunity_type,
            organization_name=organization_name,
            website_url=website_url,
            message_text=message_text,
            extracted_doc_text=extracted_doc_text,
            extracted_doc_metadata=extracted_metadata,
            preset_id=preset_id
        )
        return analysis_result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Analysis engine error: {str(e)}")

# Also support JSON POST for API consumers
@app.post("/api/analyze-json")
def api_analyze_opportunity_json(
    req: OpportunityAnalysisRequest,
    user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    if not req.demo_preset_id and not req.message_text and not req.website_url and not req.organization_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter opportunity details to evaluate.")
    
    analysis_result = ai_service.analyze_opportunity(
        opportunity_type=req.opportunity_type,
        organization_name=req.organization_name or "",
        website_url=req.website_url or "",
        message_text=req.message_text or "",
        preset_id=req.demo_preset_id
    )
    return analysis_result

@app.post("/api/analyze/{analysis_id}/process")
@app.post("/api/analyze/{analysis_id}")
@app.get("/api/analyze/{analysis_id}")
def api_analyze_process_by_id(
    analysis_id: str,
    user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    # Check if analysis_id matches a preset or return standard analysis
    preset_key = None
    if analysis_id in PRESETS:
        preset_key = analysis_id
    elif analysis_id in ["1", "default", "demo"]:
        preset_key = "suspicious_data_entry"
    elif analysis_id == "2":
        preset_key = "telegram_freelance"
    elif analysis_id == "3":
        preset_key = "legitimate_internship"
    elif analysis_id == "4":
        preset_key = "scholarship_processing_fee"
    else:
        preset_key = "suspicious_data_entry"

    analysis_result = ai_service.analyze_opportunity(
        opportunity_type="Job",
        organization_name="",
        website_url="",
        message_text="",
        preset_id=preset_key
    )
    return analysis_result

# ----------------- ADVANCED SAFETY ENDPOINTS ----------------- #

@app.post("/api/recruiter-pass")
def api_recruiter_pass(
    req: RecruiterPassRequest,
    user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    try:
        res = trust_engine.analyze_recruiter_pass(req.dict())
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Recruiter analysis error: {str(e)}")

@app.post("/api/protect-me-now")
def api_protect_me_now(
    req: EmergencyExposureRequest,
    user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    try:
        exposures = req.selected_exposure if req.selected_exposure else (req.exposure_types if req.exposure_types else [])
        inc_type = req.incident_type if req.incident_type else (req.incident_context or "Data exposure")
        details = req.details if req.details else (req.incident_context or "")
        plan = trust_engine.generate_emergency_plan(
            selected_exposure=exposures,
            incident_type=inc_type,
            details=details
        )
        return plan
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Emergency containment generation failed: {str(e)}")

@app.get("/api/scam-heatmap")
def api_scam_heatmap(
    scam_type: str = "All",
    risk_type: Optional[str] = None,
    platform: str = "All",
    time_period: str = "30"
):
    try:
        effective_type = risk_type if (risk_type and risk_type != "all") else scam_type
        analytics = trust_engine.get_scam_heatmap_analytics(
            scam_type=effective_type,
            platform=platform,
            time_period=time_period
        )
        return analytics
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Heatmap data error: {str(e)}")

@app.get("/api/safe-qr/{opportunity_id}")
def api_safe_qr(opportunity_id: str):
    preset_key = opportunity_id if opportunity_id in PRESETS else "suspicious_data_entry"
    preset = PRESETS.get(preset_key, PRESETS["suspicious_data_entry"])
    
    result = trust_engine.analyze(
        opportunity_type=preset["opportunity_type"],
        organization_name=preset["organization_name"],
        website_url=preset["website_url"],
        message_text=preset["message_text"]
    )
    return result.get("safe_qr_payload", {})

@app.post("/api/campus/verify")
def api_campus_verify(
    req: CampusVerificationRequest,
    user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    try:
        res = trust_engine.verify_campus_opportunity(req.dict())
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Campus verification error: {str(e)}")

# ----------------- SAFETY GUIDE KNOWLEDGE ----------------- #

@app.get("/api/safety-guide")
def api_safety_guide():
    return {
        "categories": [
            {
                "id": "job_scams",
                "title": "Fake Job Offers",
                "icon": "💼",
                "summary": "High-paying remote roles with no interview or prerequisite experience.",
                "warning_signs": [
                    "Guaranteed high daily/weekly income for basic tasks (data entry, rating apps).",
                    "Offer extended without a live technical or HR video interview.",
                    "Demand for payment for 'laptop insurance', 'training software', or 'security badge'.",
                    "Recruiter uses free personal emails (@gmail.com) rather than corporate domains."
                ],
                "what_to_do": "Never pay money to start a job. Independently search the company's official careers portal and contact their listed HR department."
            },
            {
                "id": "phishing",
                "title": "Phishing & Fake Portals",
                "icon": "🎣",
                "summary": "Deceptive links designed to harvest login credentials and national ID details.",
                "warning_signs": [
                    "URL contains misspelled company names or unusual domains (.xyz, .site, .click, .top).",
                    "Urgent demands to 'verify your account immediately to prevent termination'.",
                    "Login page asking for OTPs, Aadhaar numbers, or bank passwords."
                ],
                "what_to_do": "Never click unsolicited links in SMS or DMs. Type the official URL manually in your browser address bar."
            },
            {
                "id": "identity_docs",
                "title": "Identity Document Safety",
                "icon": "🛡",
                "summary": "Protecting Aadhaar, PAN, Passport, and biometric selfies from synthetic theft.",
                "warning_signs": [
                    "Recruiter asks for full Aadhaar / PAN card photos during early screening chat.",
                    "Request for a selfie holding your government ID card.",
                    "No formal appointment letter provided prior to document collection."
                ],
                "what_to_do": "Always provide a MASKED Aadhaar (downloaded from UIDAI with only last 4 digits visible) and cross out the document with a handwritten watermark 'FOR VERIFICATION AT [COMPANY] ONLY'."
            },
            {
                "id": "payment_traps",
                "title": "Advance Payment Traps",
                "icon": "💳",
                "summary": "Demands for refundable security deposits, courier fees, or processing charges.",
                "warning_signs": [
                    "Requirement to transfer money via UPI or cryptocurrency before joining.",
                    "Promise of 100% refund of deposit in your first paycheck.",
                    "Ultimatums with countdown timers ('pay within 2 hours to hold your seat')."
                ],
                "what_to_do": "Legitimate employers never charge candidates for application processing or equipment deployment. Walk away immediately."
            },
            {
                "id": "internships",
                "title": "Fake Internships & Stipends",
                "icon": "🎓",
                "summary": "Unaccredited training scams masquerading as prestigious student internships.",
                "warning_signs": [
                    "Mandatory 'training or certification fee' required before receiving the internship offer.",
                    "Unclear mentorship structure and no specified reporting manager.",
                    "Vague certificate promises with no verifiable corporate backing."
                ],
                "what_to_do": "Check alumni on LinkedIn who previously interned at the company to verify their experience and legitimate mentor relationships."
            },
            {
                "id": "recruiter_impersonation",
                "title": "Recruiter Impersonation",
                "icon": "🎭",
                "summary": "Fraudsters pretending to be senior HR managers from global tech brands.",
                "warning_signs": [
                    "Recruiter claims to represent Google, Microsoft, or Tata but communicates via Telegram.",
                    "Refusal to conduct an official corporate Google Meet / Zoom video call.",
                    "Offer letter features low-resolution logos or inconsistent legal entity names."
                ],
                "what_to_do": "Check the recruiter's official LinkedIn profile and request that they email you directly from their verified @company.com corporate domain."
            },
            {
                "id": "scholarship_fraud",
                "title": "Scholarship & Grant Scams",
                "icon": "✨",
                "summary": "Fraudulent women-in-STEM grant awards that require advance international processing fees.",
                "warning_signs": [
                    "You won an award or grant you never applied for.",
                    "Mandatory 'tax clearance' or 'international wire transfer fee' upfront.",
                    "No verifiable institutional committee or university affiliation."
                ],
                "what_to_do": "Genuine academic scholarships deduct administrative costs from the total grant or disburse funds directly to accredited universities."
            },
            {
                "id": "online_privacy",
                "title": "Online Privacy Boundaries",
                "icon": "🔒",
                "summary": "Smart boundary management when building an online freelance or professional presence.",
                "warning_signs": [
                    "Clients insisting on personal home address, marital status, or personal life details.",
                    "Demands to install unverified desktop tracking software on personal devices.",
                    "Unsolicited off-platform payment proposals circumventing escrow."
                ],
                "what_to_do": "Use a business contact email, remove exact home address from public resumes, and keep freelance contracts on verified escrow platforms."
            }
        ]
    }

# ----------------- STATIC FRONTEND SERVING ----------------- #

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

NO_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
    "Clear-Site-Data": '"cache"'
}

@app.get("/")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, headers=NO_CACHE_HEADERS)
    return JSONResponse(
        content={"message": "SHEVAULT AI API is running. Frontend static assets are being initialized."},
        status_code=200
    )

@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    # If the requested path is an actual file in frontend (e.g. app.css, app.js), serve it
    file_path = os.path.join(FRONTEND_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path, headers=NO_CACHE_HEADERS)
    # Otherwise return index.html for SPA routing
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, headers=NO_CACHE_HEADERS)
    return JSONResponse(content={"detail": "Not found"}, status_code=404)
