from execution.audit_engine.reporter import PDFReporter
from execution.audit_engine.models import AuditResult, AuditSubmission, OverallScore, LayerScore, AuditTask, TaskStatus
from datetime import datetime

def main():
    # Create dummy data
    submission = AuditSubmission(
        business_name="Test Business",
        website_url="https://example.com",
        contact_email="test@example.com"
    )
    
    # Dummy Layer 1
    l1 = LayerScore(layer_id=1, name="Entity Clarity", points_earned=15, max_points=20)
    l1.tasks.append(AuditTask(task_id="L1_NAME", layer=1, name="Name Match", description="Checks name", status=TaskStatus.PASS, reasoning="Matched Name"))
    
    overall = OverallScore(
        total_points=85,
        max_total_points=100,
        grade="B",
        layer_scores=[l1]
    )
    
    result = AuditResult(submission=submission, overall_score=overall)
    
    reporter = PDFReporter()
    output_path = ".tmp/test_report.pdf"
    
    print(f"Generating PDF to {output_path}...")
    reporter.generate_pdf(result, output_path)

if __name__ == "__main__":
    main()
