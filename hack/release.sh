#!/bin/bash
set -o nounset
set -o errexit
set -o pipefail

REPO_ROOT=$(realpath "$(dirname "${BASH_SOURCE}")/..")
RELEASE_ROOT=${REPO_ROOT}/.cache/release

helm package ./helm/kube-copilot -d ${RELEASE_ROOT}

git clone git@github.com:feiskyer/kube-copilot.git -b gh-pages ${RELEASE_ROOT}/.pages
cd ${RELEASE_ROOT}/.pages
helm repo index ${RELEASE_ROOT}
helm repo index --merge index.yaml ${RELEASE_ROOT}
cp ${REPO_ROOT}/README.md .
cp ${RELEASE_ROOT}/*.tgz .
cp ${RELEASE_ROOT}/index.yaml .
git add .
git commit -am 'Update Helm releases'
git push origin gh-pages

# clean up
rm -rf ${RELEASE_ROOT}