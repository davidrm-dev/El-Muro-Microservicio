from __future__ import annotations

from typing import Any

import requests

from app.core.config import get_settings


class ServiceDiscoveryError(RuntimeError):
    pass


def discover_service_url(service_name: str, timeout: float = 5.0) -> str:
    settings = get_settings()
    app_name = service_name.upper()
    eureka_base = settings.eureka_server_url.rstrip("/")

    response = requests.get(
        f"{eureka_base}/apps/{app_name}",
        headers={"Accept": "application/json"},
        timeout=timeout,
    )
    response.raise_for_status()

    payload = response.json()
    application: dict[str, Any] | None = payload.get("application")
    if not application:
        raise ServiceDiscoveryError(f"Service {service_name} not found in Eureka")

    instances = application.get("instance")
    if isinstance(instances, dict):
        instances = [instances]
    if not isinstance(instances, list) or not instances:
        raise ServiceDiscoveryError(f"Service {service_name} has no instances in Eureka")

    up_instance = next((item for item in instances if item.get("status") == "UP"), None)
    instance = up_instance or instances[0]

    host = instance.get("ipAddr") or instance.get("hostName")
    port_info = instance.get("port") or {}
    if isinstance(port_info, dict):
        port = port_info.get("$")
    else:
        port = port_info

    if not host or port is None:
        raise ServiceDiscoveryError(f"Service {service_name} has invalid Eureka metadata")

    return f"http://{host}:{int(port)}"
