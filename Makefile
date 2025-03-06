all:

pip:
	pip install -r requirements.txt

export-pip:
	poetry export --without-hashes --format=requirements.txt --with=dev | sort > requirements.txt 

create-venv:
	python -n virtualenv .venv
