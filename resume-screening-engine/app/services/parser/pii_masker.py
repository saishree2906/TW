# import re

# EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
# PHONE_REGEX = r"\+?\d[\d\s\-]{8,}\d"


# def mask_pii(text: str) -> str:
#     """
#     Masks emails and phone numbers to enforce fairness and compliance.
#     """
#     text = re.sub(EMAIL_REGEX, "[EMAIL_REDACTED]", text)
#     text = re.sub(PHONE_REGEX, "[PHONE_REDACTED]", text)
#     return text


import re

# Improved Regex for better international phone support
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"


def mask_pii(text: str, name: str = None) -> str:
    """Masks emails, phone numbers, and names to enforce fairness."""
    if not text:
        return ""

    # 1. Mask Emails
    text = re.sub(EMAIL_REGEX, "[EMAIL_REDACTED]", text)

    # 2. Mask Phones
    text = re.sub(PHONE_REGEX, "[PHONE_REDACTED]", text)

    # 3. Mask Name (Critical for Fairness)
    if name and isinstance(name, str):
        # We mask individual parts of the name (First/Last) to be thorough
        for part in name.split():
            if len(part) > 2:  # Ignore initials
                text = re.sub(
                    re.escape(part),
                    "[NAME_REDACTED]",
                    text,
                    flags=re.IGNORECASE,
                )

    return text
