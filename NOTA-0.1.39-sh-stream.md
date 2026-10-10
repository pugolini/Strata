# Strata v0.1.39 — regresión del stream de shared experts en gfx1201 (RDNA4)

## Veredicto

| Version | t/s mediana | Notas |
|---|---|---|
| v0.1.37 (baseline) | 61,18 | estable |
| v0.1.39 por defecto | 43,43 | REGRESION -29% |
| v0.1.39 + STRATA_SH_STREAM=0 | **65,57 – 66,92** | **+7,7% a +9,4% vs baseline** |

## Causa raiz

`src/core/verify.cpp:907` (v0.1.39):

    const bool sh_fork = sh_stream_env && !prof_on_ && sh_cs_ != nullptr && ev_fork_ != nullptr && ev_join_ != nullptr;

`STRATA_SH_STREAM` sin definir = ON. El fork del stream del shared expert (nuevo en 0.1.39,
commit 055122c "fix(cuda,decode): ... restore 100% bit-exactness") es una optimizacion CUDA
que en HIP/gfx1201 penaliza: el stream secundario serializa contra el principal en vez de
solapar. v0.1.37 NO tiene esta ruta.

Evidencia del porque: con `STRATA_VERIFY_PROFILE=1` (que fuerza `prof_on_=true` y por tanto
`sh_fork=false`) v0.1.39 ya rendia 60,40 t/s. El propio codigo de profiling desactiva la ruta
lenta.

## Desglose por ventana (STRATA_DECODE_TIMING, ms/ventana)

| Etapa | v0.1.37 | v0.1.39 | v0.1.39 + SH_STREAM=0 |
|---|---|---|---|
| GPU-reach wait | 21,18 | 31,06 | **20,26** |
| host per-layer | 1,40 | 0,73 | 0,79 |
| draft | 3,30 | 3,38 | 3,26 |
| commit/emit | 0,22 | 0,23 | 0,10 |
| **total/window** | 28,23 | 38,57 | **26,03** |

La perdida era enteramente tiempo de GPU en el verify.

## Lo que SI mejora v0.1.39 (motivo para adoptarla)

- **KV streaming: 99,90% de hits en VRAM** (815.340 lecturas de bloque), 3,4 MiB desde RAM.
- **resident RAM: 18,07 GiB de expertos en RAM, 0 blob reads del fichero** (v0.1.37 hacia 85.658 blob reads).
- Arranque y `--vram-elastic`, `--peer-device`, `--batch/--slots`, `--reorder`, ajuste de effort sin releer prompt.

## Configuracion aplicada

`/models/Strata/strata-262k.json` → `env: {"STRATA_RESIDENT_PIN":"0", "STRATA_SH_STREAM":"0"}`

## Rollback

    cd /models/Strata && git reset --hard snapshot-20261004T163500Z
    cp engine/strata.v0.1.37 engine/strata && /models/Strata/start-262k.sh
