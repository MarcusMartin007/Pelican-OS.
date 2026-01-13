from execution.audit_engine.collectors import Layer1Collector
from execution.audit_engine.models import AuditSubmission

def main():
    # Test with Google as a dummy target (unlikely to have "About" link on search home maybe, but good for stability)
    # Or better, use python.org which definitely has About.
    submission = AuditSubmission(
        business_name="Python",
        website_url="https://www.python.org",
        contact_email="test@example.com"
    )
    
    print(f"Testing Layer 1 Collector for {submission.website_url}...")
    collector = Layer1Collector(submission)
    tasks = collector.collect()
    
    for task in tasks:
        print(f"[{task.status.value}] {task.name}: {task.reasoning}")
        if task.status.value == "PASS":
             print(f"   (+{task.score_impact} pts)")

if __name__ == "__main__":
    main()
