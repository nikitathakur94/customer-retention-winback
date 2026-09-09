"""Convert the validated editable deck with the bundled headless renderer."""

import os, subprocess, sys, shutil
from pathlib import Path
from retention.common import ROOT, run_dir, read, save, digest

mode = sys.argv[1] if len(sys.argv) > 1 else "full"
p = run_dir(mode)
runtime = Path(
    os.environ.get(
        "CODEX_ARTIFACT_RUNTIME",
        "/Users/nik/.cache/codex-runtimes/codex-primary-runtime/dependencies",
    )
)
info = read(p / "slides/presentation_provenance.json")
pptx = Path(info["pptx"])
fontconfig = ROOT / ".cache/fonts.conf"
fontconfig.parent.mkdir(exist_ok=True)
fontconfig.write_text(
    f"<fontconfig><dir>/System/Library/Fonts</dir><dir>/System/Library/Fonts/Supplemental</dir><dir>/Library/Fonts</dir><cachedir>{ROOT / '.cache/fontconfig'}</cachedir></fontconfig>"
)
env = os.environ.copy()
env["FONTCONFIG_FILE"] = str(fontconfig)
subprocess.run(
    [
        str(runtime / "bin/override/soffice"),
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(p / "slides"),
        str(pptx),
    ],
    check=True,
    env=env,
)
pdf = pptx.with_suffix(".pdf")
if not pdf.exists():
    raise RuntimeError("Renderer did not create PDF")
shutil.copy2(pptx, p / "slides/deck.pptx")
shutil.copy2(pdf, p / "slides/deck.pdf")
preview = p / "slides/pdf_preview"
preview.mkdir(exist_ok=True)
subprocess.run(
    [
        str(runtime / "bin/override/pdftoppm"),
        "-scale-to",
        "1280",
        "-png",
        str(p / "slides/deck.pdf"),
        str(preview / "slide"),
    ],
    check=True,
)
save(
    p / "slides/delivery.json",
    {
        "pptx": "deck.pptx",
        "pdf": "deck.pdf",
        "pptx_sha256": digest(p / "slides/deck.pptx"),
        "pdf_sha256": digest(p / "slides/deck.pdf"),
        "render_method": "bundled headless LibreOffice and Poppler; not opened in Microsoft PowerPoint",
    },
)
