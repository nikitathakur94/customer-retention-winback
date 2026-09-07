"""Explicit, resumable local commands with measured execution logs."""
import argparse,subprocess,sys,time,resource
from .common import ROOT,run_dir,save,now

def dbt(mode):
    import os
    env=os.environ.copy(); env['RETENTION_DB']=str(ROOT/'warehouse'/f'{mode}.duckdb')
    subprocess.run([str(ROOT/'.venv/bin/dbt'),'build','--project-dir',str(ROOT/'dbt'),'--profiles-dir',str(ROOT/'dbt')],env=env,check=True)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('step',choices=['doctor','download','profile','build','dbt','train','evaluate','score','cohorts','hillstrom','reports','trace','presentation','reproduce']); parser.add_argument('--mode',choices=['dev','full'],default='dev'); args=parser.parse_args()
    from .ingest import doctor,download
    from .profiling import profile
    from .snapshots import build
    from .modeling import train,evaluate
    from .scoring import score
    from .experiments import dry_run
    from .hillstrom import analyze
    from .reporting import reports,trace,presentation
    steps={'doctor':lambda:doctor(),'download':lambda:download(),'profile':lambda:profile(args.mode),'build':lambda:build(args.mode),'dbt':lambda:dbt(args.mode),'train':lambda:train(args.mode),'evaluate':lambda:evaluate(args.mode),'score':lambda:score(args.mode),'cohorts':lambda:dry_run(args.mode),'hillstrom':lambda:analyze(args.mode),'reports':lambda:reports(args.mode),'trace':lambda:trace(args.mode),'presentation':lambda:presentation(args.mode)}
    selected=list(steps) if args.step=='reproduce' else [args.step]
    for step in selected:
        p=run_dir(args.mode); started=time.perf_counter(); print('START',step,flush=True)
        if args.step=='reproduce' and step=='train' and (p/'freeze.json').exists(): print('Using already frozen models'); continue
        try: steps[step](); status='passed'
        except Exception as exc:
            save(p/'execution'/f'{step}.json',{'status':'failed','error':str(exc),'time':now(),'seconds':time.perf_counter()-started}); raise
        save(p/'execution'/f'{step}.json',{'status':status,'time':now(),'seconds':time.perf_counter()-started,'peak_rss_bytes_macos':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        print('DONE',step,flush=True)
if __name__=='__main__': main()
