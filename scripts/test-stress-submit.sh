#!/usr/bin/env bash

#set -ex

NB_HELLO=2
NB_POPUL=2
NB_ROOFI=2
NB_RECAS=5
NB_HTAUT=0 # FIXME
NB_BSMSE=5

user=1

cmd=echo  # dry run
cmd=      # do it!

cd ..

for i in $(seq 1 $NB_HELLO); do
  cd reana-demo-helloworld
  $cmd reana-client run -w hello-$user-ser -f ./reana.yaml
  user=$((user+1))
  $cmd reana-client run -w hello-$user-yad -f ./reana-yadage.yaml
  user=$((user+1))
  $cmd reana-client run -w hello-$user-cwl -f ./reana-cwl.yaml
  user=$((user+1))
  cd ..
done

for i in $(seq 1 $NB_POPUL); do
  cd reana-demo-worldpopulation
  $cmd reana-client run -w popul-$user-ser -f ./reana.yaml
  user=$((user+1))
  $cmd reana-client run -w popul-$user-yad -f ./reana-yadage.yaml
  user=$((user+1))
  $cmd reana-client run -w popul-$user-cwl -f ./reana-cwl.yaml
  user=$((user+1))
  cd ..
done

for i in $(seq 1 $NB_ROOFI); do
  cd reana-demo-root6-roofit
  $cmd reana-client run -w roofi-$user-ser -f ./reana.yaml
  user=$((user+1))
  $cmd reana-client run -w roofi-$user-yad -f ./reana-yadage.yaml
  user=$((user+1))
  $cmd reana-client run -w roofi-$user-cwl -f ./reana-cwl.yaml
  user=$((user+1))
  cd ..
done

for i in $(seq 1 $NB_RECAS); do
  cd reana-demo-atlas-recast
  $cmd reana-client run -w recas-$user-yad -f ./reana.yaml
  user=$((user+1))
  cd ..
done

for i in $(seq 1 $NB_BSMSE); do
  cd reana-demo-bsm-search
  $cmd reana-client run -w bsmse-$user-yad -f ./reana.yaml
  user=$((user+1))
  cd ..
done

cd reana
