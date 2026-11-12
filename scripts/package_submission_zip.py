import os
import shutil
import zipfile

BASE_DIR = r"d:\RR_PRESSURE_INDEX_2027"
FINAL_SUB_DIR = os.path.join(BASE_DIR, "outputs", "final_submission")
ZIP_OUTPUT = os.path.join(BASE_DIR, "RR_PRESSURE_INDEX_2027_FINAL_SUBMISSION_PACKAGE.zip")

# Copy player_intelligence_summary.xlsx to root
src_xlsx = os.path.join(FINAL_SUB_DIR, "player_intelligence_summary.xlsx")
dst_xlsx = os.path.join(BASE_DIR, "RR_PRESSURE_INDEX_2027_PLAYER_INTELLIGENCE.xlsx")
if os.path.exists(src_xlsx):
    shutil.copy2(src_xlsx, dst_xlsx)
    print(f"[+] Copied {src_xlsx} to {dst_xlsx}")

# Create ZIP of outputs/final_submission
print(f"[*] Creating ZIP archive: {ZIP_OUTPUT}...")
with zipfile.ZipFile(ZIP_OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(FINAL_SUB_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, FINAL_SUB_DIR)
            zipf.write(file_path, arcname)
            print(f"  Added: {arcname}")

print(f"[SUCCESS] Archive generated: {ZIP_OUTPUT} ({os.path.getsize(ZIP_OUTPUT):,} bytes)")

