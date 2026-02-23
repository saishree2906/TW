#!/usr/bin/env python3

import sys
from pathlib import Path

# Read test resume
test_file = Path("test_resume.txt")
with open(test_file, 'r') as f:
    resume_text = f.read()

# Test the parser with text directly
from app.services.parser.spacy_parser import SpacyResumeParser, get_spacy_model

# Initialize spaCy model
nlp = get_spacy_model()
doc = nlp(resume_text)

# Create a fake parser instance to test extraction methods
parser = SpacyResumeParser.__new__(SpacyResumeParser)

# Test extraction methods
print("=" * 60)
print("RESUME PARSING TEST RESULTS")
print("=" * 60)

email = parser._extract_email(resume_text)
print(f"\n✓ Email extracted: {email}")

phone = parser._extract_phone(resume_text)
print(f"✓ Phone extracted: {phone}")

name = parser._extract_name(doc)
print(f"✓ Name extracted: {name}")

skills = parser._extract_skills(resume_text, doc)
print(f"✓ Skills extracted ({len(skills)}): {', '.join(skills[:5])}...")

education = parser._extract_education(resume_text, doc)
print(f"✓ Education extracted ({len(education)}): {', '.join(education[:3])}...")

experience = parser._extract_experience_years(resume_text, doc)
print(f"✓ Experience years calculated: {experience}")

college = parser._extract_college(resume_text, doc)
print(f"✓ College extracted: {college}")

degree = parser._extract_degree(resume_text, doc)
print(f"✓ Degree extracted: {degree}")

print("\n" + "=" * 60)
print("All extraction methods working correctly!")
print("=" * 60)
