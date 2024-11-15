# make run ARGS='execute "find all kube-dns pods"'

.PHONY: run
run:
	poetry run kube-copilot $(ARGS)

.PHONY: web
web:
	streamlit run web/Home.py

.PHONY: build
build:
	poetry build

.PHONY: install
install: build
	pip install --force-reinstall --no-deps dist/$(shell ls -t dist | head -n 1)

.PHONY: versioning
versioning:
	yq -i ".image.tag = \"v$(shell poetry version -s)\"" ./helm/kube-copilot/values.yaml
	yq -i ".version = \"$(shell poetry version -s)\"" ./helm/kube-copilot/Chart.yaml
	yq -i ".appVersion = \"$(shell poetry version -s)\"" ./helm/kube-copilot/Chart.yaml

.PHONY: publish
publish: build
	poetry publish
	# gh release create v$(shell poetry version -s)

.PHONY: update
update:
	poetry up
	poetry update

.PHONY: release-helm
release-helm:
	hack/release.sh

.PHONY: release
release: versioning publish release-helm

.PHONY: clean
clean:
	rm -rf dist

.PHONY: install-dev
install-dev:
	poetry install

.PHONY: install-poetry
install-poetry:
	# curl -sSL https://install.python-poetry.org | python3 -
	# brew install pipx && pipx ensurepath
	pipx install poetry
	poetry self add poetry-plugin-up
