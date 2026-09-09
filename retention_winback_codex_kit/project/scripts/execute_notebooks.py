"""Execute walkthroughs using the project interpreter; keep outputs out of Git."""

import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
from retention.common import ROOT, run_dir, save, now

mode = sys.argv[1] if len(sys.argv) > 1 else "full"
kernels = ROOT / ".cache/kernels"
save(
    kernels / "retention/kernel.json",
    {
        "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
        "display_name": "Retention local",
        "language": "python",
    },
)
manager = KernelSpecManager(kernel_dirs=[str(kernels)])
results = []
for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
    nb = nbformat.read(path, as_version=4)
    nb.cells[1].source = (
        nb.cells[1]
        .source.replace("MODE='dev'", f"MODE='{mode}'")
        .replace("MODE='full'", f"MODE='{mode}'")
    )
    km = KernelManager(kernel_name="retention", kernel_spec_manager=manager)
    NotebookClient(
        nb, km=km, timeout=120, resources={"metadata": {"path": str(ROOT)}}
    ).execute()
    out = run_dir(mode) / "executed_notebooks" / path.name
    out.parent.mkdir(exist_ok=True)
    nbformat.write(nb, out)
    results.append({"notebook": path.name, "status": "passed", "time": now()})
    print(path.name, "passed", flush=True)
save(run_dir(mode) / "execution/notebooks.json", results)
