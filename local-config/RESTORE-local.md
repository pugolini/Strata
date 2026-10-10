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
