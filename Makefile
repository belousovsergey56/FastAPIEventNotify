run:
	uvicorn src.main:app --port 5000 --reload
run_tuna:
	tuna http 5000
