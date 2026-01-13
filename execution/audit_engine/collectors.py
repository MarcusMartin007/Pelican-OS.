import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from .models import AuditTask, TaskStatus, AuditSubmission
from .utils import normalize_url

class BaseCollector:
    def __init__(self, submission: AuditSubmission):
        self.submission = submission
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.soup: Optional[BeautifulSoup] = None

    def fetch_page(self, url: str) -> Optional[str]:
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def parse_homepage(self):
        if not self.soup:
            html = self.fetch_page(self.submission.website_url)
            if html:
                self.soup = BeautifulSoup(html, 'lxml')

    def collect(self) -> List[AuditTask]:
        """Override this method in subclasses"""
        return []

class Layer1Collector(BaseCollector):
    """
    Layer 1: Entity Clarity
    Only identity signals: Business Name, NAP, About, Contact, Org Schema, Social Links.
    """
    def collect(self) -> List[AuditTask]:
        self.parse_homepage()
        tasks = []
        
        # 1. Check Business Name Presence (Identity)
        tasks.append(self.check_business_name())
        
        # 2. Check Phone Number (NAP)
        tasks.append(self.check_phone_number())
        
        # 3. Check About Page (Identity)
        tasks.append(self.check_about_page())
        
        # 4. Check Contact Page (Contact Clarity)
        tasks.append(self.check_contact_page())

        # 5. Check Social Profile Linkage (Identity)
        tasks.append(self.check_social_links())

        # 6. Check Organization Schema (Identity)
        tasks.append(self.check_org_schema())
        
        # 7. Check GBP Presence (External Identity) - NEW
        tasks.append(self.check_gbp_presence())
        
        return tasks

    # ... existing methods check_business_name to check_org_schema ...
    def check_business_name(self) -> AuditTask:
        task = AuditTask(task_id="L1_NAME", layer=1, name="Business Name Consistency", description="Verifies name on homepage", max_points=3)
        if not self.soup:
            task.status = TaskStatus.FAIL; task.reasoning = "Could not reach homepage."
            return task
        text = self.soup.get_text().lower()
        if self.submission.business_name.lower() in text:
            task.status = TaskStatus.PASS; task.score_impact = 3; task.reasoning = f"Found '{self.submission.business_name}'."
        else:
            task.status = TaskStatus.WARN; task.score_impact = 0; task.reasoning = f"Name '{self.submission.business_name}' not found exactly."
        return task

    def check_phone_number(self) -> AuditTask:
        task = AuditTask(task_id="L1_NAP", layer=1, name="NAP Consistency", description="Checks for visible phone number", max_points=3)
        if not self.soup: return task
        phone_pattern = r'(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}'
        matches = re.findall(phone_pattern, self.soup.get_text())
        if matches:
            task.status = TaskStatus.PASS; task.score_impact = 3; task.reasoning = "Found potential phone number."
            task.evidence = {"matches": matches[:3]}
        else:
            task.status = TaskStatus.WARN; task.reasoning = "No obvious phone number format found."
        return task

    def check_about_page(self) -> AuditTask:
        task = AuditTask(task_id="L1_ABOUT", layer=1, name="About Page Presence", description="Identity signal", max_points=3)
        if not self.soup: return task
        about_links = self.soup.find_all('a', href=True, string=re.compile(r'about', re.I))
        if about_links:
            task.status = TaskStatus.PASS; task.score_impact = 3; task.reasoning = "Found 'About' page link."
        else:
            task.status = TaskStatus.WARN; task.reasoning = "No 'About' link found."
        return task

    def check_contact_page(self) -> AuditTask:
        task = AuditTask(task_id="L1_CONTACT", layer=1, name="Contact Clarity", description="Contact page signal", max_points=3)
        if not self.soup: return task
        contact_links = self.soup.find_all('a', href=True, string=re.compile(r'contact', re.I))
        if contact_links:
            task.status = TaskStatus.PASS; task.score_impact = 3; task.reasoning = "Found 'Contact' page link."
        else:
            task.status = TaskStatus.WARN; task.reasoning = "No 'Contact' link found."
        return task

    def check_social_links(self) -> AuditTask:
        task = AuditTask(task_id="L1_SOCIAL", layer=1, name="Social Profile Linkage", description="Identity signal", max_points=4)
        if not self.soup: return task
        platforms = ['facebook.com', 'instagram.com', 'twitter.com', 'x.com', 'linkedin.com', 'youtube.com', 'tiktok.com']
        found = []
        for link in self.soup.find_all('a', href=True):
            href = link['href'].lower()
            for p in platforms:
                if p in href and p not in found: found.append(p)
        task.evidence = {"platforms": found}
        if len(found) >= 2:
            task.status = TaskStatus.PASS; task.score_impact = 4; task.reasoning = f"Linked to {len(found)} social profiles."
        elif len(found) == 1:
            task.status = TaskStatus.PASS; task.score_impact = 2; task.reasoning = f"Linked to 1 social profile."
        else:
            task.status = TaskStatus.WARN; task.reasoning = "No social profile links found."
        return task

    def check_org_schema(self) -> AuditTask:
        task = AuditTask(task_id="L1_SCHEMA", layer=1, name="Organization Schema", description="Identity structured data", max_points=4)
        if not self.soup: return task
        schemas = self.soup.find_all('script', type='application/ld+json')
        found_org = False
        for s in schemas:
            if s.string and ('"Organization"' in s.string or '"LocalBusiness"' in s.string):
                found_org = True; break
        if found_org:
            task.status = TaskStatus.PASS; task.score_impact = 4; task.reasoning = "Found Organization/LocalBusiness schema."
        else:
            task.status = TaskStatus.WARN; task.reasoning = "No Organization schema found."
        return task

    def check_gbp_presence(self) -> AuditTask:
        task = AuditTask(task_id="L1_GBP", layer=1, name="Google Business Link", description="Checks for GMB/GBP Link", max_points=4)
        if not self.soup: return task
        # Check for typical Google Maps or Business Profile shortlinks
        patterns = [r'google\.com/maps', r'g\.page', r'google\.com/business']
        found = False
        for link in self.soup.find_all('a', href=True):
            href = link['href'].lower()
            if any(re.search(p, href) for p in patterns):
                found = True; break
        
        if found:
            task.status = TaskStatus.PASS; task.score_impact = 4; task.reasoning = "Found link to Google Business Profile/Maps."
        else:
            task.status = TaskStatus.WARN; task.reasoning = "No direct link to Google Business Profile found."
        return task


