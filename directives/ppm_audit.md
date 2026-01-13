# Directive: PPM Visibility Audit

## Goal
Perform a comprehensive 5-layer visibility audit for a business website and generate a branded PDF report.

## Inputs
- `business`: Business Name
- `url`: Website URL
- `email`: Contact Email

## Outputs
- PDF Report in `reports/` folder.
- Console output with score summary.

## Tooling
- **Script**: `execution/run_audit.py`
- **Engine**: `execution/audit_engine/`

## Instructions
1.  Run the audit script:
    ```bash
    python3 execution/run_audit.py --business "Business Name" --url "example.com" --email "user@example.com"
    ```
2.  Retrieve the PDF from the location specified in the output.
3.  Send the PDF to the user (currently handled by script mock delivery).

## Edge Cases
- Site unreachable: Collectors handle timeouts and return FAIL status.
- Missing dependencies: Ensure `pip install -r requirements.txt` and `playwright install` are run.
- Invalid URL: Normalized by utility function.
