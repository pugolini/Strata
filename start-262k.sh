#!/bin/bash
# HELIOS 262K: contexto nativo completo (el modelo esta entrenado para 262144).
# Memoria medida previamente: expertos 18.50 GiB pageable + KV 3.09 GiB pinned
# = 21.59 GiB, contra el limite de 26624 MiB del contenedor 200.
set -euo pipefail
cd /models/Strata
V=/models/Strata/.venv/lib/python3.12/site-packages
export LD_LIBRARY_PATH="$V/_rocm_sdk_devel/lib:$V/_rocm_sdk_libraries_gfx120X_all/lib:${LD_LIBRARY_PATH:-}"
export HSA_OVERRIDE_GFX_VERSION=12.0.1
export STRATA_RESIDENT_PIN=0
export PATH=/opt/rocm/bin:$PATH

exec /models/Strata/.venv/bin/python /models/Strata/serve/server.py \
  --engine strata \
  --config /models/Strata/strata-262k.json \
  --port 8080
