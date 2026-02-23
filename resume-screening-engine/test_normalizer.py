#!/usr/bin/env python3
"""Test normalizer output"""
from app.services.parser.normalizer import normalize

# Simulate raw parser output
raw_data = {
    "skills": ["python", "java", "fastapi", "docker", "aws"],
    "experience_years": 8.0,
    "education": ["bachelor", "science", "master"],
    "total_experience": 8,
    "name": "John Smith",
    "email": "john.smith@example.com",
    "mobile_number": "(555) 123-4567",
    "college_name": "University of California",
    "degree": "Bachelor of Science in Computer Science",
    "no_of_pages": 1,
}

result = normalize(raw_data)

import json
print("\n" + "=" * 60)
print("NORMALIZATION TEST (PRD-Compliant Response)")
print("=" * 60)
print(json.dumps(result, indent=2))
print("\n" + "=" * 60)

# Verify structure
assert result["status"] == "success", "Status should be 'success'"
assert "data" in result, "Should have 'data' key"
assert "skills" in result["data"], "Data should have 'skills'"
assert "experience_years" in result["data"], "Data should have 'experience_years'"
assert "education" in result["data"], "Data should have 'education'"
assert "contact" in result["data"], "Data should have 'contact'"
assert result["data"]["contact"]["masked"] == True, "Contact should be masked"
assert "name" not in result["data"]["contact"], "Name should not be exposed"
assert "email" not in result["data"]["contact"], "Email should not be exposed"
assert "phone" not in result["data"]["contact"], "Phone should not be exposed"

print("✓ Response structure is PRD-compliant")
print("✓ PII is properly masked (name, email, phone not in response)")
print("✓ All required fields present")
print("=" * 60)
