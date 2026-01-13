import csv
import os
import json
from .models import AuditResult

class InternalStorage:
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.leads_file = os.path.join(storage_dir, "audit_leads.csv")
        self.ensure_storage()

    def ensure_storage(self):
        os.makedirs(self.storage_dir, exist_ok=True)
        if not os.path.exists(self.leads_file):
            with open(self.leads_file, 'w', newline='') as f:
                writer = csv.writer(f)
                # Header
                writer.writerow([
                    "Timestamp", "ID", "Business Name", "URL", "Email", 
                    "Overall Score", "Grade", 
                    "L1 Score", "L2 Score", "L3 Score", "L4 Score", "L5 Score",
                    "Detailed Data Path"
                ])

    def save_result(self, result: AuditResult, detailed_json_path: str = ""):
        sub = result.submission
        score = result.overall_score
        
        # Extract layer scores safely (assume ordered 1-5, but be safe)
        l_scores = {l.layer_id: l.points_earned for l in score.layer_scores}
        
        with open(self.leads_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                sub.timestamp.isoformat(),
                sub.id,
                sub.business_name,
                sub.website_url,
                sub.contact_email,
                score.total_points,
                score.grade,
                l_scores.get(1, 0),
                l_scores.get(2, 0),
                l_scores.get(3, 0),
                l_scores.get(4, 0),
                l_scores.get(5, 0),
                detailed_json_path
            ])
        
        print(f"Lead saved to internal storage: {self.leads_file}")
