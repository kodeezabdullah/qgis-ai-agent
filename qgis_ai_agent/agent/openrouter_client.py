import json
import time

import requests


FALLBACK_MODELS = [
    "moonshotai/kimi-k2.6:free",
    "openai/gpt-oss-120b:free",
    "openai/gpt-oss-20b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
]

RATE_LIMIT_WAIT_SECONDS = 30
MAX_FULL_CYCLES = 3


def _short_name(model_id):
    return model_id.split("/", 1)[-1].split(":", 1)[0]


class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key, model=None, status_callback=None):
        self.api_key = api_key
        primary = model or FALLBACK_MODELS[0]
        chain = [primary] + [m for m in FALLBACK_MODELS if m != primary]
        self.models = chain
        self.model = primary
        self.current_index = 0
        self.last_status = ""
        self._status_callback = status_callback

    def set_status_callback(self, callback):
        self._status_callback = callback

    def _emit_status(self, text):
        self.last_status = text
        print(f"[OpenRouterClient] {text}")
        if self._status_callback:
            try:
                self._status_callback(text)
            except Exception:
                pass

    def _post(self, messages, tools, model_id):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": model_id, "messages": messages}
        if tools:
            payload["tools"] = tools
        return requests.post(
            self.BASE_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=60,
        )

    def _request_with_fallback(self, messages, tools):
        for cycle in range(MAX_FULL_CYCLES):
            for idx, model_id in enumerate(self.models):
                self.current_index = idx
                self.model = model_id
                self._emit_status(f"Using: {_short_name(model_id)}")
                try:
                    response = self._post(messages, tools, model_id)
                    if response.status_code == 429:
                        next_idx = idx + 1
                        if next_idx < len(self.models):
                            self._emit_status(
                                f"Rate limited, switching to {_short_name(self.models[next_idx])}..."
                            )
                        continue
                    response.raise_for_status()
                    return {"ok": True, "data": response.json(), "model": model_id}
                except requests.exceptions.HTTPError as e:
                    return {
                        "ok": False,
                        "error": f"HTTP {e.response.status_code}: {e.response.text}",
                        "model": model_id,
                    }
                except requests.exceptions.RequestException as e:
                    return {"ok": False, "error": f"Request failed: {e}", "model": model_id}

            self._emit_status(
                f"All models rate limited. Waiting {RATE_LIMIT_WAIT_SECONDS}s before retry..."
            )
            time.sleep(RATE_LIMIT_WAIT_SECONDS)

        return {"ok": False, "error": "All models rate limited after multiple retries"}

    def chat(self, messages, tools=None):
        result = self._request_with_fallback(messages, tools)
        if not result["ok"]:
            return f"[API error] {result['error']}"
        try:
            return result["data"]["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as e:
            return f"[API error] Unexpected response format: {e}"

    def complete(self, messages, tools=None):
        result = self._request_with_fallback(messages, tools)
        if not result["ok"]:
            return {"error": result["error"]}
        try:
            return {"message": result["data"]["choices"][0]["message"], "model": result["model"]}
        except (KeyError, IndexError, ValueError) as e:
            return {"error": f"Unexpected response format: {e}"}
