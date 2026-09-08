"""Paths, provenance, and bounded local connections."""
from pathlib import Path
import hashlib, json, os
from datetime import datetime, timezone
import duckdb
ROOT = Path(__file__).resolve().parents[2]
CUTS = {'train':'2019-12-01','validation':'2019-12-30','test':'2020-01-28','latest_unlabeled':'2020-03-01'}
DISCLOSURE = 'Public-data reconstruction; not original Macy’s data, implementation, or measured company impact.'
def now(): return datetime.now(timezone.utc).isoformat()
def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()
def save(path, obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,default=str,allow_nan=False)+'\n')
def read(path): return json.loads(Path(path).read_text())
def run_dir(mode):
    if mode not in ('dev','full'): raise ValueError('mode must be dev or full; fixtures never enter results')
    p=ROOT/'artifacts'/f'{mode}-v1'; p.mkdir(parents=True,exist_ok=True); return p

def connect(mode,readonly=False):
    p=ROOT/'warehouse'; p.mkdir(exist_ok=True)
    con=duckdb.connect(str(p/f'{mode}.duckdb'),read_only=readonly)
    con.execute("SET TimeZone='UTC'")
    if not readonly:
        spill=ROOT/'.cache'/f'spill-{mode}'; spill.mkdir(parents=True,exist_ok=True)
        con.execute("SET memory_limit='4GB'; SET threads=4; SET enable_progress_bar=false; SET TimeZone='UTC'")
        con.execute(f"SET temp_directory='{spill}'")
    return con
