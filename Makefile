.PHONY: discover-data update-structured-surveys update-recent-occurrences update-ocean-nowcast update-ocean-forecast validate-data build-evidence-catalog rank-species project-status

discover-data:
	python3 scripts/acquisition/discover_latest_survey_data.py

update-structured-surveys:
	python3 scripts/acquisition/download_ncrmp_regions.py

update-recent-occurrences:
	python3 scripts/acquisition/download_obis_recent.py

update-ocean-nowcast:
	python3 scripts/acquisition/update_current_ocean_data.py

update-ocean-forecast:
	python3 scripts/acquisition/update_ocean_forecast.py

validate-data:
	python3 scripts/validation/validate_noaa_rvc.py

build-evidence-catalog:
	python3 scripts/preprocessing/build_evidence_catalog.py

rank-species:
	python3 scripts/modeling/rank_regional_readiness.py

project-status:
	python3 scripts/project_status.py
