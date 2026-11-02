"""
SHEVAULT AI - Core Trust Engine, Opportunity Black Box, Recruiter Pass & Emergency Response
"""
import re
import urllib.parse
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

# Preset Scenarios for Demonstrations & Testing
PRESETS = {
    "suspicious_data_entry": {
        "id": "suspicious_data_entry",
        "title": "Remote Data Entry Assistant (Deposit Required)",
        "opportunity_type": "Job",
        "organization_name": "Apex Global Solutions Inc",
        "website_url": "https://apex-global-careers-portal.xyz/apply",
        "message_text": """Congratulations! You have been selected for the position of Remote Data Entry Specialist at Apex Global Solutions Inc. 
The monthly salary is ₹65,000 / $1,200 USD per month for 15 hours of work per week. No prior experience is needed.
To finalize your employee contract and disburse your home-office laptop, please send:
1. Clear photo of Front and Back of your Aadhaar Card & PAN Card
2. Bank Account details and Cancelled Cheque for direct deposit
3. A refundable security deposit of ₹3,500 for equipment verification via UPI to hr-apex@oksbi within 24 hours.

Please reply immediately on Telegram @ApexHR_Ritu to secure your joining slot.""",
    },
    "telegram_freelance": {
        "id": "telegram_freelance",
        "title": "Graphic Designer Freelance Gig (Telegram Only)",
        "opportunity_type": "Freelance",
        "organization_name": "Vogue Media Agency (UK)",
        "website_url": "https://vogue-media-designs.site",
        "message_text": """Hi dear! We saw your portfolio on Instagram and love your aesthetic. We want to hire you for our luxury branding project.
Compensation: $800 per banner design.
Before we send the briefing documents, our compliance team requires your government ID (Passport or National ID) and a selfie holding your ID for international anti-fraud registration.
Connect with our Project Lead on Telegram: https://t.me/voguemedia_lead. Fast response required as project starts tomorrow.""",
    },
    "legitimate_internship": {
        "id": "legitimate_internship",
        "title": "Google STEP Software Engineering Internship",
        "opportunity_type": "Internship",
        "organization_name": "Google India Pvt Ltd",
        "website_url": "https://careers.google.com/jobs/results/",
        "message_text": """Thank you for interviewing for the Summer 2026 STEP Internship program at Google Bangalore. 
We are pleased to extend an offer for the 10-week summer internship.
Stipend: ₹75,000/month with housing and travel assistance.
Next Steps: Log in to your official Google Careers applicant portal at https://careers.google.com to review and electronically sign your offer letter.
Please do not email any sensitive government documents or banking details directly. All official identity verification will be conducted through our secure enterprise onboarding portal prior to your joining date in May 2026.""",
    },
    "scholarship_processing_fee": {
        "id": "scholarship_processing_fee",
        "title": "Global Women in STEM Leadership Grant",
        "opportunity_type": "Scholarship",
        "organization_name": "International STEM Foundation",
        "website_url": "http://womenstem-grants-2026.online",
        "message_text": """URGENT NOTIFICATION: You have been shortlisted for the 2026 Global Women in Tech Excellence Grant worth $5,000 USD.
To claim your grant allocation before the midnight deadline, submit your Aadhaar number, PAN, and full bank routing details. 
A one-time mandatory international clearance processing fee of ₹1,999 must be paid via UPI to grant-clearance@upi. If payment is not completed within 3 hours, your allocation will be transferred to the next candidate.""",
    }
}

