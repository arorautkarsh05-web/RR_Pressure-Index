"""
RR AUCTION INTELLIGENCE 2027 — DASHBOARD PDF EXPORT ENGINE
Generates 4 high-resolution franchise-grade PDF exports:
1. executive_overview.pdf
2. batting_intelligence.pdf
3. bowling_intelligence.pdf
4. auction_intelligence.pdf
"""

import os
import subprocess
import time
from pathlib import Path

BASE_DIR = Path("D:/RR_PRESSURE_INDEX_2027")
HTML_DIR = BASE_DIR / "dashboard" / "html"
EXPORTS_DIR = BASE_DIR / "dashboard" / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

BROWSER_EXE = EDGE_EXE if os.path.exists(EDGE_EXE) else CHROME_EXE

print(f"[*] Using Browser Binary: {BROWSER_EXE}")

# Read master index.html
with open(HTML_DIR / "index.html", "r", encoding="utf-8") as f:
    master_html = f.read()

PAGES = [
    {
        "id": "executive_overview",
        "tab_id": "tab-overview",
        "render_call": "renderExecutiveOverview();",
        "filename": "executive_overview.pdf",
        "title": "Executive Overview"
    },
    {
        "id": "batting_intelligence",
        "tab_id": "tab-batting",
        "render_call": "renderBattingIntelligence();",
        "filename": "batting_intelligence.pdf",
        "title": "Batting Intelligence"
    },
    {
        "id": "bowling_intelligence",
        "tab_id": "tab-bowling",
        "render_call": "renderBowlingIntelligence();",
        "filename": "bowling_intelligence.pdf",
        "title": "Bowling Intelligence"
    },
    {
        "id": "auction_intelligence",
        "tab_id": "tab-auction",
        "render_call": "renderAuctionIntelligence();",
        "filename": "auction_intelligence.pdf",
        "title": "Auction Intelligence"
    }
]

def generate_export_html(page_config):
    tab_id = page_config["tab_id"]
    render_call = page_config["render_call"]
    page_id = page_config["id"]
    
    # Modify master HTML: make target tab active, others inactive
    modified = master_html
    # Remove active from all tab-pane
    modified = modified.replace('class="tab-pane active"', 'class="tab-pane"')
    # Add active to target tab-pane
    modified = modified.replace(f'id="{tab_id}" class="tab-pane"', f'id="{tab_id}" class="tab-pane active"')
    
    # Remove active from all nav-tab
    modified = modified.replace('class="nav-tab active"', 'class="nav-tab"')
    modified = modified.replace(f'class="nav-tab" data-target="{tab_id}"', f'class="nav-tab active" data-target="{tab_id}"')
    
    # Inject auto-trigger render script before closing body
    trigger_script = f"""
    <script>
      window.addEventListener('load', () => {{
        setTimeout(() => {{
          if (typeof {render_call} === 'function') {{
            {render_call}
          }}
        }}, 200);
      }});
    </script>
    </body>
    """
    modified = modified.replace("</body>", trigger_script)
    
    export_html_path = HTML_DIR / f"export_{page_id}.html"
    with open(export_html_path, "w", encoding="utf-8") as f:
        f.write(modified)
    
    return export_html_path

def convert_to_pdf(html_path, output_pdf):
    file_url = f"file:///{str(html_path).replace(os.sep, '/')}"
    cmd = [
        BROWSER_EXE,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={str(output_pdf)}",
        file_url
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[!] Error printing {html_path.name}: {result.stderr}")
    else:
        # Check output file
        if output_pdf.exists() and output_pdf.stat().st_size > 1000:
            print(f"[+] Successfully exported {output_pdf.name} ({output_pdf.stat().st_size:,} bytes)")
        else:
            print(f"[!] Output PDF not generated or too small: {output_pdf.name}")

def main():
    print("=== RR AUCTION INTELLIGENCE 2027: PDF EXPORT GENERATOR ===")
    start_time = time.time()
    
    for page in PAGES:
        print(f"\n[*] Processing: {page['title']}...")
        export_html = generate_export_html(page)
        out_pdf = EXPORTS_DIR / page["filename"]
        convert_to_pdf(export_html, out_pdf)
    
    elapsed = time.time() - start_time
    print(f"\n[+] PDF export run completed in {elapsed:.2f} seconds.")
    
    # Summary of generated PDFs
    print("\n=== GENERATED PDF SUMMARY ===")
    for page in PAGES:
        p = EXPORTS_DIR / page["filename"]
        if p.exists():
            print(f"  - {p.name}: {p.stat().st_size:,} bytes | Absolute: {p.resolve()}")
        else:
            print(f"  - {p.name}: MISSING")

if __name__ == "__main__":
    main()

