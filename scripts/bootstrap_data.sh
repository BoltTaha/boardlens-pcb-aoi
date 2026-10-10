#!/usr/bin/env bash
set -euo pipefail
mkdir -p data/raw third_party
curl -L --fail --continue-at - -o data/raw/VisA_20220922.tar \
  https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar
test "$(stat -c %s data/raw/VisA_20220922.tar)" = "1929840640"
tar -xf data/raw/VisA_20220922.tar -C data/raw
if [ ! -d third_party/visa_dataset/.git ]; then
  git clone --depth 1 https://github.com/wxs56837/visa_dataset third_party/visa_dataset
fi
python3 -m ml.datasets.validate_visa data/raw/VisA
python3 -m ml.datasets.prepare_visa --source data/raw/VisA

