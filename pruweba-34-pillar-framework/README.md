# Pruweba

A solo engineering practice building governed automation and open governance tooling.

## What is in this repo

### 34-pillar governance framework
- Python pillar implementations in `pillars/`
- Grouped by family: federation, truth, research, operations, intelligence, boundary, enterprise
- Each pillar exposes a `health_check()` contract
- Loader and registry in `__init__.py`

### Job pipeline
- `pipeline/scraper.py` — job ingestion from remote sources
- `pipeline/classify.py` — job classification
- `pipeline/generate.py` — output generation
- `pipeline/track.py` — tracking and logging
- Supporting utilities: cookie management, blocker handling, filtering, tiering, monitoring

### Research engine
- `research.py` plus `research/continuum.py`, `research/enterprise_value.py`, `research/trading.py`
- Continuum, enterprise value, and trading research modules

## Website
- https://pruweba.com

## Owner
- Jan Michael Acibron
- https://linkedin.com/in/jan-michael-acibron
- https://github.com/rankfixer-ai

## License
- MIT