class Layer2Collector(BaseCollector):
    # ... (No changes needed to L2 - L4 starts next)
    """
    Layer 2: Structural Accessibility
    Only crawlability and machine access: HTTPS, Robots, Sitemap, Performance, H1, Canonicals.
    """
    def collect(self) -> List[AuditTask]:
        tasks = []
        
        # 1. Check SSL (HTTPS)
        tasks.append(self.check_ssl())
        
        # 2. Check Robots.txt
        tasks.append(self.check_robots_txt())
        
        # 3. Check Sitemap
        tasks.append(self.check_sitemap())
        
        # 4. Check Performance (TTFB)
        tasks.append(self.check_performance())
        
        # 5. Check H1 Presence (Structural) - Moved from L3
        self.parse_homepage() # Need soup for H1
        tasks.append(self.check_h1_structure())

        # 6. Check Canalization (Canonicals) - NEW
        tasks.append(self.check_canonical())
        
        return tasks

    def check_ssl(self) -> AuditTask:
        task = AuditTask(task_id="L2_HTTPS", layer=2, name="HTTPS / SSL", description="Structural security", max_points=3)
        if self.submission.website_url.startswith("https://"):
            task.status = TaskStatus.PASS; task.score_impact = 3; task.reasoning = "Site uses HTTPS."
        else:
            task.status = TaskStatus.FAIL; task.reasoning = "Site does not use HTTPS."
        return task

    def check_robots_txt(self) -> AuditTask:
        task = AuditTask(task_id="L2_ROBOTS", layer=2, name="Robots.txt", description="Crawlability signal", max_points=3)
        parsed = urlparse(self.submission.website_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        try:
            resp = self.session.get(robots_url, timeout=5)
            if resp.status_code == 200:
                task.status = TaskStatus.PASS; task.score_impact = 3; task.reasoning = "Found robots.txt."
            else:
                task.status = TaskStatus.FAIL; task.reasoning = f"Robots.txt status {resp.status_code}."
        except: task.status = TaskStatus.FAIL; task.reasoning = "Could not fetch robots.txt."
        return task

    def check_sitemap(self) -> AuditTask:
        task = AuditTask(task_id="L2_SITEMAP", layer=2, name="Sitemap.xml", description="Crawlability signal", max_points=3)
        parsed = urlparse(self.submission.website_url)
        sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
        try:
            resp = self.session.get(sitemap_url, timeout=5)
            if resp.status_code == 200:
                task.status = TaskStatus.PASS; task.score_impact = 3; task.reasoning = "Found sitemap.xml."
            else:
                # Fallback to robots checking is skipped for brevity/strictness, assuming standard location for L2 check
                task.status = TaskStatus.WARN; task.reasoning = "Sitemap.xml not at root."
        except: task.status = TaskStatus.WARN; task.reasoning = "Could not check sitemap."
        return task

    def check_performance(self) -> AuditTask:
        task = AuditTask(task_id="L2_CORE_WEB", layer=2, name="Core Web Vitals (Proxy)", description="TTFB Performance", max_points=4)
        try:
            resp = self.session.get(self.submission.website_url, timeout=10)
            ttfb = resp.elapsed.total_seconds()
            if ttfb < 0.6: task.status = TaskStatus.PASS; task.score_impact = 4; task.reasoning = f"Fast TTFB: {ttfb:.2f}s"
            else: task.status = TaskStatus.WARN; task.score_impact = 2; task.reasoning = f"Slow TTFB: {ttfb:.2f}s"
        except: task.status = TaskStatus.FAIL; task.reasoning = "Performance check failed."
        return task

    def check_h1_structure(self) -> AuditTask:
        task = AuditTask(task_id="L2_H1", layer=2, name="H1 Presence", description="Structural hierarchy root", max_points=4)
        if not self.soup: return task
        h1s = self.soup.find_all('h1')
        if len(h1s) == 1: task.status = TaskStatus.PASS; task.score_impact = 4; task.reasoning = "Exactly one H1 tag."
        elif len(h1s) > 1: task.status = TaskStatus.WARN; task.score_impact = 2; task.reasoning = f"Multiple H1 tags ({len(h1s)})."
        else: task.status = TaskStatus.FAIL; task.reasoning = "No H1 tag found. This reduces AI confidence in page hierarchy."
        return task

    def check_canonical(self) -> AuditTask:
        task = AuditTask(task_id="L2_CANONICAL", layer=2, name="Canonical Tag", description="Indexability signal", max_points=3)
        if not self.soup: return task
        canonical = self.soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            task.status = TaskStatus.PASS; task.score_impact = 3; task.reasoning = "Found canonical tag."
        else:
            task.status = TaskStatus.WARN; task.reasoning = "No canonical tag found."
        return task


class Layer3Collector(BaseCollector):
    # ... (Keep existing L3)
    """
    Layer 3: Semantic Alignment
    Meaning and topical relevance: Taxonomy, Headings, FAQ, Keywords, Title/Meta relevance.
    """
    def collect(self) -> List[AuditTask]:
        self.parse_homepage()
        tasks = []
        if not self.soup: return tasks

        # 1. Title Relevance (Semantic)
        tasks.append(self.check_title_tag())
        
        # 2. Meta Desc Relevance (Semantic)
        tasks.append(self.check_meta_description())
        
        # 3. Heading Hierarchy (Structure of Meaning)
        tasks.append(self.check_heading_hierarchy())
        
        # 4. FAQ Presence (Semantic Depth)
        tasks.append(self.check_faq_schema()) # Or content check
        
        return tasks

    def check_title_tag(self) -> AuditTask:
        task = AuditTask(task_id="L3_TITLE", layer=3, name="Title Relevance", description="Topical alignment", max_points=5)
        title = self.soup.title.string if self.soup.title else None
        if title and 10 <= len(title) <= 70:
            task.status = TaskStatus.PASS; task.score_impact = 5; task.reasoning = "Title exists and is optimized length."
        else:
            task.status = TaskStatus.WARN; task.score_impact = 2; task.reasoning = "Title missing or suboptimal length."
        return task

    def check_meta_description(self) -> AuditTask:
        task = AuditTask(task_id="L3_META", layer=3, name="Meta Description", description="Semantic summary", max_points=5)
        meta = self.soup.find('meta', attrs={'name': 'description'})
        content = meta.get('content') if meta else None
        if content and 50 <= len(content) <= 300: # Widen range a bit
            task.status = TaskStatus.PASS; task.score_impact = 5; task.reasoning = "Meta description present."
        else:
            task.status = TaskStatus.WARN; task.score_impact = 0; task.reasoning = "Meta description missing or short."
        return task

    def check_heading_hierarchy(self) -> AuditTask:
        task = AuditTask(task_id="L3_HIERARCHY", layer=3, name="Heading Hierarchy", description="Structure of meaning", max_points=5)
        # Check presence of H2s or H3s
        h2s = self.soup.find_all('h2')
        if h2s:
            task.status = TaskStatus.PASS; task.score_impact = 5; task.reasoning = f"Found {len(h2s)} H2 subheadings for content structure."
        else:
            task.status = TaskStatus.WARN; task.score_impact = 2; task.reasoning = "No H2 headings found (flat structure)."
        return task

    def check_faq_schema(self) -> AuditTask:
        task = AuditTask(task_id="L3_FAQ", layer=3, name="FAQ / Semantic Depth", description="FAQ Schema or Content", max_points=5)
        # Check for FAQPage schema
        schemas = self.soup.find_all('script', type='application/ld+json')
        found_faq = False
        for s in schemas:
            if s.string and '"FAQPage"' in s.string: found_faq = True; break
        
        if found_faq:
            task.status = TaskStatus.PASS; task.score_impact = 5; task.reasoning = "Found FAQPage Schema."
        else:
            # Fallback: check for "FAQ" text in headings/links
            if self.soup.find('a', string=re.compile(r'faq', re.I)) or self.soup.find(re.compile(r'h[1-6]'), string=re.compile(r'faq', re.I)):
                task.status = TaskStatus.PASS; task.score_impact = 3; task.reasoning = "Found FAQ content signals (link/heading)."
            else:
                task.status = TaskStatus.WARN; task.score_impact = 0; task.reasoning = "No FAQ schema or content found."
        return task


class Layer4Collector(BaseCollector):
    """
    Layer 4: Authority & Reinforcement
    Only trust signals: Reviews, Citations, Author/Founder Schema. NO Technical checks.
    """
    def collect(self) -> List[AuditTask]:
        self.parse_homepage()
        tasks = []
        if not self.soup: return tasks

        # 1. Reviews / Third-Party Detection
        tasks.append(self.check_reviews())
        
        # 2. Directory/Citation signals (External links out to directories or badges)
        tasks.append(self.check_citations())

        return tasks

    def check_reviews(self) -> AuditTask:
        task = AuditTask(task_id="L4_REVIEWS", layer=4, name="Reviews & Reputation", description="Trust signal", max_points=10)
        review_platforms = ['google.com', 'yelp.com', 'trustpilot.com', 'tripadvisor.com', 'facebook.com']
        
        found = []
        # Check actual links to profile
        for link in self.soup.find_all('a', href=True):
            href = link['href'].lower()
            if any(p in href for p in review_platforms):
                found.append(href)

        if found:
            task.status = TaskStatus.PASS; task.score_impact = 10; task.reasoning = f"Found {len(found)} external review profiles linked."
            task.evidence = {"links": found}
        else:
             task.status = TaskStatus.WARN; task.score_impact = 0; task.reasoning = "No direct links to active review profiles found."
        return task

    def check_citations(self) -> AuditTask:
        task = AuditTask(task_id="L4_CITATIONS", layer=4, name="Citations / Directories", description="Trust signal", max_points=10)
        # Check for BBB, Chamber of commerce, Industry certs
        directories = ['bbb.org', 'chamber', 'yellowpages', 'superpages']
        links = [a['href'] for a in self.soup.find_all('a', href=True)]
        found = []
        for l in links:
            if any(d in l.lower() for d in directories):
                found.append(l)
        
        if found:
            task.status = TaskStatus.PASS; task.score_impact = 10; task.reasoning = "Found citation/directory badges or links."
        else:
            task.status = TaskStatus.WARN; task.score_impact = 0; task.reasoning = "No common directory/citation links found on home."
        return task


class Layer5Collector(BaseCollector):
    """
    Layer 5: Automation Readiness
    Only action enablement: Conversion, Chat, Newsletter, Tracking.
    """
    def collect(self) -> List[AuditTask]:
        self.parse_homepage()
        tasks = []
        if not self.soup: return tasks

        # 1. Chat/Conversational Entry
        tasks.append(self.check_chat())

        # 2. Tracking/CRM Signals (Analytics)
        tasks.append(self.check_tracking())

        # 3. Newsletter/Capture
        tasks.append(self.check_capture())

        return tasks

    def check_chat(self) -> AuditTask:
        task = AuditTask(task_id="L5_CHAT", layer=5, name="Conversational Entry", description="Action enablement", max_points=5)
        widgets = ['intercom', 'drift', 'tawk', 'crisp', 'zendesk', 'hubspot', 'tidio', 'chat']
        found = False
        html = str(self.soup).lower()
        for w in widgets:
            if w in html: found = True; break
        
        if found: task.status = TaskStatus.PASS; task.score_impact = 5; task.reasoning = "Found chat widget/code."
        else: task.status = TaskStatus.WARN; task.reasoning = "No chat widget detected."
        return task

    def check_tracking(self) -> AuditTask:
        task = AuditTask(task_id="L5_TRACKING", layer=5, name="CRM/Tracking Signals", description="Action enablement", max_points=5)
        signals = ['googletagmanager', 'analytics', 'fbq(', 'hubspot', 'segment']
        html = str(self.soup).lower()
        found = []
        for s in signals:
            if s in html: found.append(s)
        
        if found: task.status = TaskStatus.PASS; task.score_impact = 5; task.reasoning = f"Found tracking signals: {','.join(found)}."
        else: task.status = TaskStatus.WARN; task.reasoning = "No major tracking/CRM scripts found."
        return task

    def check_capture(self) -> AuditTask:
        task = AuditTask(task_id="L5_CAPTURE", layer=5, name="Lead Capture", description="Action enablement", max_points=5)
        # Look for form tags or inputs
        forms = self.soup.find_all('form')
        if forms:
            task.status = TaskStatus.PASS; task.score_impact = 5; task.reasoning = f"Found {len(forms)} HTML forms (potential lead capture)."
        else:
            task.status = TaskStatus.WARN; task.reasoning = "No native HTML forms found."
        return task

