.PHONY: setup all build schemas validate api export reports bench test verify fetch serve site clean
PY ?= python3

setup:
	$(PY) -m pip install -r requirements.txt

all: build schemas validate api export reports   ## full pipeline (no network needed)

build:
	$(PY) tools/build.py
schemas:
	$(PY) tools/make_schemas.py
validate:
	$(PY) tools/validate.py
api:
	$(PY) tools/make_api.py
export:
	$(PY) tools/export_data.py
reports:
	$(PY) tools/make_reports.py
bench:
	$(PY) tools/benchmark.py

test: validate                                       ## parity (JS vs Python), Monte Carlo cross-check, backend smoke test
	node tools/parity_check.js
	node tools/sim_check.js
	$(PY) tools/smoke_test.py

fetch:                                               ## re-download source pages (needs network access to JPL/NASA/ULA/ESA)
	bash tools/fetch_sources.sh

verify:                                              ## re-run verification on cached pages, then rebuild
	$(PY) -I tools/verify_celestial.py
	$(PY) -I tools/verify_launch.py
	$(MAKE) all

serve:                                               ## local backend on :8000
	$(PY) tools/serve_api.py

site:                                                ## static site + API on :8001
	cd docs && $(PY) -m http.server 8001

clean:
	find . -name __pycache__ -not -path "./.git/*" -exec rm -rf {} +
