__VERSION__ = "0.0.8"

bump:
	bump2version --allow-dirty --current-version $(__VERSION__) patch Makefile custom_components/miele/const.py custom_components/miele/manifest.json

lint:
	isort custom_components
	black custom_components
	flake8 custom_components

install_dev:
	pip install -r requirements-dev.txt
