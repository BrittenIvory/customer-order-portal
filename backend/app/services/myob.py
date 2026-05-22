import asyncio
import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

MYOB_TIMEOUT = 30.0


class MYOBClient:
    """Client for MYOB Advanced (Acumatica) contract-based REST API."""

    def __init__(self) -> None:
        self.base_url = settings.MYOB_BASE_URL.rstrip("/")
        self.api_endpoint = f"{self.base_url}/entity/Default/24.200.001"
        self.client = httpx.AsyncClient(timeout=MYOB_TIMEOUT)
        self._cookies: httpx.Cookies | None = None
        self._login_lock = asyncio.Lock()

    async def _ensure_logged_in(self) -> None:
        if self._cookies:
            return
        async with self._login_lock:
            if self._cookies:
                return
            await self._do_login()

    async def _do_login(self) -> None:
        url = f"{self.base_url}/entity/auth/login"
        payload = {
            "name": settings.MYOB_USERNAME,
            "password": settings.MYOB_PASSWORD,
            "company": settings.MYOB_COMPANY,
        }
        if settings.MYOB_BRANCH:
            payload["branch"] = settings.MYOB_BRANCH
        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        self._cookies = resp.cookies
        logger.info("Logged in to MYOB Advanced")

    async def _relogin_and_retry(
        self, url: str, params: dict[str, str] | None
    ) -> httpx.Response:
        async with self._login_lock:
            self._cookies = None
            await self._do_login()
        return await self.client.get(url, params=params, cookies=self._cookies)

    async def logout(self) -> None:
        url = f"{self.base_url}/entity/auth/logout"
        await self.client.post(url, cookies=self._cookies)
        self._cookies = None

    async def _get(
        self, entity: str, params: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        await self._ensure_logged_in()
        url = f"{self.api_endpoint}/{entity}"
        resp = await self.client.get(url, params=params, cookies=self._cookies)
        if resp.status_code == 401:
            resp = await self._relogin_and_retry(url, params)
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else [data]

    async def _get_single(
        self, entity: str, key: str
    ) -> dict[str, Any] | None:
        await self._ensure_logged_in()
        url = f"{self.api_endpoint}/{entity}/{key}"
        resp = await self.client.get(url, cookies=self._cookies)
        if resp.status_code == 401:
            resp = await self._relogin_and_retry(url, None)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def get_sales_orders(
        self, customer_id: str | None = None
    ) -> list[dict[str, Any]]:
        params: dict[str, str] = {"$expand": "Details"}
        if customer_id:
            params["$filter"] = f"CustomerID eq '{customer_id}'"
        return await self._get("SalesOrder", params)

    async def get_sales_order(self, order_nbr: str) -> dict[str, Any] | None:
        await self._ensure_logged_in()
        params = {"$expand": "Details"}
        url = f"{self.api_endpoint}/SalesOrder/SO/{order_nbr}"
        resp = await self.client.get(url, params=params, cookies=self._cookies)
        if resp.status_code == 401:
            resp = await self._relogin_and_retry(url, params)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def get_purchase_orders(
        self, vendor_ref: str | None = None
    ) -> list[dict[str, Any]]:
        params: dict[str, str] = {"$expand": "Details"}
        if vendor_ref:
            params["$filter"] = f"VendorRef eq '{vendor_ref}'"
        return await self._get("PurchaseOrder", params)

    async def get_purchase_order(
        self, order_nbr: str
    ) -> dict[str, Any] | None:
        await self._ensure_logged_in()
        params = {"$expand": "Details"}
        url = f"{self.api_endpoint}/PurchaseOrder/PO/{order_nbr}"
        resp = await self.client.get(url, params=params, cookies=self._cookies)
        if resp.status_code == 401:
            resp = await self._relogin_and_retry(url, params)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def get_purchase_receipts(
        self,
    ) -> list[dict[str, Any]]:
        params: dict[str, str] = {"$expand": "Details"}
        return await self._get("PurchaseReceipt", params)

    async def get_invoices(
        self, customer_id: str | None = None
    ) -> list[dict[str, Any]]:
        params: dict[str, str] = {"$expand": "Details"}
        if customer_id:
            params["$filter"] = f"CustomerID eq '{customer_id}'"
        return await self._get("Invoice", params)


myob_client = MYOBClient()
