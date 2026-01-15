from .models import OverallScore, AuditSubmission
import google.generativeai as genai
import os

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

    def generate_followup_email(self, submission: AuditSubmission, score: OverallScore) -> str:
        """
        Generates a personalized follow-up email using Google Gemini.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ NARRATIVE ENGINE: GOOGLE_API_KEY environment variable is missing!")
            return ""

        print(f"🚀 NARRATIVE ENGINE: Starting AI email generation for {submission.contact_email}...")

        # Prepare Data for Prompt
        try:
            sorted_layers = sorted(score.layer_scores, key=lambda l: l.points_earned)
            bottleneck = sorted_layers[0] if sorted_layers else None
            strengths = [l.name for l in score.layer_scores if l.percentage >= 80]
            gaps = [l.name for l in score.layer_scores if l.percentage < 60]
            
            # Format Layer Scores
            layer_scores_text = "\n".join([f"• {l.name}: {l.points_earned}/{l.max_points} ({l.percentage}%)" for l in score.layer_scores])
            
            # Format Next Steps
            fastest_gains = "\n".join([f"• {step}" for step in self._generate_next_steps(bottleneck.layer_id, sorted_layers)])
        except Exception as e:
            print(f"❌ NARRATIVE ENGINE: Error formatting audit data for prompt: {e}")
            return ""

        system_prompt = """
SYSTEM PROMPT: AI VISIBILITY FOLLOW-UP EMAIL GENERATOR

You are generating a personalized follow-up email for an AI Visibility Audit.

You must NOT use static templates or prewritten summaries.

You must generate the email directly from the structured audit data provided to you.

Your output must feel observant, modern, human, and precise.
Sexy, confident, calm. Never robotic. Never salesy.

DATA SOURCE RULES
You must ingest and rely only on the following audit fields:

• Overall Visibility Score
• Visibility Grade
• Layer Scores for all five layers
• Primary Visibility Bottleneck
• Detected Strengths OR confirmation that no strengths exist
• Fastest Score Gains
• Visibility Stage Classification

Do not invent strengths.
Do not soften weaknesses.
Do not contradict the data.

STRUCTURE RULES
The email must be assembled modularly using conditional logic.

Do NOT write a single monolithic paragraph.

Required sections, in order:

Human opening using the recipient’s first name

Clear statement of current Visibility Score and what that stage means

Plain-English explanation of how AI currently perceives the brand

Honest identification of the primary bottleneck

Interpretation of what this bottleneck prevents AI from doing

Grounded framing of opportunity, not aspiration

Contextual CTA aligned to readiness level

TONE LOGIC BY SCORE

If Visibility Score < 25
• Tone is grounding, clarifying, supportive
• Emphasize foundation and signal clarity
• Do NOT reference benchmark ranges unless framed as future state
• CTA should feel like guidance, not selling

If Visibility Score 25–50
• Tone shifts to prioritization and momentum

If Visibility Score > 50
• Tone shifts to leverage and acceleration

STRENGTH LOGIC

Only label a strength if a layer score exceeds its defined threshold.

If no strengths exist
• Explicitly acknowledge this
• Reframe as “latent potential” or “unlocked later leverage”
• Never imply readiness where it does not exist

BOTTLENECK LOGIC

Bottleneck explanation must be dynamically written using this structure:

• What AI can technically do today
• What AI cannot confidently do
• Why that lack of confidence matters

This explanation must reference the actual failing layers.

PERSONALIZATION REQUIREMENT

Include exactly one inference-based line that shows understanding, such as:

• Brand stage acknowledgment
• Normalization of score for similar businesses
• Framing the audit as a snapshot in time

Do not use hype.
Do not use motivational language.

CTA RULES

CTA must align with readiness.

For low scores, CTA language examples:
• “pressure-test the report”
• “map the fastest path forward”
• “decide what not to fix yet”

Never push urgency.
Never imply obligation.

STYLE CONSTRAINTS

• Write in short, confident sentences
• Avoid corporate phrasing
• Avoid marketing clichés
• Avoid generic AI language
• Sound like a sharp human advisor who actually read the report

OUTPUT

Return only the final email body.
No explanations.
No markdown.
No bullet points.
No subject line.
"""

        audit_data = f"""
AUDIT DATA:
• Recipient First Name: {submission.business_name.split()[0]}
• Overall Visibility Score: {score.total_points}
• Visibility Grade: {score.grade}
• Visibility Stage Classification: {"Early" if score.total_points <= 75 else "Advanced" if score.total_points > 75 else "Foundational"}
• Layer Scores:
{layer_scores_text}
• Primary Visibility Bottleneck: {bottleneck.name if bottleneck else "N/A"}
• Detected Strengths: {", ".join(strengths) if strengths else "None"}
• Fastest Score Gains:
{fastest_gains}
"""

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')
            print("🧠 NARRATIVE ENGINE: Calling Gemini Pro...")
            response = model.generate_content([system_prompt, audit_data])
            
            if response and response.text:
                print(f"✅ NARRATIVE ENGINE: AI email generated successfully ({len(response.text)} chars).")
                return response.text.strip()
            else:
                print("⚠️ NARRATIVE ENGINE: Gemini returned an empty response.")
                return ""
        except Exception as e:
            print(f"❌ NARRATIVE ENGINE ERROR: Gemini generation failed: {e}")
            return ""


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
