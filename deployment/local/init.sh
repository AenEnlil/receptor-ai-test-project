
sleep 5s &&
python seeding.py &&
uvicorn app.main:app --host=0.0.0.0 --reload

