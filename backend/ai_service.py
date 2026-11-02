"""
SHEVAULT AI - AI Service Integration Layer
Provides abstraction for live LLM inference (Google Gemini) with graceful fallback to the 5-Module Trust Engine.
"""
import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from .trust_engine import trust_engine, PRESETS

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    def is_ai_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def analyze_opportunity(self, 
                            opportunity_type: str, 
                            organization_name: str, 
                            website_url: str, 
                            message_text: str,
                            extracted_doc_text: str = "",
                            extracted_doc_metadata: Optional[Dict[str, Any]] = None,
                            preset_id: Optional[str] = None) -> Dict[str, Any]:
        
        # If preset is selected and fields are empty, populate from preset
        if preset_id and preset_id in PRESETS:
            preset = PRESETS[preset_id]
            if not opportunity_type:
                opportunity_type = preset["opportunity_type"]
            if not organization_name:
                organization_name = preset["organization_name"]
            if not website_url:
                website_url = preset["website_url"]
            if not message_text:
                message_text = preset["message_text"]

        # 1. First run the deterministic 5-module Trust Engine for high-precision regex/signal detection
        base_result = trust_engine.analyze(
            opportunity_type=opportunity_type,
            organization_name=organization_name,
            website_url=website_url,
            message_text=message_text,
            extracted_doc_text=extracted_doc_text,
            extracted_doc_metadata=extracted_doc_metadata,
            is_live_ai=False
        )

        # 2. If Gemini API key is configured, optionally enrich with live LLM synthesis
        if self.is_ai_configured():
            try:
                enriched = self._call_gemini_api(
                    opportunity_type, organization_name, website_url, message_text, extracted_doc_text, base_result
                )
                if enriched:
                    return enriched
            except Exception as e:
                print(f"[SHEVAULT AI] Gemini API call skipped/failed: {e}. Falling back to Smart Trust Engine.")
        
        # Return TrustEngine result with transparent mode badge
        return base_result

    def _call_gemini_api(self, opp_type: str, org_name: str, url: str, message: str, doc_text: str, base_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        prompt = f"""
You are SHEVAULT AI, an AI trust and identity protection analyst for women evaluating digital opportunities (jobs, internships, scholarships, freelance gigs).
Analyze the following opportunity:
- Type: {opp_type}
- Organization: {org_name}
- URL: {url}
- Message/Offer Text: {message}
- Document Extracted: {doc_text}

Our rule-based signals detected:
- Overall risk: {base_result['overall_risk_level']}
- Trust score: {base_result['trust_score']}

Respond ONLY with a valid JSON object matching this schema:
{{
  "ai_summary": "2-3 empowering, clear sentences explaining the opportunity and key risks or safety signals.",
  "additional_red_flags": ["list of any subtle psychological or impersonation flags"],
  "safe_sharing_recommendation": "specific advice on what to share vs withhold"
}}
"""
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(text)
            
            # Enrich base result
            base_result["is_live_ai"] = True
            base_result["analysis_mode_label"] = "Live Gemini AI Analysis"
            if "ai_summary" in parsed:
                base_result["score_explanation"] = parsed["ai_summary"]
            
            return base_result

ai_service = AIService()
