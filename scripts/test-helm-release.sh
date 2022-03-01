#!/usr/bin/env sh
BRANCH=master
RELEASEPYPI=0.9.0a1
RELEASEHELM=0.9.0-alpha.1
USER=john.doe@example.org
PASS=mysecretpassword
rm -rf /tmp/reana-$RELEASEPYPI
mkdir -p /tmp/reana-$RELEASEPYPI
cd /tmp/reana-$RELEASEPYPI || exit 1
rm -rf  ~/.virtualenvs/reana-$RELEASEPYPI
virtualenv ~/.virtualenvs/reana-$RELEASEPYPI
source ~/.virtualenvs/reana-$RELEASEPYPI/bin/activate
pip install reana-client==$RELEASEPYPI
git clone https://github.com/reanahub/reana-demo-helloworld --depth 1
kind delete cluster
wget https://raw.githubusercontent.com/reanahub/reana/$BRANCH/etc/kind-localhost-30443.yaml
kind create cluster --config kind-localhost-30443.yaml
wget https://raw.githubusercontent.com/reanahub/reana/$BRANCH/scripts/prefetch-images.sh
sh prefetch-images.sh
helm repo add reanahub https://reanahub.github.io/reana
helm repo update
helm install reana reanahub/reana --version $RELEASEHELM --namespace reana --create-namespace --wait
wget https://raw.githubusercontent.com/reanahub/reana/$BRANCH/scripts/create-admin-user.sh
sh create-admin-user.sh reana reana $USER $PASS
cd reana-demo-helloworld || exit 1
export REANA_SERVER_URL=https://localhost:30443
export REANA_ACCESS_TOKEN=$(kubectl -n reana get secret reana-admin-access-token -o json | jq -r '.data | map_values(@base64d) | .ADMIN_ACCESS_TOKEN')
reana-client run -w serial
reana-client run -w yadage -f ./reana-yadage.yaml
reana-client run -w cwl -f ./reana-cwl.yaml
reana-client run -w snakemake -f ./reana-snakemake.yaml
firefox $REANA_SERVER_URL
