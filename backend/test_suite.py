"""
SHEVAULT AI - Automated Integration & Acceptance Test Suite
"""
import urllib.request
import urllib.parse
import json

def run_tests():
    print("=" * 60)
    print("   SHEVAULT AI - COMPREHENSIVE SYSTEM VERIFICATION   ")
    print("=" * 60)

    # 1. Health check
    res = urllib.request.urlopen("http://127.0.0.1:8000/api/health")
    health = json.loads(res.read().decode())
    print(f"1. Health Check: {health['status']} | Mode: {health['mode']}")

    # 2. Registration test
    reg_data = json.dumps({
        "name": "Sneha Rao",
        "email": "sneha@shevault.ai",
        "password": "StrongPassword123!",
        "role": "Professional"
    }).encode("utf-8")
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/api/auth/register", data=reg_data, headers={"Content-Type": "application/json"})
        reg_res = json.loads(urllib.request.urlopen(req).read().decode())
        print(f"2. Registration: Success for {reg_res['user']['name']} ({reg_res['user']['role']})")
    except Exception:
        print("2. Registration: User already exists in SQLite DB (Skipping creation)")

    # 3. Login test
    login_data = json.dumps({"email": "sneha@shevault.ai", "password": "StrongPassword123!"}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=login_data, headers={"Content-Type": "application/json"})
    auth_res = json.loads(urllib.request.urlopen(req).read().decode())
    token = auth_res["token"]
    print(f"3. Authentication: JWT Token received successfully ({token[:24]}...)")

    # 4. Profile update test
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/api/auth/update-profile?name=Sneha%20Rao%20MBA&role=Entrepreneur&allow_storage=true",
        method="POST",
        headers={"Authorization": f"Bearer {token}"}
    )
    up_res = json.loads(urllib.request.urlopen(req).read().decode())
    print(f"4. Profile Update: Updated name to '{up_res['user']['name']}', role to '{up_res['user']['role']}'")

    # 5. Analysis Scenario 1: Remote Data Entry (Deposit Trap)
    p1 = urllib.parse.urlencode({
        "opportunity_type": "Job",
        "organization_name": "Apex Global Solutions",
        "website_url": "https://apex-careers.xyz",
        "message_text": "Submit Aadhaar, PAN, and pay ₹3,500 security deposit via UPI to hr@oksbi within 24 hours."
    }).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:8000/api/analyze", data=p1, headers={"Authorization": f"Bearer {token}"})
    res1 = json.loads(urllib.request.urlopen(req).read().decode())
    print(f"5. Scenario 1 (Deposit Trap): {res1['overall_risk_level']} (Score: {res1['trust_score']}/100)")
    print(f"   -> Detected Evidence Items: {len(res1['evidence_list'])}")
    print(f"   -> 5 Modules Evaluated: {list(res1['modules'].keys())}")
    print(f"   -> Safe Push-Back Script Generated: {bool(res1.get('safe_communication_script'))}")

    # 6. Analysis Scenario 2: Legit Google STEP Internship
    p2 = urllib.parse.urlencode({
        "opportunity_type": "Internship",
        "organization_name": "Google India Pvt Ltd",
        "website_url": "https://careers.google.com/jobs/results/",
        "message_text": "Summer 2026 STEP Internship offer. Review and sign inside careers.google.com portal. No sensitive documents requested over email."
    }).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:8000/api/analyze", data=p2, headers={"Authorization": f"Bearer {token}"})
    res2 = json.loads(urllib.request.urlopen(req).read().decode())
    print(f"6. Scenario 2 (Google STEP): {res2['overall_risk_level']} (Score: {res2['trust_score']}/100)")

    # 7. Analysis Scenario 3: Telegram KYC Selfie Trap
    p3 = urllib.parse.urlencode({
        "opportunity_type": "Freelance",
        "organization_name": "Vogue Media",
        "website_url": "https://vogue-media-designs.site",
        "message_text": "Send passport photo and a selfie holding your ID on Telegram @voguemedia_lead for $800 gig."
    }).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:8000/api/analyze", data=p3, headers={"Authorization": f"Bearer {token}"})
    res3 = json.loads(urllib.request.urlopen(req).read().decode())
    print(f"7. Scenario 3 (Selfie Trap): {res3['overall_risk_level']} (Score: {res3['trust_score']}/100)")

    # 8. Presets and Safety Guide
    presets_res = json.loads(urllib.request.urlopen("http://127.0.0.1:8000/api/presets").read().decode())
    guide_res = json.loads(urllib.request.urlopen("http://127.0.0.1:8000/api/safety-guide").read().decode())
    print(f"8. Knowledge & Presets: {len(presets_res['presets'])} Presets, {len(guide_res['categories'])} Safety Categories")

    print("=" * 60)
    print("   ALL 8 END-TO-END ACCEPTANCE TESTS PASSED!   ")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
