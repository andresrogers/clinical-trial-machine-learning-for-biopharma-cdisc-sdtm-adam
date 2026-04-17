#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="${1:-$PWD}"
ARCHIVE_DIR="$ROOT_DIR/data/external/archives"
CDISC_RAW_DIR="$ROOT_DIR/data/external/cdisc_pilot/raw_xpt"
CDISC_META_DIR="$ROOT_DIR/data/external/cdisc_pilot/metadata"
CDISC_CSR_DIR="$ROOT_DIR/data/external/cdisc_pilot/csr"
CLINTRIALDATA_DIR="$ROOT_DIR/data/external/clintrialdata"
SAFETYDATA_DIR="$ROOT_DIR/data/external/safetydata"
PHARMAVERSE_REF_DIR="$ROOT_DIR/docs/reference/pharmaverse"
REG_REF_DIR="$ROOT_DIR/docs/reference/regulatory"

mkdir -p \
  "$ARCHIVE_DIR" \
  "$CDISC_RAW_DIR" \
  "$CDISC_META_DIR" \
  "$CDISC_CSR_DIR" \
  "$CLINTRIALDATA_DIR" \
  "$SAFETYDATA_DIR" \
  "$ROOT_DIR/data/interim" \
  "$ROOT_DIR/data/derived" \
  "$ROOT_DIR/data/generated" \
  "$ROOT_DIR/metadata" \
  "$ROOT_DIR/qc" \
  "$ROOT_DIR/config" \
  "$ROOT_DIR/src/ingest" \
  "$ROOT_DIR/src/transform" \
  "$ROOT_DIR/src/modeling" \
  "$ROOT_DIR/src/reporting" \
  "$PHARMAVERSE_REF_DIR" \
  "$REG_REF_DIR"

download() {
  local url="$1"
  local dest="$2"
  local tmp="${dest}.part"
  mkdir -p "$(dirname "$dest")"
  rm -f "$tmp"
  if command -v curl >/dev/null 2>&1; then
    curl -fL --retry 4 --retry-delay 2 --retry-all-errors -o "$tmp" "$url"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$tmp" "$url"
  else
    echo "ERROR: neither curl nor wget is installed" >&2
    exit 1
  fi
  mv "$tmp" "$dest"
}

echo "Downloading archives..."
download "https://codeload.github.com/cdisc-org/sdtm-adam-pilot-project/zip/refs/heads/master" "$ARCHIVE_DIR/cdisc-pilot-master.zip"
download "https://cran.r-project.org/src/contrib/clinTrialData_0.1.3.tar.gz" "$CLINTRIALDATA_DIR/clinTrialData_0.1.3.tar.gz"
download "https://codeload.github.com/SafetyGraphics/safetyData/zip/refs/heads/main" "$ARCHIVE_DIR/safetyData-main.zip"

echo "Extracting required files..."
TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

python3 - <<'PY' "$ARCHIVE_DIR/cdisc-pilot-master.zip" "$TMP_DIR/cdisc" "$CDISC_RAW_DIR" "$CDISC_META_DIR" "$CDISC_CSR_DIR"
import os, sys, zipfile, shutil
zip_path, tmp_root, raw_dir, meta_dir, csr_dir = sys.argv[1:6]
needed = {"dm.xpt","ae.xpt","lb.xpt","vs.xpt","ex.xpt","ds.xpt","adsl.xpt","adae.xpt","adlbc.xpt","adlbh.xpt","adtte.xpt","advs.xpt"}
os.makedirs(tmp_root, exist_ok=True)
with zipfile.ZipFile(zip_path) as z:
    z.extractall(tmp_root)
for root, _, files in os.walk(tmp_root):
    for f in files:
        fl = f.lower()
        path = os.path.join(root, f)
        if "/updated-pilot-submission-package/900172/m5/datasets/" in path.replace('\\','/').lower() and fl in needed:
            shutil.copy2(path, os.path.join(raw_dir, fl))
        elif 'define' in fl and (fl.endswith('.xml') or fl.endswith('.pdf')):
            shutil.copy2(path, os.path.join(meta_dir, f))
        elif fl.startswith('cdiscpilot01') and fl.endswith('.pdf'):
            shutil.copy2(path, os.path.join(csr_dir, f))
        elif '/53-clin-stud-rep/' in path.replace('\\','/').lower():
            shutil.copy2(path, os.path.join(csr_dir, f))
PY

python3 - <<'PY' "$ARCHIVE_DIR/safetyData-main.zip" "$TMP_DIR/safety" "$SAFETYDATA_DIR"
import os, sys, zipfile, shutil
zip_path, tmp_root, out_dir = sys.argv[1:4]
os.makedirs(tmp_root, exist_ok=True)
with zipfile.ZipFile(zip_path) as z:
    z.extractall(tmp_root)
for root, _, files in os.walk(tmp_root):
    for f in files:
        fl = f.lower()
        path = os.path.join(root, f)
        norm = path.replace('\\','/').lower()
        if '/data/' in norm or fl.startswith('readme') or fl == 'description':
            shutil.copy2(path, os.path.join(out_dir, f))
PY

cat > "$PHARMAVERSE_REF_DIR/links.txt" <<'EOF'
https://pharmaverse.github.io/examples
https://pharmaverse.github.io/examples/sdtm
https://pharmaverse.github.io/examples/adam
https://pharmaverse.github.io/examples/tlg
https://github.com/pharmaverse/admiral
EOF

cat > "$REG_REF_DIR/links.txt" <<'EOF'
https://www.cdisc.org/standards/foundational/sdtmig/sdtmig-v3-3/html
https://www.cdisc.org/standards/foundational/adam
https://www.fda.gov/media/133252/download
https://www.ema.europa.eu/
EOF

echo "Done."
echo "Root: $ROOT_DIR"
find "$ROOT_DIR/data/external" -maxdepth 3 -type f | sort
