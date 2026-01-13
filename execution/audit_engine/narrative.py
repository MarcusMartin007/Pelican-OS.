from .models import OverallScore, AuditSubmission

class NarrativeEngine:
    """
    AI-Driven Narrative Enrichment (Non-Scored Module)
    Generates "AI Visibility Summary" by interpreting existing audit findings.
    """
    def __init__(self):
        pass

    def generate_narrative(self, submission: AuditSubmission, score: OverallScore) -> dict:
        """
        Synthesizes findings from layers to generate the narrative.
        In a real scenario, this would call Gemini Pro.
        Here, we use a robust heuristic-based generator as the 'Safe Fallback'.
        """
        
        # 1. Identify Bottleneck Layer (Lowest percentage)
        sorted_layers = sorted(score.layer_scores, key=lambda l: l.points_earned) # Use points for granularity
        bottleneck = sorted_layers[0] if sorted_layers else None
        second_weakest = sorted_layers[1] if len(sorted_layers) > 1 else None
        
        # 2. Identify Strengths/Gaps
        strengths = [l.name for l in score.layer_scores if l.percentage >= 80]
        gaps = [l.name for l in score.layer_scores if l.percentage < 60]
        
        # 3. Construct Narrative Sections
        
        # AI Readiness Explanation
        if score.total_points >= 80:
            readiness = "Your brand is highly visible to AI systems. Agents can confidently verify your identity and authority."
        elif score.total_points >= 50:
            readiness = "AI systems can find and understand your brand, but may hesitate to cite or recommend it due to authority and alignment gaps."
        else:
            readiness = "Your brand is currently invisible or untrusted by AI systems. Agents will likely ignore your entity in favor of clearer competitors."
            
        # Bottleneck Impact (Refined Nuance)
        # Check for compounded bottleneck (e.g., top 2 failures are close or specific combo)
        is_compounded = second_weakest and second_weakest.percentage < 60
        
        if is_compounded:
            impact = (f"The primary visibility constraint is a combination of {bottleneck.name} and {second_weakest.name}."
                      f" AI systems can access your site, but inconsistent hierarchy signals and limited third-party validation reduce confidence in citing or recommending your brand.")
        else:
            impact = f"The primary bottleneck is {bottleneck.name} ({bottleneck.grade}). This prevents AI agents from {self._get_bottleneck_impact(bottleneck.layer_id)}."

        # Strength Summary
        if strengths:
            str_summary = f"Strong signals detected in {', '.join(strengths[:3])}, providing a solid foundation."
        else:
            str_summary = "No dominant strengths detected yet; the foundation needs reinforcement."

        # Gap Summary
        if gaps:
            gap_summary = f"Critical gaps in {', '.join(gaps[:3])} are reducing your Visibility Score."
        else:
            gap_summary = "No critical failures detected, but optimization is possible."

        # Next Steps (Upgrades)
        next_steps = self._generate_next_steps(bottleneck.layer_id, sorted_layers)

        # Closing Line
        closing = "With targeted upgrades in structure and authority, your existing automation stack is well positioned to convert increased AI visibility into measurable lead flow."
        
        # Benchmark Text (Safe Fallback)
        benchmark = "Most businesses at this early visibility stage score between 55 and 75."

        return {
            "readiness_explanation": readiness,
            "bottleneck_impact": impact,
            "strength_summary": str_summary,
            "gap_summary": gap_summary,
            "fastest_gains": next_steps,
            "closing_line": closing,
            "benchmark_text": benchmark
        }

    def _get_bottleneck_impact(self, layer_id: int) -> str:
        impacts = {
            1: "unambiguously identifying who you are",
            2: "efficiently crawling and indexing your content",
            3: "understanding the semantic meaning of your services",
            4: "trusting your brand enough to recommend it",
            5: "taking action or converting traffic on your behalf"
        }
        return impacts.get(layer_id, "processing your site")

    def _generate_next_steps(self, bottleneck_id: int, sorted_layers) -> list:
        # Generate 3 prioritized steps. 
        steps = []
        
        # Step 1: Bottleneck
        steps.append(self._get_layer_fix(bottleneck_id))
        
        # Step 2: Next weakest
        if len(sorted_layers) > 1:
            steps.append(self._get_layer_fix(sorted_layers[1].layer_id))
            
        # Step 3: General L5 or Authority
        if bottleneck_id != 5:
             # Check if L5 is already perfect
             l5_layer = next((l for l in sorted_layers if l.layer_id == 5), None)
             if l5_layer and l5_layer.percentage >= 100:
                 steps.append("Monitor and optimize existing conversion interactions to ensure AI-driven traffic is captured efficiently.")
             else:
                 steps.append("Install a conversion interactions (Chat/Forms) to capture AI-driven traffic.")
        else:
             steps.append("Verify business details on 3rd-party knowledge graphs (Wikidata, Crunchbase) to solidify trust.")
             
        return steps[:3]

    def _get_layer_fix(self, layer_id: int) -> str:
        # "Action + Benefit" structure
        fixes = {
            1: "claim your Google Business Profile to lock in identity trust.",
            2: "add a homepage H1 tag to restore hierarchy signals.",
            3: "enrich Title Tags and Meta Descriptions to clarify semantic meaning.",
            4: "generate 3-5 new reviews on Google/Trustpilot to validate authority.",
            5: "implement a chat widget or lead capture form to become fully equipped."
        }
        # Prepend "Immediately" or "Action" verb if needed contextually, 
        # but the list format works best as imperative.
        # Let's Capitalize first letter.
        fix = fixes.get(layer_id, "optimize site structure.")
        return fix[0].upper() + fix[1:]
