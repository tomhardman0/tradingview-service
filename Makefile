dev:
	cd server && uvicorn main:app --reload

prod:
	cd server && uvicorn main:app --host 0.0.0.0 --port 8080