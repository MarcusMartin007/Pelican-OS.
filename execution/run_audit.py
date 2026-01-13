import argparse
import sys
import os
from datetime import datetime
from execution.audit_engine.models import AuditSubmission, AuditResult
from execution.audit_engine.collectors import (
    Layer1Collector, Layer2Collector, Layer3Collector, Layer4Collector, Layer5Collector
)
from execution.audit_engine.scorer import Scorer
from execution.audit_engine.reporter import PDFReporter
from execution.audit_engine.utils import normalize_url

def execute_audit(business_name: str, url: str, email: str, output_base_dir: str = None) -> str:
    """
    Executes the full audit workflow.
    Returns the paths to the generated reports.
    """
    # 1. Intake & Normalize
    normalized_url = normalize_url(url)
    submission = AuditSubmission(
        business_name=business_name,
        website_url=normalized_url,
        contact_email=email
    )
    
    print(f"Starting Audit for: {submission.business_name} ({submission.website_url})")
    
    # 2. Collect Evidence
    collectors = [
        Layer1Collector(submission),
        Layer2Collector(submission),
        Layer3Collector(submission),
        Layer4Collector(submission),
        Layer5Collector(submission)
    ]
    
    all_tasks = []
    
    for i, collector in enumerate(collectors, 1):
        print(f"Running Layer {i} collection...")
        try:
            tasks = collector.collect()
            all_tasks.extend(tasks)
        except Exception as e:
            print(f"Error in Layer {i}: {e}")
            
    # 3. Score
    print("Calculating scores...")
    scorer = Scorer()
    layer_scores = []
    for i in range(1, 6):
        layer_scores.append(scorer.calculate_layer_score(i, all_tasks))
        
    overall_score = scorer.calculate_overall_score(layer_scores)
    
    # Generate Narrative
    from execution.audit_engine.narrative import NarrativeEngine
    narrative_engine = NarrativeEngine()
    overall_score.ai_narrative = narrative_engine.generate_narrative(submission, overall_score)
    
    result = AuditResult(
        submission=submission,
        overall_score=overall_score
    )
    
    print(f"\nOverall Score: {overall_score.total_points}/100 Grade: {overall_score.grade}")
    for l in layer_scores:
        print(f"Layer {l.layer_id} ({l.name}): {l.points_earned}/{l.max_points}")

    # 4. Report
    print("\nGenerating Reports...")
    
    if output_base_dir:
        out_dir = output_base_dir
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join([c for c in submission.business_name if c.isalnum() or c in (' ','-')]).strip().replace(' ', '_')
        out_dir = f"reports/{safe_name}_{timestamp}"
    
    # PDF (Summary Only)
    pdf_reporter = PDFReporter(template_path="templates/summary_report_template.html")
    pdf_file = os.path.join(out_dir, "audit_summary.pdf")
    pdf_reporter.generate_pdf(result, pdf_file)
    
    # Markdown (Detailed)
    from execution.audit_engine.params_reporter import MarkdownReporter
    md_reporter = MarkdownReporter()
    md_file = os.path.join(out_dir, "audit_detail.md")
    md_reporter.generate_markdown(result, md_file)
    
    # 5. Internal Storage
    from execution.audit_engine.storage import InternalStorage
    storage = InternalStorage()
    storage.save_result(result, detailed_json_path=os.path.abspath(md_file))
    
    return os.path.abspath(pdf_file)

def main():
    parser = argparse.ArgumentParser(description="PPM AI Visibility Audit Automation")
    parser.add_argument("--business", required=True, help="Business Name")
    parser.add_argument("--url", required=True, help="Website URL")
    parser.add_argument("--email", required=True, help="Contact Email")
    parser.add_argument("--output", default=None, help="Output directory for report")
    
    args = parser.parse_args()
    
    try:
        report_path = execute_audit(args.business, args.url, args.email, args.output)
        print(f"Summary PDF ready at: {report_path}")
        print(f"Email would be sent to: {args.email}")
    except Exception as e:
        print(f"Audit failed: {e}")

if __name__ == "__main__":
    main()
