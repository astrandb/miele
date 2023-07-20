src_dir := custom_components/miele

bump:
	bump2version --allow-dirty patch $(src_dir)/const.py $(src_dir)/manifest.json

bump_minor:
	bump2version --allow-dirty minor $(src_dir)/const.py $(src_dir)/manifest.json

bump_major:
	bump2version --allow-dirty major $(src_dir)/const.py $(src_dir)/manifest.json

# lint:
# 	isort $(src_dir)
# 	black $(src_dir)
# 	flake8 $(src_dir)

# .venv:
# 	python3.10 -m venv .venv

# install_dev: | .venv
# 	(. .venv/bin/activate; \
# 	pip install -Ur requirements-dev.txt )

# clean:
# 	rm -rf .venv $(src_dir)/__pycache__
