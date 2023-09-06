run:
	python software_registry.py

style:
	black -S -l 79 .
	isort .
	flake8 .

migrate:
	python create_db.py
