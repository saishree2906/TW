<!-- 1. pdfminer.six strengths & limitations

2. Handling multi-column resumes

3. Common extraction issues (headers, footers)

4. Why PDF-only scope is acceptable now -->

# Resume Extraction Research Notes

### 1. pdfminer.six strengths & limitations
- **Strengths**: Granular layout control and coordinate mapping.
- **Limitations**: Slow processing for large batches and complex table parsing.

### 2. Handling multi-column resumes
- **Strategy**: Used `pdfplumber` because it treats text as visual blocks rather than a single stream, preserving the separation between left and right columns.

### 3. Common extraction issues (headers, footers)
- **Finding**: Page numbers and contact info often repeat. Current logic uses a vertical coordinate threshold to skip the top and bottom 10% of page text.

### 4. Why PDF-only scope is acceptable now
- **Reasoning**: 95% of professional resumes are submitted in PDF/DOCX to preserve formatting. Plain text support is deprioritized to ensure high-accuracy extraction of structured headers.