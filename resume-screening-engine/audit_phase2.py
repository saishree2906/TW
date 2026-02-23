import sys
import re
from typing import Dict, Any

# --- STEP 1: TEST THE PRIVACY LAYER (PII MASKER) ---
try:
    from app.services.parser.pii_masker import mask_pii
    print("✅ PII Masker Found")
except ImportError:
    print("❌ CRITICAL: pii_masker.py missing or broken")
    sys.exit(1)

def test_privacy():
    print("\n--- 1. AUDITING PRIVACY (FAIRNESS) ---")
    sample_text = "Contact John Smith at john@email.com or 555-0199"
    # Testing if it handles the NAME (The common logic bug)
    result = mask_pii(sample_text, name="John Smith")

    if "[NAME_REDACTED]" in result:
        print("✅ SUCCESS: Candidate Name is hidden.")
    else:
        print("❌ FAIL: Candidate Name is still visible! (Logic Bug)")

# --- STEP 2: TEST THE DATA CLEANER (NORMALIZER) ---
try:
    from app.services.parser.normalizer import normalize
    print("✅ Normalizer Found")
except ImportError:
    print("❌ CRITICAL: normalizer.py missing or broken")
    sys.exit(1)

def test_data_integrity():
    print("\n--- 2. AUDITING DATA INTEGRITY (CORRECTNESS) ---")
    # Simulate the "8+ years" crash case
    buggy_data = {
        "name": "Jane Doe",
        "experience_years": "8+ years",
        "skills": ["Python", "Python"], # Testing duplicate removal
        "raw_text": "Jane Doe has 8+ years in Python."
    }

    try:
        result = normalize(buggy_data)
        exp = result["data"]["experience_years"]
        skills = result["data"]["skills"]

        if isinstance(exp, float):
            print(f"✅ SUCCESS: '8+ years' converted to float {exp}")
        else:
            print(f"❌ FAIL: Experience is still a string: {type(exp)}")

        if len(skills) == 1:
            print("✅ SUCCESS: Duplicate skills removed.")
        else:
            print(f"❌ FAIL: Found {len(skills)} skills (Duplicates remain).")

    except Exception as e:
        print(f"❌ CRITICAL CRASH: Normalizer cannot handle strings! Error: {e}")

# --- EXECUTE THE AUDIT ---
if __name__ == "__main__":
    print("🚀 STARTING PHASE 2 AUTOMATED AUDIT")
    test_privacy()
    test_data_integrity()
    print("\nAudit Complete. If you see '❌', apply the fixes we discussed.")