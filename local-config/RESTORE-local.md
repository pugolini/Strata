# Como recuperar la config local de Helios tras un update.sh de Strata

## 1. Restaurar los configs de servidor (estan en .gitignore: /strata-*.json)
cp local-config/strata-262k.json  /models/Strata/strata-262k.json
cp local-config/strata-iq3_xxs.json /models/Strata/strata-iq3_xxs.json

## 2. Re-aplicar el parche del chat_template (thinking OFF por defecto)
git apply local-config/parche-chat-template-thinking-off.patch
# (o copiar directamente: cp local-config/chat_template.jinja.thinking-off serve/chat_template.jinja)

## 3. Restaurar la unit systemd (apuntaba a un config obsoleto)
cp local-config/helios-server.service /etc/systemd/system/helios-server.service
systemctl daemon-reload && systemctl restart helios-server.service

## 4. Si el arbol git se perdio del todo, recuperar la rama desde el bundle
git clone -b local-helios local-config/bundles/local-helios-*.bundle /models/Strata-restaurado

## Comprobacion de que todo esta bien
curl -s http://127.0.0.1:8080/health
tail -30 /models/Strata/strata-262k.log | grep -E "lendable|WARNING"
# Debe decir: 2269 of the prompt path's 2269 lendable slots keep their experts in RAM too
# y NINGUN WARNING. Si sale "278 of 2269", falta STRATA_RESIDENT_HEADROOM_GIB=2.

## 0.1.44.1 (2026-10-16)
- Rama `local-helios-0144` (base upstream 296b59d2): plantilla thinking-off, config local y el router agrupado (commits del PR `pr-route-window`).
- `strata-262k.json`: `STRATA_HC_Q8=0` (0.1.44 lo activa por defecto en gfx12 y cambia la salida), `"reasoning_effort": "none"` en el propio JSON (#1641), `STRATA_TSUM=1`, `STRATA_ROUTE_WIN=1`, `--mtp-draft-vocab data/draft_vocab_en.bin --mtp-q4 head`.
- Compilar: `HIP_PLATFORM=amd` y `-DHIP_PLATFORM=amd` (hipconfig --platform vacio en este entorno).
- Canarios al arrancar: no debe salir "hyper-connection projections are read as Q8_0"; VRAM libre ~1190 MiB; "thinking level: none".
- Validar: `python3 local-config/validate.py` (OpenAI y Anthropic, con y sin stream).
- Volver a 0.1.41: ver /models/Strata-backup-0141-*/ (serve/, strata, strata-262k.json) y `git checkout local-helios`.
