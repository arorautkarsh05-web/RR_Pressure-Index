"""
RR PRESSURE INDEX 2027 — REPOSITORY INVENTORY SCANNER
Generates reports/audit/REPOSITORY_INVENTORY.md
Classifies every file in the repository into Categories A-I.
"""

import os
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("D:/RR_PRESSURE_INDEX_2027")
AUDIT_DIR = BASE_DIR / "reports" / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = AUDIT_DIR / "REPOSITORY_INVENTORY.md"

def classify_file(rel_path_str, size_bytes):
    p = Path(rel_path_str)
    parts = p.parts
    ext = p.suffix.lower()
    name = p.name

    # Check for temporary/cache files
    if "__pycache__" in parts or ext == ".pyc" or name in [".DS_Store", "Thumbs.db", "desktop.ini"]:
        return "G. TEMPORARY FILE"

    # Raw data
    if len(parts) >= 2 and parts[0] == "data" and parts[1] == "raw":
        return "B. ESSENTIAL DATA FILE"
        
    # Processed data
    if len(parts) >= 2 and parts[0] == "data" and parts[1] == "processed":
        return "B. ESSENTIAL DATA FILE"

    # Core source files
    if parts[0] == "src" and ext == ".py":
        return "A. ESSENTIAL SOURCE FILE"

    # Core scripts
    if parts[0] == "scripts" and ext in [".py", ".ps1", ".sh"]:
        return "A. ESSENTIAL SOURCE FILE"

    # Jupyter notebooks
    if parts[0] == "notebooks" and ext == ".ipynb":
        return "C. ESSENTIAL ANALYTICAL OUTPUT"

    # Dashboard source code and schema
    if parts[0] == "dashboard":
        if ext in [".dax", ".m", ".json", ".pbip", ".pbir", ".pbism", ".bim", ".html", ".js", ".css"]:
            return "A. ESSENTIAL SOURCE FILE"
        elif ext == ".md":
            return "D. ESSENTIAL DOCUMENTATION"
        elif ext == ".csv":
            return "E. GENERATED REPRODUCIBLE OUTPUT"
        elif ext == ".pdf":
            return "F. DUPLICATE DELIVERABLE"

    # Outputs: Final submission
    if len(parts) >= 2 and parts[0] == "outputs" and parts[1] == "final_submission":
        if ext in [".csv", ".xlsx"]:
            return "C. ESSENTIAL ANALYTICAL OUTPUT"
        elif ext in [".pdf", ".pptx"]:
            return "C. ESSENTIAL ANALYTICAL OUTPUT"
        elif ext in [".md", ".html"]:
            return "D. ESSENTIAL DOCUMENTATION"

    # Outputs: tables / rankings / charts / audit
    if parts[0] == "outputs":
        if parts[1] in ["tables", "rankings"]:
            return "C. ESSENTIAL ANALYTICAL OUTPUT"
        elif parts[1] in ["charts"]:
            return "E. GENERATED REPRODUCIBLE OUTPUT"
        elif parts[1] in ["audit"]:
            return "E. GENERATED REPRODUCIBLE OUTPUT"
        elif parts[1] in ["dashboard"]:
            return "E. GENERATED REPRODUCIBLE OUTPUT"

    # Documentation in report/ or reports/
    if parts[0] in ["report", "reports"]:
        if ext == ".md":
            return "D. ESSENTIAL DOCUMENTATION"
        elif ext == ".pdf":
            return "C. ESSENTIAL ANALYTICAL OUTPUT"

    # Root files
    if len(parts) == 1:
        if ext == ".md":
            return "D. ESSENTIAL DOCUMENTATION"
        elif ext in [".pdf", ".pptx", ".xlsx", ".zip"]:
            return "C. ESSENTIAL ANALYTICAL OUTPUT"

    return "I. UNKNOWN — REQUIRES INVESTIGATION"

def scan_repository():
    all_files = []
    category_counts = defaultdict(int)
    category_sizes = defaultdict(int)
    ext_counts = defaultdict(int)
    ext_sizes = defaultdict(int)
    
    total_size = 0

    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            full_path = Path(root) / f
            try:
                rel_path = full_path.relative_to(BASE_DIR)
                size = full_path.stat().st_size
                ext = full_path.suffix.lower() or "(no ext)"
                
                cat = classify_file(str(rel_path), size)
                
                all_files.append({
                    "rel_path": str(rel_path).replace("\\", "/"),
                    "size": size,
                    "ext": ext,
                    "cat": cat
                })
                
                category_counts[cat] += 1
                category_sizes[cat] += size
                ext_counts[ext] += 1
                ext_sizes[ext] += size
                total_size += size
            except Exception as e:
                print(f"Error accessing {full_path}: {e}")

    all_files.sort(key=lambda x: (x["cat"], x["rel_path"]))

    lines = []
    lines.append("# RR PRESSURE INDEX 2027: COMPLETE REPOSITORY INVENTORY")
    lines.append("## Phase 1 Audit: Comprehensive Asset & Artifact Classification\n")
    lines.append(f"**Audit Timestamp:** 2026-11-11 | **Repository Root:** `{BASE_DIR}`\n")
    lines.append("---\n")
    lines.append("### 1. Repository Macro Metrics\n")
    lines.append(f"- **Total Number of Files:** {len(all_files):,}")
    lines.append(f"- **Total Repository Size:** {total_size:,} bytes ({total_size / (1024*1024):.2f} MB)")
    lines.append(f"- **Distinct File Extensions:** {len(ext_counts)}\n")
    
    lines.append("### 2. Breakdown by File Classification Category\n")
    lines.append("| Category Code & Description | File Count | Total Size (Bytes) | Total Size (MB) | % of Repo Size |")
    lines.append("| :--- | :---: | :---: | :---: | :---: |")
    for cat in sorted(category_counts.keys()):
        c_count = category_counts[cat]
        c_size = category_sizes[cat]
        c_mb = c_size / (1024*1024)
        c_pct = (c_size / total_size) * 100 if total_size > 0 else 0
        lines.append(f"| **{cat}** | {c_count:,} | {c_size:,} | {c_mb:.2f} MB | {c_pct:.2f}% |")
    lines.append(f"| **TOTAL** | **{len(all_files):,}** | **{total_size:,}** | **{total_size / (1024*1024):.2f} MB** | **100.00%** |\n")

    lines.append("### 3. Breakdown by File Extension\n")
    lines.append("| File Extension | Count | Total Size (Bytes) | Total Size (MB) |")
    lines.append("| :--- | :---: | :---: | :---: |")
    for ext, count in sorted(ext_counts.items(), key=lambda x: x[1], reverse=True):
        sz = ext_sizes[ext]
        lines.append(f"| `{ext}` | {count:,} | {sz:,} | {sz / (1024*1024):.2f} MB |")
    lines.append("\n---\n")

    lines.append("### 4. Granular File Inventory & Classification Table\n")
    lines.append("| Relative File Path | Size (Bytes) | Extension | Classification Category |")
    lines.append("| :--- | :---: | :---: | :--- |")
    for f in all_files:
        lines.append(f"| `{f['rel_path']}` | {f['size']:,} | `{f['ext']}` | {f['cat']} |")
    lines.append("\n---\n")
    lines.append("*Generated by automated Phase 1 repository audit pipeline.*")

    OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"[+] Successfully generated: {OUT_FILE} ({OUT_FILE.stat().st_size:,} bytes)")
    print(f"[+] Total files inventoried: {len(all_files):,}, Total size: {total_size / (1024*1024):.2f} MB")

if __name__ == "__main__":
    scan_repository()
