from typing import List
from .models import AuditTask, LayerScore, OverallScore, TaskStatus

class Scorer:
    def __init__(self):
        pass

    def calculate_layer_score(self, layer_id: int, tasks: List[AuditTask]) -> LayerScore:
        points = 0
        max_points = 0
        
        for task in tasks:
            if task.layer == layer_id:
                max_points += task.max_points
                points += task.score_impact
        
        percentage = (points / max_points * 100) if max_points > 0 else 0
        
        # Determine Grade
        if percentage >= 90: grade = "A"
        elif percentage >= 80: grade = "B"
        elif percentage >= 70: grade = "C"
        elif percentage >= 60: grade = "D"
        else: grade = "F"
        
        layer_names = {
            1: "Entity Clarity",
            2: "Structural Accessibility",
            3: "Semantic Alignment",
            4: "Authority & Reinforcement",
            5: "Automation Readiness"
        }
        
        layer_tasks = [t for t in tasks if t.layer == layer_id]
        
        return LayerScore(
            layer_id=layer_id,
            name=layer_names.get(layer_id, f"Layer {layer_id}"),
            points_earned=points,
            max_points=max_points,
            percentage=round(percentage, 2),
            grade=grade,
            tasks=layer_tasks
        )

    def calculate_overall_score(self, layer_scores: List[LayerScore]) -> OverallScore:
        total_points = sum(l.points_earned for l in layer_scores)
        max_total = sum(l.max_points for l in layer_scores)
        
        percentage = (total_points / max_total * 100) if max_total > 0 else 0
        
        if percentage >= 90: grade = "A"
        elif percentage >= 80: grade = "B"
        elif percentage >= 70: grade = "C"
        elif percentage >= 60: grade = "D"
        else: grade = "F"
        
        # Generate Outcome Statement
        # "Your score reflects how ready AI systems are to confidently cite, trust, and act on behalf of your brand. 
        # {Strong} is strong, but {Weak} signals are limiting visibility."
        
        strong_layers = [l.name for l in layer_scores if l.percentage >= 80]
        weak_layers = [l.name for l in layer_scores if l.percentage < 60]
        
        base_sentence = "Your score reflects how ready AI systems are to confidently cite, trust, and act on behalf of your brand."
        
        dynamic_part = ""
        if not strong_layers and not weak_layers:
             dynamic_part = "You have a balanced visibility profile with room for optimization."
        elif not weak_layers:
            dynamic_part = "Your visibility performance is strong across all tracked layers."
        elif not strong_layers:
            dynamic_part = "Foundational improvements are needed across multiple layers to establish visibility."
        else:
            # We have mix
            strong_text = f"{strong_layers[0]}" if len(strong_layers) == 1 else "Structural health" # simplified fallback if multiple or complex
            # For brevity/readability, let's pick the "best" strong and group the weaks
            
            # Simple list join
            if len(strong_layers) > 0:
                s_part = f"{', '.join(strong_layers[:2])} {'is' if len(strong_layers)==1 else 'are'} strong"
            
            w_part = ""
            if len(weak_layers) > 0:
                # Group 4 & 5 often go together as "authority and automation"
                if "Authority & Reinforcement" in weak_layers and "Automation Readiness" in weak_layers:
                    w_part = "authority and automation signals are limiting visibility"
                else:
                    w_part = f"{weak_layers[0].lower()} signals are limiting visibility"
            
            dynamic_part = f"{s_part}, but {w_part}."

        summary_text = f"{base_sentence} {dynamic_part}"
        
        return OverallScore(
            total_points=total_points,
            max_total_points=max_total,
            grade=grade,
            summary_text=summary_text,
            layer_scores=layer_scores
        )
