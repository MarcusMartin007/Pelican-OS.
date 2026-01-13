from playwright.sync_api import sync_playwright
import jinja2
import os
from .models import AuditResult

class PDFReporter:
    def __init__(self, template_path: str = "templates/report_template.html"):
        self.template_path = template_path
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(template_path))))

    def generate_html(self, result: AuditResult) -> str:
        template = self.env.get_template(os.path.basename(self.template_path))
        return template.render(
            submission=result.submission,
            overall_score=result.overall_score
        )

    def generate_pdf(self, result: AuditResult, output_path: str):
        html_content = self.generate_html(result)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(html_content)
            page.pdf(path=output_path, format="A4", print_background=True)
            browser.close()
        
        print(f"PDF generated at: {output_path}")
