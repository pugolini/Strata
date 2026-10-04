import re

path = '/models/Strata/serve/server.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if with_shared properly forces enable_thinking=False when reasoning_effort is none
old_func = '''    def with_shared(self, req: dict, api: str) -> dict:
        The request with the shared thinking level and max tokens filled in where it has none of its own.
        s = self.shared
        if not s:
            return req
        req = dict(req)
        if max_tokens in s and not req.get(max_tokens) and not req.get(max_completion_tokens):
            req[max_tokens] = s[max_tokens]
        effort = s.get(reasoning_effort)
        if not req.get(reasoning_effort) and not req.get(reasoning):
            req[reasoning_effort] = effort or none
        if effort:
            if api == openai:
                ctk = req.get(chat_template_kwargs) if isinstance(req.get(chat_template_kwargs), dict) else {}
                if not req.get(reasoning_effort) and not req.get(reasoning) and \
                        enable_thinking not in ctk and reasoning_effort not in ctk:
                    req[reasoning_effort] = effort
            elif not req.get(thinking) and not req.get(output_config):
                if effort == none:
                    req[thinking] = {type: disabled}
                else:
                    req[output_config] = {effort: effort}
        return req'''

new_func = '''    def with_shared(self, req: dict, api: str) -> dict:
        The request with the shared thinking level and max tokens filled in where it has none of its own.
        s = self.shared
        if not s:
            return req
        req = dict(req)
        if max_tokens in s and not req.get(max_tokens) and not req.get(max_completion_tokens):
            req[max_tokens] = s[max_tokens]
        effort = s.get(reasoning_effort)
        if effort:
            if api == openai:
                ctk = req.get(chat_template_kwargs) if isinstance(req.get(chat_template_kwargs), dict) else {}
                if not req.get(reasoning_effort) and not req.get(reasoning) and \
                        enable_thinking not in ctk and reasoning_effort not in ctk:
                    if effort == none:
                        req[chat_template_kwargs] = {**ctk, enable_thinking: False}
                    else:
                        req[reasoning_effort] = effort
            elif not req.get(thinking) and not req.get(output_config):
                if effort == none:
                    req[thinking] = {type: disabled}
                else:
                    req[output_config] = {effort: effort}
        return req'''

if old_func in content:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.replace(old_func, new_func))
    print(PATCHED server.py successfully)
else:
    print(WARNING: exact match not found for with_shared)
