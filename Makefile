.PHONY: setup all staging verified validate api export training test verify fetch serve site clean
PY ?= python3

setup:
	$(PY) -m pip install -r requirements.txt

# Public dataset = verified/ (strict mode). `staging` is the internal build that still contains unverified/estimated values and is never served.
all: staging verified validate api export training     ## full pipeline (no network needed)

staging:
	$(PY) tools/build.py
	$(PY) tools/make_schemas.py
	$(PY) tools/validate.py

verified:
	$(PY) tools/make_verified.py

validate:
	$(PY) tools/validate_verified.py

api:
	$(PY) tools/make_api.py

export:
	$(PY) tools/export_data.py

training:                                            ## ML-ready files in training/
	$(PY) tools/make_training.py
	$(PY) tools/validate_training.py
	$(PY) tools/make_trajectories.py
	$(PY) tools/validate_trajectories.py
	$(PY) tools/make_design_dataset.py
	$(PY) tools/validate_design.py

test: validate                                       ## backend smoke test (16 endpoint checks)
	$(PY) tools/smoke_test.py

fetch:                                               ## re-download source pages (needs network access to JPL/NASA/ULA/ESA hosts)
	bash tools/fetch_sources.sh

verify:                                              ## re-run verification on cached pages, then rebuild everything
	$(PY) -I tools/verify_celestial.py
	$(PY) -I tools/verify_launch.py
	$(MAKE) all

serve:                                               ## local backend on :8000
	$(PY) tools/serve_api.py

site:                                                ## static site + API on :8001
	cd docs && $(PY) -m http.server 8001

clean:
	find . -name __pycache__ -not -path "./.git/*" -exec rm -rf {} +
