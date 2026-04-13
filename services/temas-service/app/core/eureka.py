from __future__ import annotations

from typing import Any

import py_eureka_client.eureka_client as eureka_client

from app.core.config import get_settings


async def register_with_eureka() -> Any:
    settings = get_settings()
    if not settings.eureka_enabled:
        return None

    await eureka_client.init_async(
        eureka_server=settings.eureka_server_url,
        app_name=settings.service_name,
        instance_port=settings.service_port,
        instance_host=settings.eureka_instance_host,
        instance_ip=settings.eureka_instance_ip,
        health_check_url=f"http://{settings.eureka_instance_host}:{settings.service_port}/health",
        home_page_url=f"http://{settings.eureka_instance_host}:{settings.service_port}/",
    )
    return eureka_client


async def stop_eureka_client() -> None:
    settings = get_settings()
    if settings.eureka_enabled:
        await eureka_client.stop_async()