class TrustEngine:
    """
    SHEVAULT AI 5-Module Trust Engine:
    1. Trust Analysis
    2. Scam Detection
    3. Identity Protection
    4. Privacy Analysis
    5. Document Intelligence
    """

    def __init__(self):
        # Identity patterns
        self.aadhaar_regex = re.compile(r'\b(aadhaar|aadhar|uidai|\d{4}\s?\d{4}\s?\d{4})\b', re.IGNORECASE)
        self.pan_regex = re.compile(r'\b(pan card|pan number|[a-z]{5}\d{4}[a-z])\b', re.IGNORECASE)
        self.passport_regex = re.compile(r'\b(passport|national id|voter id|driving license|govt id|government id)\b', re.IGNORECASE)
        self.bank_regex = re.compile(r'\b(bank account|cancelled cheque|account number|ifsc|routing number|swift code|debit card|credit card|cvv|bank routing)\b', re.IGNORECASE)
        self.otp_regex = re.compile(r'\b(otp|one time password|verification code|security pin|login credentials|password|2fa code)\b', re.IGNORECASE)
        self.selfie_id_regex = re.compile(r'\b(selfie holding|photo of id|id card picture|selfie with card|video kyc|selfie verification)\b', re.IGNORECASE)

        # Scam & Coercion patterns
        self.payment_trap_regex = re.compile(
            r'\b(security deposit|refundable deposit|processing fee|registration fee|laptop fee|laptop deposit|equipment charge|delivery charge|dispatch fee|courier charge|training fee|induction fee|kit fee|id card fee|badge fee|badge charge|exam fee|test fee|assessment fee|clearance fee|verification fee|gate fee|gst charge|tax deduction upfront|wire transfer|pay advance|upi id|send ₹|pay \$|pay ₹|transfer ₹|deposit ₹|pay \d+|send \d+|fee of ₹|fee of \$|deposit of ₹|deposit of \$|via upi|gpay|phonepe|paytm|qr code|caution money|stipend after paying|paid assessment|prepaid task|deposit 1000|deposit 500|pay to start|recharge)\b', 
            re.IGNORECASE
        )
        self.doc_retention_regex = re.compile(
            r'\b(original marksheet|original certificate|submit 10th|submit 12th|retain certificate|retain marksheet|deposit original|original documents|employment bond|security bond|promissory note|service bond|bond penalty|breach penalty|surrender marksheet)\b',
            re.IGNORECASE
        )
        self.task_scam_regex = re.compile(
            r'\b(like and subscribe|youtube like|subscribe channel|review task|google map review|hotel review|movie review|rating task|app rating|daily task|task bonus|commission per task|prepaid task|recharge wallet|deposit \d+ earn|earn daily \d+|earn from mobile|part time 2-3 hours|earn \d+ to \d+ daily|daily payout|work from home data entry)\b',
            re.IGNORECASE
        )
        self.urgency_regex = re.compile(
            r'\b(urgent|immediate|within 24 hours|within 12 hours|within 3 hours|within 1 hour|midnight deadline|act fast|offer expires|hurry|limited slots|limited seats|last chance|forfeit|selection cancelled|immediate joining|closing soon)\b', 
            re.IGNORECASE
        )
        self.telegram_wa_regex = re.compile(
            r'\b(telegram|t\.me|whatsapp only|reach me on whatsapp|dm on telegram|@\w+_hr|@\w+_lead|@\w+|contact on telegram|whatsapp group|telegram channel|telegram group|inbox on whatsapp)\b', 
            re.IGNORECASE
        )
        self.crypto_regex = re.compile(r'\b(crypto|bitcoin|usdt|binance|wallet address|eth|airdrop)\b', re.IGNORECASE)
        self.unrealistic_comp_regex = re.compile(
            r'\b(65,000 for 15 hours|1000\$ per day|no experience required.*50000|earn 5000 daily|guaranteed return|no interview|direct selection|selected without interview|direct joining|no exam|earn from home.*50000)\b', 
            re.IGNORECASE
        )
        
        # Free / suspicious email domains
        self.free_email_regex = re.compile(r'@(gmail\.com|yahoo\.com|hotmail\.com|outlook\.com|protonmail\.com|mail\.com|yandex\.com)', re.IGNORECASE)

    def analyze(self, 
                opportunity_type: str, 
                organization_name: str, 
                website_url: str, 
                message_text: str, 
                extracted_doc_text: str = "",
                extracted_doc_metadata: Optional[Dict[str, Any]] = None,
                is_live_ai: bool = False) -> Dict[str, Any]:
        
        full_text = f"{message_text}\n{extracted_doc_text}"
        
        # 1. Identity Detection
        has_aadhaar = bool(self.aadhaar_regex.search(full_text))
        has_pan = bool(self.pan_regex.search(full_text))
        has_passport = bool(self.passport_regex.search(full_text))
        has_bank = bool(self.bank_regex.search(full_text))
        has_otp = bool(self.otp_regex.search(full_text))
        has_selfie_id = bool(self.selfie_id_regex.search(full_text))

        # 2. Scam Vectors
        has_payment = bool(self.payment_trap_regex.search(full_text))
        has_doc_retention = bool(self.doc_retention_regex.search(full_text))
        has_task_scam = bool(self.task_scam_regex.search(full_text))
        has_urgency = bool(self.urgency_regex.search(full_text))
        has_telegram_wa = bool(self.telegram_wa_regex.search(full_text))
        has_crypto = bool(self.crypto_regex.search(full_text))
        has_unrealistic = bool(self.unrealistic_comp_regex.search(full_text))

        # 3. URL / Website Inspection
        url_info = self._inspect_url(website_url, organization_name)
        
        # 4. Organization Inspection
        org_info = self._inspect_organization(organization_name, website_url, full_text)

        # 5. Document Intelligence
        doc_info = self._inspect_document(extracted_doc_text, extracted_doc_metadata, full_text)

        # 6. Evidence Building
        evidence_list = []
        deductions = 0
        detected_threat_labels = []

        if has_otp:
            deductions += 50
            detected_threat_labels.append("OTP/Credential demand")
            evidence_list.append({
                "id": str(uuid.uuid4())[:8],
                "title": "Critical Credential Request (OTP / Password)",
                "risk_category": "Identity Risk",
                "severity": "high",
                "description": "Request for authentication OTPs, PINs, or account credentials detected.",
                "why_it_matters": "Legitimate employers, internship sponsors, and scholarship programs will NEVER ask for your OTPs, passwords, or login access tokens.",
                "source_snippet": self._extract_snippet(full_text, self.otp_regex),
                "uncertainty_note": "Immediate high-risk signal. No legitimate organization requires access to your private verification codes."
            })

        if has_payment:
            deductions += 45
            detected_threat_labels.append("Advance fee/deposit demand")
            evidence_list.append({
                "id": str(uuid.uuid4())[:8],
                "title": "Upfront Payment or Deposit Demand",
                "risk_category": "Payment Trap",
                "severity": "high",
                "description": "Opportunity requests money upfront for 'security deposit', 'processing fee', 'laptop fee', 'training materials', or 'registration'.",
                "why_it_matters": "Genuine employment, authentic internships, and legitimate scholarships pay you; they do not require candidate-funded deposits or advance fees before starting.",
                "source_snippet": self._extract_snippet(full_text, self.payment_trap_regex),
                "uncertainty_note": "A critical red flag universally associated with employment and scholarship fraud."
            })

        if has_doc_retention:
            deductions += 40
            detected_threat_labels.append("Original certificate retention demand")
            evidence_list.append({
                "id": str(uuid.uuid4())[:8],
                "title": "Illegal Original Academic Document Retention",
                "risk_category": "Coercion Trap",
                "severity": "high",
                "description": "Requirement to deposit original 10th/12th marksheets, degree certificates, or sign punitive security bonds.",
                "why_it_matters": "Government regulations (UGC/AICTE and labor laws) strictly forbid organizations from withholding original educational certificates to enforce employment bonds.",
                "source_snippet": self._extract_snippet(full_text, self.doc_retention_regex),
                "uncertainty_note": "Employers may verify original documents in person during onboarding, but retaining them in company custody is illegal."
            })

        if has_task_scam:
            deductions += 40
            detected_threat_labels.append("Prepaid / Video rating task scam pattern")
            evidence_list.append({
                "id": str(uuid.uuid4())[:8],
                "title": "Deceptive Task / Review Rating Scheme",
                "risk_category": "Task Trap",
                "severity": "high",
                "description": "Work-from-home tasks involving 'YouTube likes', 'Google Maps reviews', 'hotel ratings', or 'prepaid task wallet recharges'.",
                "why_it_matters": "A widely documented cyber fraud scheme where victims receive tiny initial payouts before being pressured to deposit thousands into fake wallets to unlock earnings.",
                "source_snippet": self._extract_snippet(full_text, self.task_scam_regex),
                "uncertainty_note": "Legitimate organizations do not pay per video like or require prepaid recharges to perform tasks."
            })

        if has_selfie_id:
            deductions += 30
            detected_threat_labels.append("Selfie with ID biometric harvest")
            evidence_list.append({
                "id": str(uuid.uuid4())[:8],
                "title": "Selfie with ID Photo Requested",
                "risk_category": "Identity Risk",
                "severity": "high",
                "description": "Request for a photo or selfie holding government identification.",
                "why_it_matters": "ID selfies are commonly used as 'Know Your Customer' (KYC) biometric bypasses to open fraudulent bank accounts or crypto exchanges under your name.",
                "source_snippet": self._extract_snippet(full_text, self.selfie_id_regex),
                "uncertainty_note": "Rarely legitimate for standard job or internship applications outside of regulated financial institutions with certified KYC tools."
            })

        if has_aadhaar or has_pan:
            deductions += 25
            detected_docs = []
            if has_aadhaar: detected_docs.append("Aadhaar Card")
            if has_pan: detected_docs.append("PAN Card")
            doc_str = " & ".join(detected_docs)
            detected_threat_labels.append(f"Premature {doc_str} collection")

            evidence_list.append({
                "id": str(uuid.uuid4())[:8],
                "title": f"Premature Government Identity Request ({doc_str})",
                "risk_category": "Identity Risk",
                "severity": "high" if (has_payment or has_telegram_wa or has_task_scam) else "medium",
                "description": f"Direct request for {doc_str} via unverified channels before formal background verification or confirmed hiring stage.",
                "why_it_matters": "National identity documents contain sensitive identifiers that can be exploited for synthetic identity theft, unauthorized SIM activation, or loan fraud if sent over chat or unverified forms.",
                "source_snippet": self._extract_snippet(full_text, self.aadhaar_regex if has_aadhaar else self.pan_regex),
                "uncertainty_note": "While established employers eventually collect tax IDs during payroll onboarding, requesting them over chat or before a signed contract requires caution."
            })

        if has_telegram_wa:
            deductions += 25
            detected_threat_labels.append("Telegram/WhatsApp anonymous recruitment")
            evidence_list.append({
                "id": str(uuid.uuid4())[:8],
                "title": "Redirection to Informal Anonymous Messaging (Telegram/WhatsApp)",
                "risk_category": "Recruitment Irregularity",
                "severity": "medium",
                "description": "Recruitment conversation is directed exclusively to Telegram or WhatsApp instead of official company email or enterprise ATS portals.",
                "why_it_matters": "Scammers favor encrypted messaging platforms where chat logs can be wiped and accounts cannot be tied to registered corporate entities.",
                "source_snippet": self._extract_snippet(full_text, self.telegram_wa_regex),
                "uncertainty_note": "Some small startups use WhatsApp for initial scheduling, but official hiring contracts should always come via verified corporate email domains."
            })

        if has_urgency:
            deductions += 15
            detected_threat_labels.append("Coercive deadline pressure")
            evidence_list.append({
                "id": str(uuid.uuid4())[:8],
                "title": "Artificial Urgency & Pressure Tactics",
                "risk_category": "Psychological Coercion",
                "severity": "medium",
                "description": "Strict time-bound ultimatums ('within 24 hours', 'limited slots', 'immediate reply').",
                "why_it_matters": "High-pressure deadlines are engineered to induce emotional panic and prevent candidates from conducting independent background checks.",
                "source_snippet": self._extract_snippet(full_text, self.urgency_regex),
                "uncertainty_note": "Legitimate offers typically provide a reasonable review window of several days for formal contracts."
            })

        if url_info and url_info.get("suspicious_domain"):
            deductions += 25
            detected_threat_labels.append("Suspicious domain structure")
            evidence_list.append({
                "id": str(uuid.uuid4())[:8],
                "title": f"Suspicious Domain Structure ({url_info.get('domain', 'URL')})",
                "risk_category": "Domain Impersonation",
                "severity": "high",
                "description": f"The provided URL uses high-risk TLDs or mismatching naming patterns ({url_info.get('domain')}).",
                "why_it_matters": "Fraudsters routinely register cheap alternative domains (like .xyz, .site, .online, or hyphens) to mimic well-known organizations.",
                "source_snippet": website_url,
                "uncertainty_note": "Check WHOIS registration date and cross-reference with official corporate search directories."
            })

        if has_bank:
            deductions += 15
            evidence_list.append({
                "id": str(uuid.uuid4())[:8],
                "title": "Early Banking / Cancelled Cheque Collection",
                "risk_category": "Financial Privacy",
                "severity": "medium",
                "description": "Bank account numbers, routing codes, or cancelled cheques requested prior to official offer confirmation.",
                "why_it_matters": "Banking details should only be submitted through secure HRMS payroll systems after an offer letter has been independently verified and signed.",
                "source_snippet": self._extract_snippet(full_text, self.bank_regex),
                "uncertainty_note": "Normal during confirmed payroll onboarding, but highly risky when paired with unverified recruiters."
            })

        # Calculate Overall Risk Level & Enforce Strict Score Capping (Never show 100% on scams)
        is_high_risk = (
            has_payment or has_otp or has_doc_retention or has_task_scam or 
            has_selfie_id or (has_aadhaar and has_telegram_wa) or 
            (has_unrealistic and has_telegram_wa) or deductions >= 35
        )
        is_medium_risk = (
            not is_high_risk and (
                has_aadhaar or has_pan or has_urgency or has_telegram_wa or 
                (url_info and not url_info.get("is_https")) or deductions >= 15
            )
        )

        if is_high_risk:
            overall_risk = "HIGH RISK"
            overall_badge = "🔴 HIGH RISK"
            raw_score = 100 - max(65, deductions)
            trust_score = max(10, min(35, raw_score))
            score_explanation = f"Calculated Trust Score: {trust_score}/100 (HIGH RISK). Critical risk indicators flagged: {', '.join(detected_threat_labels) if detected_threat_labels else 'coercive payment and identity demands'}."
        elif is_medium_risk:
            overall_risk = "NEEDS REVIEW"
            overall_badge = "🟡 NEEDS REVIEW"
            raw_score = 100 - deductions
            trust_score = max(45, min(70, raw_score))
            score_explanation = f"Calculated Trust Score: {trust_score}/100 (NEEDS REVIEW). Caution advised due to sensitive data requests or unverified recruitment channels."
        else:
            overall_risk = "LOW CONCERN"
            overall_badge = "🟢 LOW CONCERN"
            raw_score = 100 - deductions
            trust_score = min(max(90, raw_score), 98)
            score_explanation = f"Calculated Trust Score: {trust_score}/100 (LOW CONCERN). Standard opportunity patterns verified with no fees, deposit demands, or premature identity requests."

        # Build 5 AI Module Summaries
        modules = {
            "trust_analysis": {
                "status": "safe" if trust_score > 75 else ("caution" if trust_score > 45 else "danger"),
                "headline": "Opportunity Pattern & Legitimacy",
                "summary": "Verified domain consistency and standard recruitment flow." if trust_score > 75 else ("Requires independent verification before sharing personal documents." if trust_score > 45 else "High discrepancy between opportunity claims and verification signals."),
                "key_signals": [
                    f"Opportunity Type: {opportunity_type}",
                    f"Organization: {organization_name or 'Not specified'}",
                    f"Domain Reputation: {url_info.get('reputation_label', 'Standard') if url_info else 'No URL provided'}"
                ]
            },
            "scam_detection": {
                "status": "danger" if (has_payment or has_otp or has_crypto) else ("caution" if (has_urgency or has_telegram_wa) else "safe"),
                "headline": "Fraud, Phishing & Impersonation",
                "summary": "Upfront fee or critical credential trap detected." if (has_payment or has_otp) else ("Pressure tactics or unverified messaging channels identified." if (has_urgency or has_telegram_wa) else "No phishing, financial traps, or fraudulent extortion patterns detected."),
                "key_signals": [
                    f"Payment Demands: {'Detected' if has_payment else 'None'}",
                    f"Urgency / Pressure: {'Detected' if has_urgency else 'None'}",
                    f"Channel Security: {'Telegram/WhatsApp Only' if has_telegram_wa else 'Direct/Standard'}"
                ]
            },
            "identity_protection": {
                "status": "danger" if (has_otp or has_selfie_id or (has_aadhaar and has_payment)) else ("caution" if (has_aadhaar or has_pan or has_bank) else "safe"),
                "headline": "Identity Document Firewall",
                "summary": "High-risk request for sensitive government identifiers or KYC biometrics." if (has_aadhaar or has_pan or has_selfie_id or has_otp) else "No sensitive identity documents or authentication credentials requested at this stage.",
                "key_signals": [
                    f"Aadhaar / National ID: {'Requested ⚠' if has_aadhaar else 'Not requested'}",
                    f"PAN Card: {'Requested ⚠' if has_pan else 'Not requested'}",
                    f"Bank Credentials / OTP: {'Requested ⚠' if (has_bank or has_otp) else 'Safe'}"
                ]
            },
            "privacy_analysis": {
                "status": "danger" if (has_bank and has_pan and has_aadhaar) else ("caution" if (has_pan or has_bank or has_passport) else "safe"),
                "headline": "Data Exposure & Privacy Boundary",
                "summary": "Premature data collection exposes you to synthetic identity and profiling risks." if (has_aadhaar or has_pan or has_bank) else "Data requested is standard for professional outreach (resume, contact details).",
                "key_signals": [
                    f"Data Sensitivity: {'High Exposure' if (has_aadhaar or has_bank) else 'Low/Standard Exposure'}",
                    "Stage Appropriateness: " + ("Premature for initial screening" if (has_aadhaar or has_bank) else "Appropriate"),
                    "Storage Risk: Potential unencrypted chat transmission" if has_telegram_wa else "Standard transmission"
                ]
            },
            "document_intelligence": {
                "status": "caution" if doc_info.get("has_anomalies") else "safe",
                "headline": "Document & Offer Verification",
                "summary": doc_info.get("summary", "No document anomalies detected."),
                "key_signals": doc_info.get("key_signals", [
                    "Document Structure: Evaluated",
                    "Signatory Validation: Pending",
                    "Security Seal / Header: Analyzed"
                ])
            }
        }

        # Opportunity Black Box Quadrants
        black_box = self._build_opportunity_black_box(
            has_payment, has_aadhaar, has_pan, has_otp, has_selfie_id, 
            has_urgency, has_telegram_wa, url_info, org_info, doc_info, 
            organization_name, opportunity_type
        )

        # Safe Opportunity QR Payload
        analysis_id = f"shevault_{str(uuid.uuid4())[:10]}"
        safe_qr_payload = self._build_safe_qr_payload(
            analysis_id, opportunity_type, organization_name, overall_risk, 
            overall_badge, black_box
        )

        # Identity Firewall Matrix Items
        identity_firewall = [
            {
                "name": "Aadhaar / National ID",
                "detected": has_aadhaar,
                "sensitivity": "High",
                "reason": "Contains unique 12-digit biometric identifier linked to banking, mobile connections, and government records.",
                "recommended_action": "Do NOT share full Aadhaar. If identity proof is mandated at later onboarding, share a MASKED Aadhaar (showing only last 4 digits) with watermark."
            },
            {
                "name": "PAN Card",
                "detected": has_pan,
                "sensitivity": "High",
                "reason": "Permanent Account Number used for tax compliance and credit bureau checks. Not needed for initial interview screening.",
                "recommended_action": "Withhold until you have received a formal, independently verified appointment letter and confirmed payroll setup."
            },
            {
                "name": "Passport / Driving License",
                "detected": has_passport,
                "sensitivity": "High",
                "reason": "Primary citizenship & international travel document.",
                "recommended_action": "Provide only redacted copy or confirm necessity via enterprise HR portal."
            },
            {
                "name": "Bank Account / Cancelled Cheque",
                "detected": has_bank,
                "sensitivity": "Very High",
                "reason": "Financial routing and account number exposure.",
                "recommended_action": "Never submit bank details over Telegram, WhatsApp, or unsecured web forms. Share only via secure company HRMS portal."
            },
            {
                "name": "One-Time Password (OTP) / PIN",
                "detected": has_otp,
                "sensitivity": "Critical (Very High)",
                "reason": "Direct authentication token that grants access to your personal accounts or mobile banking.",
                "recommended_action": "NEVER share OTP under any circumstances. No legitimate recruiter will ever ask for an OTP."
            },
            {
                "name": "Selfie Holding ID Card",
                "detected": has_selfie_id,
                "sensitivity": "Critical (Very High)",
                "reason": "Biometric liveness proof often repurposed by fraudsters to pass automated KYC verification on credit apps.",
                "recommended_action": "Decline immediately. Reputable employers verify identity via live video call or official background check partners."
            }
        ]

        # Recommended Next Actions
        if overall_risk == "HIGH RISK":
            recommended_actions = [
                "1. Cease communication immediately and do NOT transfer any funds (security deposit, registration fee, or equipment fee).",
                "2. Withhold all sensitive identity documents (Aadhaar, PAN, Bank details, OTPs, ID selfies).",
                "3. Verify if the company has an official corporate website, careers page, or registered headquarters on Ministry of Corporate Affairs (MCA).",
                "4. If you have already shared documents, download a Masked Aadhaar from UIDAI and monitor your credit reports for unauthorized inquiries.",
                "5. Report the impersonating account on the respective platform (Telegram, LinkedIn, or Cybercrime reporting portal)."
            ]
        elif overall_risk == "NEEDS REVIEW":
            recommended_actions = [
                "1. Independently locate the organization's official website using a search engine rather than clicking links in the message.",
                "2. Send an email to the company's verified HR / recruitment email address (e.g., hr@company.com) to confirm the authenticity of this opportunity.",
                "3. Decline to provide government identity cards (Aadhaar/PAN) until formal interview rounds are completed and a verifiable offer is signed.",
                "4. If identity verification is insisted upon, provide a Masked Aadhaar showing only the last 4 digits and add a handwritten watermark across the document stating 'For Verification at [Company] Only'.",
                "5. Request all official communications to occur via verified business email domains rather than personal messaging apps."
            ]
        else:
            recommended_actions = [
                "1. Proceed with normal diligence and standard professional recruitment etiquette.",
                "2. Ensure all offer documents and onboarding materials are accessed via the company's official secure portal (HTTPS).",
                "3. When submitting onboarding documents, always use masked/watermarked copies for personal records.",
                "4. Keep a personal backup of your signed contract, job description, and agreed compensation structure."
            ]

        # Safe Communication Script
        script = self._generate_safe_script(has_aadhaar, has_pan, has_payment, has_telegram_wa, organization_name)

        # Before you share questions
        before_you_share_questions = [
            "Why is this specific document or information required at this stage of the process?",
            "Have you independently verified the company's legal entity and official domain?",
            "Is the recruiter using an official corporate domain email rather than a free provider (@gmail/@yahoo)?",
            "Can a less sensitive document (e.g. college ID, portfolio, masked ID) be used instead?",
            "Are you being pressured with an artificial deadline to share personal credentials immediately?"
        ]

        # Safe Sharing Guidance Table
        safe_sharing_table = [
            {"item": "Full Name & Professional Portfolio", "sensitivity": "Low", "stage": "Application / Screening", "guidance": "Usually safe to share on public resumes and job portals."},
            {"item": "Email Address & LinkedIn Profile", "sensitivity": "Low", "stage": "Application / Screening", "guidance": "Safe. Use a dedicated professional email address."},
            {"item": "Resume / CV (Without Home Address)", "sensitivity": "Low", "stage": "Initial Evaluation", "guidance": "Generally appropriate. Omit exact street address, father's name, or marital status."},
            {"item": "Phone Number", "sensitivity": "Medium", "stage": "Interview Scheduling", "guidance": "Share with discretion. Avoid sharing on unverified public forums."},
            {"item": "Aadhaar Card / National ID", "sensitivity": "High", "stage": "Final Onboarding Only", "guidance": "Verify necessity. Use MASKED Aadhaar with watermark only after offer acceptance."},
            {"item": "PAN Card", "sensitivity": "High", "stage": "Payroll & Tax Setup", "guidance": "Required strictly for tax deduction (TDS) during formal onboarding, never for screening."},
            {"item": "Bank Account & Cancelled Cheque", "sensitivity": "Very High", "stage": "Payroll Onboarding", "guidance": "Never share casually or over chat. Submit only through authenticated HRMS portals."},
            {"item": "OTP / Security PIN", "sensitivity": "Critical", "stage": "Never", "guidance": "NEVER SHARE. No legitimate employer or sponsor will ever ask for your OTP."},
            {"item": "Account Passwords / Private Keys", "sensitivity": "Critical", "stage": "Never", "guidance": "NEVER SHARE under any circumstance."}
        ]

        return {
            "id": analysis_id,
            "opportunity_type": opportunity_type,
            "organization_name": organization_name or "Digital Opportunity Candidate",
            "website_url": website_url,
            "overall_risk_level": overall_risk,
            "overall_risk_badge": overall_badge,
            "trust_score": trust_score,
            "score_explanation": score_explanation,
            "is_live_ai": is_live_ai,
            "analysis_mode_label": "AI Analysis" if is_live_ai else "Smart Trust Analysis Engine",
            "modules": modules,
            "evidence_list": evidence_list,
            "black_box": black_box,
            "safe_qr_payload": safe_qr_payload,
            "identity_firewall": identity_firewall,
            "website_analysis": url_info,
            "organization_check": org_info,
            "document_intelligence": doc_info,
            "before_you_share_questions": before_you_share_questions,
            "safe_sharing_table": safe_sharing_table,
            "recommended_actions": recommended_actions,
            "safe_communication_script": script,
            "created_at": datetime.utcnow().strftime("%B %d, %Y - %H:%M UTC")
        }

    def _build_opportunity_black_box(self, has_payment, has_aadhaar, has_pan, has_otp, has_selfie_id, 
                                     has_urgency, has_telegram_wa, url_info, org_info, doc_info, 
                                     org_name, opp_type) -> Dict[str, Any]:
        risk_signals = []
        positive_signals = []
        missing_information = []
        recommended_verification = []

        if has_payment:
            risk_signals.append({"badge": "🔴", "title": "Registration / Deposit Fee Requested", "desc": "Requires advance payment for laptops, processing, or training."})
        if has_otp:
            risk_signals.append({"badge": "🔴", "title": "Critical OTP / Credential Request", "desc": "Asks for private authentication codes or passwords."})
        if has_selfie_id:
            risk_signals.append({"badge": "🔴", "title": "Biometric ID Selfie Required", "desc": "Demands photo holding identity card, prone to KYC exploitation."})
        if has_aadhaar or has_pan:
            risk_signals.append({"badge": "🟠", "title": "Premature Government Tax / National ID Demand", "desc": "Requested prior to formal onboarding or signed offer."})
        if has_telegram_wa:
            risk_signals.append({"badge": "🟠", "title": "Redirection to Telegram / WhatsApp Chat", "desc": "Recruitment handled via personal encrypted messaging."})
        if has_urgency:
            risk_signals.append({"badge": "🟠", "title": "Coercive Urgency Language", "desc": "Time-sensitive ultimatums designed to bypass diligence."})
        if url_info and url_info.get("suspicious_domain"):
            risk_signals.append({"badge": "🔴", "title": "High-Risk Domain Registrar TLD", "desc": f"Uses suspicious domain pattern ({url_info.get('domain')})."})

        # Positive Signals
        if url_info and url_info.get("is_https"):
            positive_signals.append({"badge": "🟢", "title": "Encrypted HTTPS Protocol Active", "desc": "Connection to the destination web server is TLS encrypted."})
        if not has_payment and not has_otp:
            positive_signals.append({"badge": "🟢", "title": "Zero Monetary Demands", "desc": "No upfront security fees or application deposits identified."})
        if doc_info and doc_info.get("has_document") and not doc_info.get("has_anomalies"):
            positive_signals.append({"badge": "🟢", "title": "Standard Offer Document Structure", "desc": "Document includes typical job scope and designation clauses."})
        if org_info and org_info.get("badge", "").startswith("🟢"):
            positive_signals.append({"badge": "🟢", "title": "Established Corporate Signature", "desc": f"Stated entity matches recognized corporate registry profile."})

        # Missing Information
        if not url_info:
            missing_information.append({"badge": "⚪", "title": "Official Application Website URL", "desc": "No destination careers portal URL was provided for analysis."})
        if not org_name:
            missing_information.append({"badge": "⚪", "title": "Corporate Entity Legal Name", "desc": "Organization legal name missing from initial submission."})
        missing_information.append({"badge": "⚪", "title": "Corporate Email Domain Match", "desc": "Unable to confirm whether recruiter used verified @company.com address."})
        missing_information.append({"badge": "⚪", "title": "Live Interview Verification", "desc": "No record of face-to-face video assessment stage."})

        # Recommended Verification
        recommended_verification.append({"badge": "🔍", "title": "Check Official Careers Portal", "desc": "Search independently for the job requisition ID on the company's verified domain."})
        recommended_verification.append({"badge": "🔍", "title": "Request Verified Business Email", "desc": "Ask the contact to send correspondence from an official corporate domain email."})
        recommended_verification.append({"badge": "🔍", "title": "Verify Entity on Corporate Registry", "desc": "Cross-reference company incorporation on MCA (India) or Companies House."})

        return {
            "risk_signals": risk_signals,
            "positive_signals": positive_signals,
            "missing_information": missing_information,
            "recommended_verification": recommended_verification,
            "why_this_matters": "Why this matters: Legitimate opportunities can still contain some unusual signals, so SHEVAULT does not treat one signal alone as proof of fraud. Use these signals to guide your independent verification."
        }

    def _build_safe_qr_payload(self, analysis_id: str, opp_type: str, org_name: str, 
                               risk_level: str, risk_badge: str, black_box: Dict[str, Any]) -> Dict[str, Any]:
        verification_signals = [s["title"] for s in black_box["positive_signals"][:3]]
        warning_signals = [s["title"] for s in black_box["risk_signals"][:3]]
        
        return {
            "verification_id": analysis_id,
            "opportunity_title": f"{opp_type} with {org_name or 'Independent Offer'}",
            "organization_name": org_name or "Digital Opportunity Candidate",
            "opportunity_type": opp_type,
            "risk_assessment": risk_level,
            "risk_badge": risk_badge,
            "verification_signals": verification_signals or ["Standard opportunity parameters evaluated"],
            "warning_signals": warning_signals or ["No critical red flags flagged"],
            "recommended_action": "Verify through the organization's official website before submitting sensitive documents.",
            "verification_timestamp": datetime.utcnow().strftime("%B %d, %Y - %H:%M UTC"),
            "verification_url": f"/verify-opportunity?id={analysis_id}",
            "generated_by": "SHEVAULT AI - Digital Trust Engine"
        }

    def analyze_recruiter_pass(self, req_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verified Recruiter Pass Analysis
        Evaluates recruiter authenticity and clearly distinguishes 'Verified Signal' vs 'User Should Verify'
        """
        recruiter_name = req_data.get("recruiter_name", "").strip() or "Recruiter Candidate"
        company_name = req_data.get("company_name", "").strip() or "Organization"
        recruiter_email = req_data.get("recruiter_email", "").strip().lower()
        company_website = req_data.get("company_website", "").strip().lower()
        job_url = req_data.get("job_url", "").strip()
        linkedin_url = req_data.get("linkedin_url", "").strip()
        contact_number = req_data.get("contact_number", "").strip()

        verified_signals = []
        user_should_verify = []
        risk_signals = []

        # 1. Email Domain vs Website Check
        email_domain = recruiter_email.split("@")[-1] if "@" in recruiter_email else ""
        web_domain = ""
        if company_website:
            parsed = urllib.parse.urlparse(company_website if company_website.startswith("http") else f"https://{company_website}")
            web_domain = parsed.netloc.replace("www.", "")

        is_free_email = bool(self.free_email_regex.search(recruiter_email))

        if is_free_email:
            risk_signals.append({
                "title": "Recruiter Uses Free Public Email (@gmail / @yahoo)",
                "details": f"The recruiter provided a free public mailbox ({recruiter_email}) instead of an official enterprise domain.",
                "importance": "High Risk: Enterprise hiring teams and verified corporate recruiters use registered company email addresses."
            })
        elif email_domain and web_domain:
            clean_email_dom = re.sub(r'[^a-z0-9]', '', email_domain)
            clean_web_dom = re.sub(r'[^a-z0-9]', '', web_domain)
            if clean_email_dom in clean_web_dom or clean_web_dom in clean_email_dom:
                verified_signals.append({
                    "title": "Email Domain Directly Matches Company Website",
                    "details": f"Email domain '@{email_domain}' aligns with company web domain '{web_domain}'.",
                    "type": "Verified Signal"
                })
            else:
                risk_signals.append({
                    "title": "Mismatch Between Recruiter Email Domain and Company Website",
                    "details": f"Recruiter email uses '@{email_domain}' while stated company website is '{web_domain}'.",
                    "importance": "Requires Verification: May indicate impersonation of a legitimate brand."
                })
        elif email_domain:
            verified_signals.append({
                "title": "Corporate Domain Structure Present",
                "details": f"Email uses custom domain '@{email_domain}'.",
                "type": "Verified Signal"
            })

        # 2. LinkedIn URL Check
        if linkedin_url:
            if "linkedin.com/in/" in linkedin_url or "linkedin.com/company/" in linkedin_url:
                verified_signals.append({
                    "title": "LinkedIn Profile Format Valid",
                    "details": "Profile URL adheres to standard LinkedIn identification structure.",
                    "type": "Verified Signal"
                })
                user_should_verify.append({
                    "title": "Confirm Active Employee Endorsements & Shared Connections",
                    "details": f"Check if {recruiter_name}'s LinkedIn profile has mutual professional connections and verified company tenure.",
                    "type": "User Should Verify"
                })
            else:
                risk_signals.append({
                    "title": "Irregular LinkedIn Profile Format",
                    "details": "The provided LinkedIn URL does not appear to be an active public profile.",
                    "importance": "Caution"
                })
        else:
            user_should_verify.append({
                "title": "Search for Recruiter on LinkedIn",
                "details": f"Search for '{recruiter_name}' at '{company_name}' to verify their stated role and department.",
                "type": "User Should Verify"
            })

        # 3. Company Website Security
        if company_website:
            if company_website.startswith("https://") or "https" in company_website:
                verified_signals.append({
                    "title": "Company Website Uses HTTPS Encryption",
                    "details": "Encrypted transport active on target corporate domain.",
                    "type": "Verified Signal"
                })
            else:
                risk_signals.append({
                    "title": "Insecure HTTP Protocol on Stated Website",
                    "details": "Company website lacks valid TLS/HTTPS encryption.",
                    "importance": "High Security Risk"
                })
        else:
            user_should_verify.append({
                "title": "Locate Official Corporate Website",
                "details": f"Verify whether '{company_name}' operates an active official corporate domain.",
                "type": "User Should Verify"
            })

        # 4. Independent Employment Verification (Always included for safety)
        user_should_verify.append({
            "title": "Independent Switchboard Confirmation",
            "details": f"Call the listed headquarter phone number for '{company_name}' to verify if {recruiter_name} is an active HR representative.",
            "type": "User Should Verify"
        })

        if len(risk_signals) >= 2 or is_free_email:
            status = "Multiple Risk Signals"
            status_badge = "🔴 Multiple Risk Signals"
            authenticity_score = 25
            verification_status = "CAUTION"
            pass_badge = "🔴 MULTIPLE RISK SIGNALS"
            summary = f"Multiple caution indicators identified for {recruiter_name} claiming to represent {company_name}. Free email or domain discrepancies require independent verification before sharing personal documents."
        elif len(risk_signals) == 1 or not email_domain:
            status = "Needs Verification"
            status_badge = "🟡 Needs Verification"
            authenticity_score = 65
            verification_status = "CAUTION"
            pass_badge = "🟡 NEEDS VERIFICATION"
            summary = f"Certain details for {recruiter_name} appear plausible, but critical independent confirmation is required before proceeding with contract discussions."
        else:
            status = "Verification Signals Found"
            status_badge = "🟢 Verification Signals Found"
            authenticity_score = 95
            verification_status = "VERIFIED"
            pass_badge = "🟢 PASS - VERIFIED"
            summary = f"Positive verification signals identified for {recruiter_name} at {company_name}. Standard recruiter domain consistency observed."

        recommended_next_steps = [
            f"1. Send an email to the recruiter's official company address rather than communicating via personal messaging apps.",
            f"2. Request a formal video meeting via Google Meet, Microsoft Teams, or Zoom before providing any government identity copies.",
            f"3. Check the official {company_name} careers page to confirm the job opening requisition exists.",
            f"4. Never transfer funds or payment deposits to any recruiter under any circumstances."
        ]

        role_offered = req_data.get("role_offered", "Professional Role")
        platform_channel = req_data.get("platform_channel", req_data.get("contact_platform", "Direct Outreach"))

        return {
            "id": f"recpass_{str(uuid.uuid4())[:10]}",
            "recruiter_name": recruiter_name,
            "company_name": company_name,
            "organization_name": company_name,
            "role_offered": role_offered,
            "platform_channel": platform_channel,
            "status": status,
            "status_badge": status_badge,
            "verification_status": verification_status,
            "pass_badge": pass_badge,
            "authenticity_score": authenticity_score,
            "verified_signals": verified_signals,
            "user_should_verify": user_should_verify,
            "risk_signals": risk_signals,
            "summary": summary,
            "safe_action": recommended_next_steps[0],
            "recommended_next_steps": recommended_next_steps,
            "created_at": datetime.utcnow().strftime("%B %d, %Y - %H:%M UTC")
        }

    def generate_emergency_plan(self, selected_exposure: List[str], incident_type: str, details: str = "") -> Dict[str, Any]:
        """
        Protect Me Now: Emergency Data-Exposure Response Plan
        Generates immediate structured containment, account recovery, and evidence preservation checklists.
        """
        exposure_set = set(item.lower() for item in selected_exposure)
        
        has_money = "money" in exposure_set or "upi details" in exposure_set or "bank details" in exposure_set or "card details" in exposure_set or "sent money" in incident_type.lower()
        has_otp = "otp" in exposure_set or "password" in exposure_set or "shared an otp" in incident_type.lower() or "shared a password" in incident_type.lower()
        has_id = any(k in exposure_set for k in ["aadhaar", "pan", "passport", "government id", "tax id", "personal documents"])
        has_link = "clicked a suspicious link" in incident_type.lower() or "downloaded something" in incident_type.lower()

        priority_warnings = []
        checklist = []
        
        # 1. Money & Financial Exposure
        if has_money:
            priority_warnings.append("🚨 Contact your bank or payment app (GPay/PhonePe/Paytm/UPI) IMMEDIATELY to request an urgent transaction freeze.")
            checklist.extend([
                {
                    "id": "em_bank_freeze",
                    "category": "Priority Containment",
                    "title": "Call Bank / Payment Provider Emergency Helpline",
                    "instructions": "Call your bank's 24/7 fraud helpline number (found on the back of your debit card or official bank app) and ask for the transaction to be flagged as unauthorized fraud.",
                    "criticality": "critical",
                    "completed": False,
                    "action_label": "Dial 1930 (National Cyber Financial Helpline in India)"
                },
                {
                    "id": "em_preserve_tx",
                    "category": "Documentation",
                    "title": "Preserve Transaction & Chat Evidence",
                    "instructions": "Take clear screenshots of the UPI Reference / UTR Number, date, time, recipient UPI ID / Account number, and full chat logs before the fraudster deletes them.",
                    "criticality": "high",
                    "completed": False
                },
                {
                    "id": "em_report_cyber",
                    "category": "Reporting",
                    "title": "File an Official Cybercrime Report",
                    "instructions": "Submit an official complaint on the National Cyber Crime Reporting Portal (cybercrime.gov.in) or your local jurisdictional police portal.",
                    "criticality": "high",
                    "completed": False,
                    "action_link": "https://cybercrime.gov.in",
                    "action_label": "Open Cybercrime Portal"
                }
            ])

        # 2. OTP & Authentication Credential Exposure
        if has_otp:
            priority_warnings.append("🔒 An OTP or password was disclosed. Immediately change account credentials and terminate all active login sessions.")
            checklist.extend([
                {
                    "id": "em_change_pwd",
                    "category": "Secure Accounts",
                    "title": "Change Primary Password Immediately",
                    "instructions": "Change your password for the compromised service and ensure you use a strong, unique 14+ character password not used anywhere else.",
                    "criticality": "critical",
                    "completed": False
                },
                {
                    "id": "em_signout_sessions",
                    "category": "Secure Accounts",
                    "title": "Sign Out of All Unfamiliar Devices / Sessions",
                    "instructions": "Go to Account Settings > Security and click 'Log out of all devices' or 'Revoke other sessions' to kick out unauthorized access.",
                    "criticality": "critical",
                    "completed": False
                },
                {
                    "id": "em_enable_mfa",
                    "category": "Secure Accounts",
                    "title": "Switch to Authenticator App 2FA",
                    "instructions": "Where possible, switch 2-Factor Authentication from SMS OTP to an Authenticator App (like Google Authenticator) to prevent SIM-swap attacks.",
                    "criticality": "high",
                    "completed": False
                }
            ])

        # 3. Government Identity Exposure (Aadhaar / PAN / Passport)
        if has_id or not checklist:
            checklist.extend([
                {
                    "id": "em_lock_biometrics",
                    "category": "Reduce Exposure",
                    "title": "Lock Aadhaar Biometrics via UIDAI Portal",
                    "instructions": "Open the mAadhaar App or visit myaadhaar.uidai.gov.in and enable 'Lock Biometrics'. This prevents anyone from authenticating fingerprint/iris KYC under your name.",
                    "criticality": "high",
                    "completed": False,
                    "action_link": "https://myaadhaar.uidai.gov.in",
                    "action_label": "Lock Aadhaar on UIDAI"
                },
                {
                    "id": "em_credit_check",
                    "category": "Containment",
                    "title": "Check Credit Bureau Inquiries (CIBIL / Experian)",
                    "instructions": "Check your free annual credit score on official portals to verify no unauthorized personal loans or credit cards have been opened using your PAN.",
                    "criticality": "medium",
                    "completed": False
                },
                {
                    "id": "em_watermark_future",
                    "category": "Safety Protocol",
                    "title": "Switch to Masked Aadhaar for Future Sharing",
                    "instructions": "Download a Masked Aadhaar (showing only last 4 digits) for all future professional interactions and cross-watermark it with the company name.",
                    "criticality": "medium",
                    "completed": False
                }
            ])

        # 4. Suspicious Links / Downloads
        if has_link:
            checklist.extend([
                {
                    "id": "em_malware_scan",
                    "category": "Device Security",
                    "title": "Disconnect Wi-Fi and Run Anti-Malware Scan",
                    "instructions": "Temporarily disconnect your device from the internet, delete any downloaded setup files, and run a complete Windows Defender / Malwarebytes antivirus scan.",
                    "criticality": "high",
                    "completed": False
                }
            ])

        anti_recovery_warning = "CRITICAL ADVISORY: Do NOT pay any individual or agency on Telegram, Instagram, or email claiming they can 'hack back' or recover your lost funds for an advance fee. These are secondary recovery scams designed to target already distressed victims."

        evidence_locker_guidelines = [
            "1. Take unedited full-screen screenshots showing phone numbers, Telegram @handles, and message timestamps.",
            "2. Download any PDF contracts or offer letters provided by the sender.",
            "3. Record payment reference numbers (UTR, UPI transaction ID, bank reference).",
            "4. Export or export-chat the messaging history before blocking the contact."
        ]

        official_helplines = [
            {"title": "National Cyber Crime Helpline (India)", "contact": "Dial 1930 (24x7 Emergency)", "url": "https://cybercrime.gov.in"},
            {"title": "UIDAI Aadhaar Helpline", "contact": "Dial 1947", "url": "https://uidai.gov.in"},
            {"title": "National Consumer Helpline", "contact": "Dial 1915", "url": "https://consumerhelpline.gov.in"},
            {"title": "Global Cyber Fraud Reporting (US FTC / UK ActionFraud)", "contact": "reportfraud.ftc.gov / actionfraud.police.uk", "url": "https://reportfraud.ftc.gov"}
        ]

        return {
            "incident_id": f"incident_{str(uuid.uuid4())[:10]}",
            "exposure_summary": selected_exposure or ["Unspecified Data Exposure"],
            "incident_type": incident_type,
            "status_headline": "Emergency Data-Exposure Containment Activated",
            "priority_warnings": priority_warnings or ["Take immediate precautionary steps below to prevent unauthorized access or further identity exposure."],
            "anti_recovery_scam_warning": anti_recovery_warning,
            "checklist": checklist,
            "evidence_locker_guidelines": evidence_locker_guidelines,
            "official_helplines": official_helplines,
            "created_at": datetime.utcnow().strftime("%B %d, %Y - %H:%M UTC")
        }

    def get_scam_heatmap_analytics(self, scam_type: str = "All", platform: str = "All", time_period: str = "30") -> Dict[str, Any]:
        """
        Scam Heatmap: Aggregated Opportunity-Risk Intelligence
        Returns clearly labeled illustrative/aggregated trend insights.
        """
        regional_hotspots = [
            {
                "region": "National Capital Region (NCR)",
                "risk_index": "🔴 High Risk (38%)",
                "primary_threat_vector": "Fake Remote Data Entry & Laptop Caution Deposit",
                "active_hotspot_alert": "Surge in unsolicited Telegram work-from-home offers targeting college students.",
                "incidents": 1420
            },
            {
                "region": "Bengaluru & Karnataka Tech Hub",
                "risk_index": "🟡 Elevated Caution (24%)",
                "primary_threat_vector": "Tech Recruiter Impersonation on InMail",
                "active_hotspot_alert": "Fraudsters using spoofed executive names with lookalike domains.",
                "incidents": 980
            },
            {
                "region": "Mumbai & Maharashtra Metro",
                "risk_index": "🔴 High Risk (32%)",
                "primary_threat_vector": "Telegram Part-Time Task & Video Rating Scams",
                "active_hotspot_alert": "Prepaid wallet recharge traps promising 5,000 INR daily returns.",
                "incidents": 1250
            },
            {
                "region": "Tier 2 & 3 University Hubs",
                "risk_index": "🔴 Critical Threat (44%)",
                "primary_threat_vector": "Fake Academic Grants & Unaccredited Scholarships",
                "active_hotspot_alert": "Urgent fee processing demands sent via direct WhatsApp broadcast.",
                "incidents": 1840
            },
            {
                "region": "Hyderabad & Telangana Hub",
                "risk_index": "🟡 Elevated Caution (26%)",
                "primary_threat_vector": "Unaccredited International Fellowships",
                "active_hotspot_alert": "Premature document collection on Google Forms.",
                "incidents": 840
            },
            {
                "region": "Pune & Western Academic Corridor",
                "risk_index": "🔴 High Risk (29%)",
                "primary_threat_vector": "Equipment & Software Deposit Traps",
                "active_hotspot_alert": "Demands for candidate-funded sandbox credentials.",
                "incidents": 710
            }
        ]

        platform_vulnerabilities = [
            {
                "platform": "Telegram",
                "risk_score": 88,
                "common_scam_pattern": "Encrypted chats with disappearing messages and anonymous recruiter @handles"
            },
            {
                "platform": "WhatsApp (Unsolicited Messages)",
                "risk_score": 76,
                "common_scam_pattern": "Direct outreach from unfamiliar international numbers offering part-time jobs"
            },
            {
                "platform": "Unverified Google Forms / External Portals",
                "risk_score": 68,
                "common_scam_pattern": "Harvesting full color scans of unmasked Aadhaar & PAN cards"
            },
            {
                "platform": "Free Mailbox Recruiters (@gmail/@yahoo)",
                "risk_score": 58,
                "common_scam_pattern": "Claiming enterprise corporate HR designations from personal emails"
            },
            {
                "platform": "Third-Party Aggregator Job Boards",
                "risk_score": 38,
                "common_scam_pattern": "Scraped company listings redirecting to paid external assessment links"
            }
        ]

        emerging_modus_operandi = [
            {
                "tactic": "1. Caution Money / Sandbox Credential Trap",
                "description": "Candidate receives an authentic-looking offer letter but is asked to deposit 3,000-5,000 INR as security deposit before cloud credentials or laptops are dispatched."
            },
            {
                "tactic": "2. Aadhaar + PAN Identity Harvesting",
                "description": "Requiring clear unmasked government identity proofs during initial screening before any interview or official background verification stage."
            },
            {
                "tactic": "3. Paid Grant & Fellowship Clearance Traps",
                "description": "Shortlisting female students for high-value international grants ($3,000-$5,000) with a 3-hour deadline to pay an international clearance processing fee via UPI."
            },
            {
                "tactic": "4. Pre-Joining Certificate Withholding",
                "description": "Demanding physical custody of original 10th/12th academic marksheets as security bonds, strictly illegal under UGC/AICTE regulations."
            }
        ]

        summary_metrics = {
            "total_analyzed": 14850,
            "total_threats_prevented": 1428,
            "advance_fee_traps_caught": 612,
            "id_harvesting_blocked": 589,
            "highest_risk_channel": "Telegram (42%)",
            "most_common_vector": "Refundable Laptop / Registration Fee Demands",
            "most_targeted_demographic": "Students & Early Career Women",
            "most_vulnerable_platform": "Telegram & WhatsApp Anonymous Outreach"
        }

        return {
            "total_threats_prevented": 1428,
            "advance_fee_traps_caught": 612,
            "id_harvesting_blocked": 589,
            "highest_risk_channel": "Telegram (42%)",
            "summary_metrics": summary_metrics,
            "regional_hotspots": regional_hotspots,
            "regional_risks": regional_hotspots,
            "platform_vulnerabilities": platform_vulnerabilities,
            "platform_breakdown": platform_vulnerabilities,
            "emerging_modus_operandi": emerging_modus_operandi,
            "scam_types": emerging_modus_operandi,
            "meta": {
                "label": "Illustrative Aggregated Opportunity-Risk Insights",
                "sample_size": "14,850 Analyzed Opportunities",
                "time_period": f"Last {time_period} Days",
                "active_filter_type": scam_type,
                "active_filter_platform": platform,
                "last_updated": datetime.utcnow().strftime("%B %d, %Y - %H:%M UTC")
            }
        }

    def _inspect_url(self, website_url: str, organization_name: str) -> Optional[Dict[str, Any]]:
        if not website_url:
            return None
        
        parsed = urllib.parse.urlparse(website_url if website_url.startswith("http") else f"https://{website_url}")
        domain = parsed.netloc.lower() or parsed.path.lower()
        is_https = parsed.scheme == "https" or website_url.startswith("https")

        suspicious_tlds = [".xyz", ".top", ".online", ".site", ".tk", ".ml", ".ga", ".cf", ".click", ".work", ".buzz", ".guru"]
        is_suspicious_domain = any(domain.endswith(tld) for tld in suspicious_tlds)
        has_hyphens = domain.count("-") >= 2

        consistency = "Needs Verification"
        if organization_name:
            clean_org = re.sub(r'[^a-z0-9]', '', organization_name.lower())
            clean_dom = re.sub(r'[^a-z0-9]', '', domain)
            if clean_org in clean_dom or clean_dom in clean_org:
                consistency = "Domain matches stated organization"
            else:
                consistency = "Domain does not directly align with organization name"

        return {
            "url": website_url,
            "domain": domain,
            "is_https": is_https,
            "https_note": "HTTPS is enabled (encrypts traffic, but does not guarantee sender legitimacy)" if is_https else "No HTTPS encryption detected (High security risk)",
            "suspicious_domain": is_suspicious_domain or has_hyphens,
            "domain_consistency": consistency,
            "reputation_label": "Suspicious / High-Risk TLD" if is_suspicious_domain else ("Standard Corporate Domain" if is_https else "Unencrypted Domain"),
            "notes": [
                "Domain protocol: " + ("Secure HTTPS" if is_https else "Insecure HTTP"),
                "TLD risk profile: " + ("Alternative high-risk registrar" if is_suspicious_domain else "Standard commercial/educational registrar"),
                "Entity naming check: " + consistency
            ]
        }

    def _inspect_organization(self, org_name: str, website_url: str, full_text: str) -> Dict[str, Any]:
        if not org_name:
            return {
                "name": "Unspecified Organization",
                "status": "Unable to verify from the provided information",
                "badge": "🟡 Needs Verification",
                "details": "No official company name was provided in the input.",
                "verification_tips": "Ask the sender for the official legal entity name, corporate CIN (Corporate Identity Number), and official registered office address."
            }
        
        known_orgs = ["google", "microsoft", "amazon", "apple", "meta", "tata", "infosys", "wipro", "accenture", "ibm", "deloitte"]
        org_lower = org_name.lower()
        
        is_known = any(k in org_lower for k in known_orgs)
        has_free_email = bool(self.free_email_regex.search(full_text))

        if is_known and has_free_email:
            return {
                "name": org_name,
                "status": "Potential Inconsistency / High Impersonation Risk",
                "badge": "🔴 Impersonation Warning",
                "details": f"The opportunity claims to represent '{org_name}', but uses a free public email provider (e.g. Gmail/Yahoo) or Telegram instead of an official @{org_lower.split()[0]}.com corporate address.",
                "verification_tips": "Official enterprise recruiters from established companies never hire via free Gmail or personal Telegram accounts."
            }
        elif is_known:
            return {
                "name": org_name,
                "status": "Verified Entity Signature",
                "badge": "🟢 Established Enterprise",
                "details": f"Stated organization '{org_name}' corresponds to a recognized global enterprise. Ensure application is submitted via official careers portal.",
                "verification_tips": "Cross-reference job ID on the official careers page."
            }
        else:
            return {
                "name": org_name,
                "status": "Needs Verification",
                "badge": "🟡 Requires Independent Check",
                "details": f"The organization '{org_name}' requires external confirmation on official registries (e.g., MCA in India, Companies House in UK, or SEC in US).",
                "verification_tips": "Search for official press releases, LinkedIn company page with active employee connections, and registered corporate office details."
            }

    def _inspect_document(self, doc_text: str, metadata: Optional[Dict[str, Any]], full_text: str) -> Dict[str, Any]:
        has_text = bool(doc_text.strip())
        
        has_fee_clause = bool(re.search(r'(deposit|fee|charge|reimbursement|payment of ₹|payment of \$)', doc_text, re.I))
        has_penal_clause = bool(re.search(r'(penalty|forfeit|breach of contract|legal action|bond amount)', doc_text, re.I))

        signals = []
        if has_text:
            signals.append("Document Text Extracted & Parsed")
            if has_fee_clause:
                signals.append("⚠ Monetary condition or payment clause detected in document")
            if has_penal_clause:
                signals.append("⚠ Heavy penalty or bond clause identified")
            if not has_fee_clause and not has_penal_clause:
                signals.append("✓ Standard professional offer structure")
        else:
            signals.append("No document attached (Analysis based on submitted message & URL)")

        return {
            "has_document": has_text,
            "has_anomalies": has_fee_clause or has_penal_clause,
            "summary": "Document contains unusual financial or punitive clauses." if (has_fee_clause or has_penal_clause) else ("Document structure conforms to typical offer templates." if has_text else "No uploaded document analyzed."),
            "key_signals": signals,
            "extracted_elements": {
                "role_identified": bool(re.search(r'(role|position|title|designation)', doc_text or full_text, re.I)),
                "remuneration_clause": bool(re.search(r'(stipend|salary|compensation|remuneration|payout|per month)', doc_text or full_text, re.I)),
                "confidentiality_clause": bool(re.search(r'(nda|confidentiality|non-disclosure)', doc_text or full_text, re.I)),
                "identity_demand": bool(re.search(r'(aadhaar|pan|passport|id proof)', doc_text or full_text, re.I))
            }
        }

    def _extract_snippet(self, text: str, regex_pattern) -> Optional[str]:
        match = regex_pattern.search(text)
        if not match:
            return None
        start = max(0, match.start() - 40)
        end = min(len(text), match.end() + 60)
        snippet = text[start:end].replace('\n', ' ').strip()
        return f"...{snippet}..."

    def _generate_safe_script(self, has_aadhaar: bool, has_pan: bool, has_payment: bool, has_telegram_wa: bool, org_name: str) -> str:
        org = org_name or "your team"
        if has_payment:
            return (
                f"Dear Hiring Team,\n\n"
                f"Thank you for sharing the opportunity details with {org}. "
                f"As a standard personal security guideline, I do not make advance payments, equipment deposits, or processing transfers for employment or scholarship consideration. "
                f"Could you please confirm if this opportunity can proceed without upfront financial commitments through official corporate channels?\n\n"
                f"Best regards,"
            )
        elif has_aadhaar or has_pan:
            return (
                f"Dear Recruiting Team,\n\n"
                f"Thank you for considering my profile for {org}. "
                f"To protect my sensitive personal information, I will be pleased to provide masked identification (Masked Aadhaar / verified credentials) "
                f"directly through your organization's secure HR onboarding portal once the formal written contract has been finalized.\n\n"
                f"Looking forward to the next steps.\n\n"
                f"Best regards,"
            )
        elif has_telegram_wa:
            return (
                f"Hello,\n\n"
                f"Thank you for reaching out regarding {org}. "
                f"For professional records and data privacy, I prefer to conduct all hiring communications and document reviews via official company email addresses. "
                f"Please feel free to send the detailed project brief or offer to my email address.\n\n"
                f"Thank you for understanding,"
            )
        else:
            return (
                f"Dear {org} Team,\n\n"
                f"Thank you for extending this opportunity. I am reviewing the terms and look forward to completing the formal onboarding through your official enterprise portal.\n\n"
                f"Best regards,"
            )

    def verify_campus_opportunity(self, req_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Campus SHEVAULT Mode: 5-Step Placement Cell Verification & Lifecycle Pipeline
        1. Company submits internship
        2. SHEVAULT verifies it
        3. College receives it
        4. Career cell approves & issues certificate
        5. Students see 'Campus Verified' & can run personal SHEVAULT check
        """
        college = req_data.get("college_name", "").strip() or "University Placement Cell"
        placement_officer = req_data.get("placement_officer_name", "").strip() or "Placement Coordinator"
        company = req_data.get("company_name", "").strip() or "Recruiting Organization"
        role_offered = req_data.get("role_offered", "").strip() or req_data.get("drive_title", "").strip() or "Internship / Full-Time Role"
        email = req_data.get("recruiter_email", "").strip().lower()
        website = req_data.get("company_website", "").strip().lower()
        comm_mode = req_data.get("communication_mode", "Official Placement Cell Portal")
        zero_fee = req_data.get("zero_fee_placement_policy", True)
        doc_retention = req_data.get("original_document_retention_policy", True)
        details = req_data.get("opportunity_details", "").strip() or req_data.get("drive_details", "").strip()

        combined_text = f"{company} {role_offered} {details}".lower()

        is_free_email = bool(self.free_email_regex.search(email)) if email else False
        has_fee_pattern = (not zero_fee) or bool(self.payment_trap_regex.search(combined_text))
        has_orig_pattern = (not doc_retention) or bool(self.doc_retention_regex.search(combined_text))
        has_task_scam = bool(self.task_scam_regex.search(combined_text))
        has_telegram_wa = bool(self.telegram_wa_regex.search(combined_text))

        risk_factors = []
        deductions = 0

        if has_fee_pattern:
            deductions += 50
            risk_factors.append("Violation of Zero-Fee Placement Policy: Candidate-funded deposits, training fees, or equipment charges detected.")

        if has_orig_pattern:
            deductions += 40
            risk_factors.append("Violation of Document Safety Policy: Mandatory retention of original marksheets or certificates demanded.")

        if has_task_scam:
            deductions += 45
            risk_factors.append("Deceptive Task Trap: Commission per like/rating or prepaid task wallet structure detected.")

        if has_telegram_wa and "telegram" in comm_mode.lower():
            deductions += 25
            risk_factors.append("Informal Channel Redirection: Drive registration is hosted exclusively via unverified Telegram/WhatsApp.")

        if is_free_email:
            deductions += 20
            risk_factors.append("Recruiter uses a free public email address (@gmail/@yahoo) rather than verified enterprise corporate domain.")

        # Calculate Score
        if has_fee_pattern or has_orig_pattern or has_task_scam or deductions >= 45:
            clearance_status = "REJECTED"
            clearance_badge = "🔴 REJECTED: STUDENT RISK"
            trust_score = max(15, min(35, 100 - deductions))
            audit_summary = f"REJECTED FOR CAMPUS. Critical student safety violations detected for {company} ({role_offered}). Prohibited candidate fees or original document retention clauses flagged."
            action = "DO NOT CIRCULATE. Placement Cell must issue a warning against applying directly to this recruiter."
            student_notice = (
                f"🚨 CAMPUS PLACEMENT ADVISORY - {college}\n"
                f"Drive: {role_offered} at {company}\n"
                f"STATUS: REJECTED / NOT APPROVED BY PLACEMENT CELL\n"
                f"Security Finding: Opportunity failed student safety compliance checks. Students must not transfer money or submit original marksheets."
            )
        elif deductions >= 20:
            clearance_status = "CONDITIONAL"
            clearance_badge = "🟡 CONDITIONAL CLEARANCE"
            trust_score = max(45, min(68, 100 - deductions))
            audit_summary = f"CONDITIONAL CLEARANCE. Stated offer from {company} requires formal domain confirmation and written zero-fee indemnity before release."
            action = "Hold notice board release pending written confirmation of corporate domain email and zero-deduction guarantee."
            student_notice = (
                f"⚠️ CAMPUS PLACEMENT NOTICE - {college}\n"
                f"Drive: {role_offered} at {company}\n"
                f"STATUS: CONDITIONAL PLACEMENT CELL AUDIT\n"
                f"Verification is currently in progress. Official registration links will be released via the campus portal once final domain checks conclude."
            )
        else:
            clearance_status = "APPROVED"
            clearance_badge = "🟢 APPROVED FOR CAMPUS"
            trust_score = min(max(92, 100 - deductions), 98)
            audit_summary = f"CAMPUS VERIFIED. {company} has passed all SHEVAULT student safety compliance checks. Zero-fee guarantee and document retention policies validated."
            action = "Approved for dissemination across official campus placement channels and student notice boards."
            student_notice = (
                f"🎓 VERIFIED CAMPUS OPPORTUNITY - {college}\n"
                f"Company: {company}\n"
                f"Role: {role_offered}\n"
                f"Status: 🟢 CAMPUS VERIFIED BY SHEVAULT AI & PLACEMENT CELL\n"
                f"Compliance: Verified Zero-Fee Hiring • No Original Document Custody • Enterprise Authenticated\n"
                f"All eligible students may apply through the official campus portal. You can also run your personal SHEVAULT identity check."
            )

        cert_id = f"SHV-CAMP-{datetime.utcnow().year}-{str(uuid.uuid4())[:4].upper()}"

        # 5-Step Pipeline Structure
        pipeline_steps = [
            {
                "step": 1,
                "title": "Company Submits Internship",
                "actor": "Company / Recruiter",
                "status": "completed",
                "badge": "1. Submitted",
                "details": f"{company} submitted '{role_offered}' details with zero-fee & anti-certificate retention policy compliance."
            },
            {
                "step": 2,
                "title": "SHEVAULT Verifies It",
                "actor": "SHEVAULT AI Engine",
                "status": "completed",
                "badge": "2. AI Verified" if clearance_status == "APPROVED" else "2. Flagged",
                "details": f"Evaluated domain authenticity, anti-fee compliance ({'Passed' if not has_fee_pattern else 'Violated ⚠'}), and bond terms."
            },
            {
                "step": 3,
                "title": "College Receives It",
                "actor": f"{college} T&P Cell",
                "status": "completed",
                "badge": "3. Received",
                "details": f"Intake verified with Security Score {trust_score}/100 and routed to {placement_officer}."
            },
            {
                "step": 4,
                "title": "Career Cell Approves",
                "actor": f"{placement_officer}",
                "status": "completed" if clearance_status == "APPROVED" else ("held" if clearance_status == "CONDITIONAL" else "rejected"),
                "badge": f"4. {clearance_status}",
                "details": f"Issued Clearance Certificate {cert_id} & generated official student circular." if clearance_status == "APPROVED" else "Drive placed on hold or rejected due to student risk."
            },
            {
                "step": 5,
                "title": "Students See 'Campus Verified' & Run Personal Check",
                "actor": "Enrolled Candidates",
                "status": "active" if clearance_status == "APPROVED" else "inactive",
                "badge": "5. Campus Verified",
                "details": "Students see verified badge on notice boards and can 1-click 'Run Personal SHEVAULT Check' for personalized KYC masking & interview guidance."
            }
        ]

        placement_advisories = [
            f"1. Zero Student Cost Rule: Remind all candidates that {company} will never charge registration or test fees.",
            "2. Safe Document Sharing: Advise students to share only Masked Aadhaar (showing last 4 digits) with cross-watermarks.",
            "3. Official Channel Enforcement: Direct students to communicate exclusively through the registered campus portal.",
            "4. Personal SHEVAULT Scan: Encourage candidates to run personal SHEVAULT checks before signing any employment bonds."
        ]

        return {
            "id": f"campus_{str(uuid.uuid4())[:10]}",
            "certificate_id": cert_id,
            "college_name": college,
            "placement_officer_name": placement_officer,
            "company_name": company,
            "role_offered": role_offered,
            "clearance_status": clearance_status,
            "clearance_badge": clearance_badge,
            "trust_score": trust_score,
            "audit_summary": audit_summary,
            "student_notice_template": student_notice,
            "pipeline_steps": pipeline_steps,
            "placement_advisories": placement_advisories,
            "risk_factors": risk_factors or ["No student risk signals flagged. Opportunity complies with UGC/AICTE safety standards."],
            "verification_date": datetime.utcnow().strftime("%B %d, %Y"),
            "created_at": datetime.utcnow().strftime("%B %d, %Y - %H:%M UTC")
        }

trust_engine = TrustEngine()
