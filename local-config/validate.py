#!/usr/bin/env python3
"""Helios API validation: OpenAI (plain + SSE), Anthropic (plain + SSE). Exit 1 on any failure."""
import json, sys, urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"
Q = "Responde solo con la palabra: hola"
fails = []


def post(path, body, headers=None):
    h = {"Content-Type": "application/json", **(headers or {})}
    return urllib.request.urlopen(urllib.request.Request(BASE + path, json.dumps(body).encode(), h), timeout=300)


def sse(resp):
    for raw in resp:
        line = raw.decode("utf-8", "replace").strip()
        if line.startswith("data:"):
            data = line[5:].strip()
            if data and data != "[DONE]":
                yield json.loads(data)


def check(name, content, reasoning):
    ok = bool(content.strip()) and not reasoning.strip()
    print(f"{'OK  ' if ok else 'FAIL'} {name:22s} content={content.strip()[:40]!r} reasoning_len={len(reasoning)}")
    if not ok:
        fails.append(name)


A_HDR = {"x-api-key": "x", "anthropic-version": "2023-06-01"}
oa = {"model": "helios-262k", "messages": [{"role": "user", "content": Q}], "max_tokens": 40, "temperature": 0}
an = {"model": "helios-262k", "messages": [{"role": "user", "content": Q}], "max_tokens": 40}

m = json.load(post("/v1/chat/completions", oa))["choices"][0]["message"]
check("openai", m.get("content") or "", m.get("reasoning_content") or "")

c = r = ""
for ev in sse(post("/v1/chat/completions", {**oa, "stream": True})):
    d = (ev.get("choices") or [{}])[0].get("delta", {})
    c += d.get("content") or ""
    r += d.get("reasoning_content") or ""
check("openai stream", c, r)

j = json.load(post("/v1/messages", an, A_HDR))
check("anthropic", "".join(b.get("text", "") for b in j["content"] if b["type"] == "text"),
      "".join(b.get("thinking", "") for b in j["content"] if b["type"] == "thinking"))

c = r = ""
for ev in sse(post("/v1/messages", {**an, "stream": True}, A_HDR)):
    d = ev.get("delta") or {}
    c += d.get("text") or ""
    r += d.get("thinking") or ""
check("anthropic stream", c, r)

# thinking explicitly requested must still work (goes to reasoning, not lost)
m = json.load(post("/v1/chat/completions", {**oa, "max_tokens": 300, "chat_template_kwargs": {"enable_thinking": True}}))["choices"][0]["message"]
ok = bool((m.get("reasoning_content") or "").strip())
print(f"{'OK  ' if ok else 'FAIL'} {'openai thinking=on':22s} reasoning_len={len(m.get('reasoning_content') or '')} content={(m.get('content') or '')[:30]!r}")
if not ok:
    fails.append("thinking on")

print("VALIDATION", "FAILED: " + ", ".join(fails) if fails else "PASSED")
sys.exit(1 if fails else 0)
