"""Bounded diagnostics transport with an allowlisted, secret-free output."""
import asyncio
import json
from datetime import datetime, timezone
from urllib.parse import urlsplit

import httpx

LIMITATIONS = ["Generowanie i walidacja danych nie są jeszcze zaimplementowane.",
               "Nie sprawdzono dostawcy ani modelu LLM; nie wykonuje się płatnych prób."]
MESSAGES = {
    "ok": "Sprawdzenie zakończyło się pomyślnie.",
    "configuration_unavailable": "Brak poprawnej konfiguracji.",
    "connection_failed": "Nie można połączyć się z bazą.",
    "invalid_privileges": "Konto lub schemat bazy ma niewłaściwe uprawnienia.",
    "lock_timeout": "Przekroczono czas oczekiwania na blokadę migracji.",
    "migration_failed": "Nie udało się zastosować migracji; wymagany restart serwisu.",
    "schema_version_missing": "Brak wymaganej wersji schematu bazy.",
    "configuration_missing": "Brak poprawnej konfiguracji bazy.",
    "permission_denied": "Brak dostępu do zasobu.",
    "missing_root": "Brak wymaganego zasobu.",
    "io_error": "Nie udało się sprawdzić lub usunąć pliku próbnego.",
    "invalid_resource": "Zasób jest nieprawidłowy.",
    "timeout": "Przekroczono czas diagnostyki serwisu.",
    "unreachable": "Nie można połączyć się z serwisem.",
    "http_error": "Serwis zwrócił nieprawidłowy status HTTP.",
    "invalid_report": "Serwis zwrócił nieprawidłowy raport.",
    "diagnostic_failed": "Diagnostyka nie powiodła się.",
}


def now():
    return datetime.now(timezone.utc).isoformat()


def check(name, code="ok", status=None):
    code = code if code in MESSAGES else "diagnostic_failed"
    return {"id": name, "status": status or ("ok" if code == "ok" else "failed"),
            "code": code, "message": MESSAGES[code], "limitations": []}


def capacity(checks):
    statuses = [item["status"] for item in checks if item["id"] != "process"]
    return "capable" if statuses and all(s == "ok" for s in statuses) else (
        "incapable" if not statuses or all(s != "ok" for s in statuses) else "partial")


def report(service, checks):
    return {"service": service, "scope": "foundation", "checked_at": now(),
            "capacity": capacity(checks), "checks": checks, "limitations": LIMITATIONS.copy()}


def valid_url(value):
    try:
        url = urlsplit(value)
        return (url.scheme in ("http", "https") and bool(url.hostname) and url.username is None
                and url.password is None and url.path in ("", "/") and not url.query and not url.fragment
                and not any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in value)
                and (url.port is None or 1 <= url.port <= 65535))
    except (ValueError, TypeError):
        return False


def clean_report(data, service):
    if not isinstance(data, dict) or data.get("service") != service or data.get("scope") != "foundation":
        raise ValueError
    timestamp = data.get("checked_at")
    if not isinstance(timestamp, str) or len(timestamp) > 40:
        raise ValueError
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if dt.utcoffset() is None or dt.utcoffset().total_seconds() != 0:
        raise ValueError
    if data.get("capacity") not in ("capable", "partial", "incapable"):
        raise ValueError
    checks = data.get("checks")
    if not isinstance(checks, list) or not 1 <= len(checks) <= 20:
        raise ValueError
    catalogs = {"application-api": {"process", "configuration", "database", "artifacts", "generation", "validation"},
                "generation-service": {"process", "configuration"},
                "validation-service": {"process", "configuration"}}
    allowed_ids = catalogs.get(service, set())
    ids = [item.get("id") if isinstance(item, dict) else None for item in checks]
    if len(ids) != len(allowed_ids) or set(ids) != allowed_ids:
        raise ValueError
    safe = []
    for item in checks:
        if not isinstance(item, dict) or item.get("id") not in allowed_ids or item.get("status") not in ("ok", "failed", "not_checked"):
            raise ValueError
        if item["id"] == "process" and (item["status"] != "ok" or item.get("code") != "ok"):
            raise ValueError
        if not isinstance(item.get("code"), str) or len(item["code"]) > 80:
            raise ValueError
        for key in ("message",):
            if not isinstance(item.get(key), str) or len(item[key]) > 500:
                raise ValueError
        limitations = item.get("limitations")
        if not isinstance(limitations, list) or len(limitations) > 20 or any(not isinstance(x, str) or len(x) > 500 for x in limitations):
            raise ValueError
        code = item["code"] if item["code"] in MESSAGES else "diagnostic_failed"
        if (item["status"] == "ok") != (code == "ok"):
            raise ValueError
        safe.append(check(item["id"], code, item["status"]))
    limitations = data.get("limitations")
    if not isinstance(limitations, list) or len(limitations) > 20 or any(not isinstance(x, str) or len(x) > 500 for x in limitations):
        raise ValueError
    if capacity(safe) != data["capacity"]:
        raise ValueError
    result = report(service, safe)
    result["checked_at"] = timestamp
    return result


async def probe(client, url, service, *, total_timeout=None):
    if not valid_url(url):
        return report(service, [check("configuration", "configuration_unavailable")])
    # The outer API needs more time than its own concurrent child probes.
    timeout = total_timeout if total_timeout is not None else (10 if service == "application-api" else 6)
    read_timeout = 10 if service == "application-api" else 5
    try:
        async with asyncio.timeout(timeout):
            async with client.stream("GET", url.rstrip("/") + "/health/ready",
                                     timeout=httpx.Timeout(read_timeout, connect=2)) as response:
                if response.status_code != 200:
                    return report(service, [check("configuration", "http_error")])
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > 65536:
                        raise ValueError
                return clean_report(json.loads(body), service)
    except (TimeoutError, httpx.TimeoutException):
        code = "timeout"
    except httpx.InvalidURL:
        code = "configuration_unavailable"
    except httpx.RequestError:
        code = "unreachable"
    except (ValueError, UnicodeError, TypeError, OverflowError, RecursionError):
        code = "invalid_report"
    except Exception:
        # Isolate unexpected failures without exposing exception contents.
        code = "diagnostic_failed"
    return report(service, [check("configuration", code)])
