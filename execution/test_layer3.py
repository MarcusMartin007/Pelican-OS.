from execution.audit_engine.collectors import Layer3Collector
from execution.audit_engine.models import AuditSubmission

def main():
    submission = AuditSubmission(
        business_name="Python",
        website_url="https://www.python.org",
        contact_email="test@example.com"
    )
    
    print(f"Testing Layer 3 Collector for {submission.website_url}...")
    collector = Layer3Collector(submission)
    tasks = collector.collect()
    
    for task in tasks:
        print(f"[{task.status.value}] {task.name}: {task.reasoning}")
        if task.status.value == "PASS":
             print(f"   (+{task.score_impact} pts)")
        if task.evidence:
             print(f"   Evidence: {str(task.evidence)[:100]}...")

if __name__ == "__main__":
    main()
