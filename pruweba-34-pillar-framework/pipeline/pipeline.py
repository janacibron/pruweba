import subprocess, time, os, sys

PYTHON = r'C:\Users\Jan\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
SCRAPER_DIR = r'C:\Users\Jan\Documents\AOP\olj_scraper'

def run_cmd(args):
    print('\n[STEP] ' + ' '.join(args))
    result = subprocess.run(
        [PYTHON] + args,
        capture_output=True, text=True, encoding='utf-8', errors='ignore',
        cwd=SCRAPER_DIR, timeout=600
    )
    if result.stdout:
        print(result.stdout[-300:])
    if result.returncode != 0:
        print('[ERR] Failed: ' + str(result.stderr[-200:]))
    return result.returncode == 0

def run_cycle():
    print('='*60)
    print('PIPELINE CYCLE START')
    print('='*60)
    ok = True
    ok = run_cmd(['scraper.py', 'automation', '3']) and ok
    ok = run_cmd(['rank_jobs.py']) and ok
    ok = run_cmd(['fetch_jobs.py']) and ok
    ok = run_cmd(['classify.py']) and ok
    ok = run_cmd(['generate.py']) and ok
    ok = run_cmd(['track.py']) and ok
    print('='*60)
    print('PIPELINE CYCLE ' + ('PASS' if ok else 'PARTIAL'))
    print('='*60)
    return ok

if __name__ == '__main__':
    if '--once' in sys.argv:
        run_cycle()
    else:
        while True:
            run_cycle()
            time.sleep(1800)
