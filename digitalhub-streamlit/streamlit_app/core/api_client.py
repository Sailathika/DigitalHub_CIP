"""
Thin HTTP client for the DigitalHub_CIP FastAPI backend.

Every function here mirrors what the original React app's httpClient.js did:
attach the bearer token from session state, raise a consistent ApiError with
the backend's `detail` message, and keep endpoint calls in one place.
"""
import os
from typing import Optional

import requests
import streamlit as st

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")
TIMEOUT = 30


class ApiError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _auth_headers() -> dict:
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _handle_response(response: requests.Response):
    if response.status_code == 204:
        return None
    content_type = response.headers.get("content-type", "")
    payload = response.json() if "application/json" in content_type else response.text

    if not response.ok:
        detail = payload.get("detail") if isinstance(payload, dict) else payload
        raise ApiError(detail or f"Request failed with status {response.status_code}", response.status_code)
    return payload


def get(path: str, params: Optional[dict] = None):
    try:
        response = requests.get(f"{BASE_URL}{path}", headers=_auth_headers(), params=params, timeout=TIMEOUT)
    except requests.exceptions.RequestException as exc:
        raise ApiError(f"Could not reach the backend at {BASE_URL}. Is it running? ({exc})") from exc
    return _handle_response(response)


def post(path: str, json: Optional[dict] = None):
    try:
        response = requests.post(f"{BASE_URL}{path}", headers=_auth_headers(), json=json or {}, timeout=TIMEOUT)
    except requests.exceptions.RequestException as exc:
        raise ApiError(f"Could not reach the backend at {BASE_URL}. Is it running? ({exc})") from exc
    return _handle_response(response)


def put(path: str, json: Optional[dict] = None):
    try:
        response = requests.put(f"{BASE_URL}{path}", headers=_auth_headers(), json=json or {}, timeout=TIMEOUT)
    except requests.exceptions.RequestException as exc:
        raise ApiError(f"Could not reach the backend at {BASE_URL}. Is it running? ({exc})") from exc
    return _handle_response(response)


def patch(path: str, json: Optional[dict] = None):
    try:
        response = requests.patch(f"{BASE_URL}{path}", headers=_auth_headers(), json=json or {}, timeout=TIMEOUT)
    except requests.exceptions.RequestException as exc:
        raise ApiError(f"Could not reach the backend at {BASE_URL}. Is it running? ({exc})") from exc
    return _handle_response(response)


def delete(path: str):
    try:
        response = requests.delete(f"{BASE_URL}{path}", headers=_auth_headers(), timeout=TIMEOUT)
    except requests.exceptions.RequestException as exc:
        raise ApiError(f"Could not reach the backend at {BASE_URL}. Is it running? ({exc})") from exc
    return _handle_response(response)


def post_form(path: str, data: Optional[dict] = None, files: Optional[dict] = None):
    """Multipart POST — used for dataset upload and product create/update with an image."""
    try:
        response = requests.post(
            f"{BASE_URL}{path}", headers=_auth_headers(), data=data or {}, files=files, timeout=TIMEOUT
        )
    except requests.exceptions.RequestException as exc:
        raise ApiError(f"Could not reach the backend at {BASE_URL}. Is it running? ({exc})") from exc
    return _handle_response(response)


def put_form(path: str, data: Optional[dict] = None, files: Optional[dict] = None):
    try:
        response = requests.put(
            f"{BASE_URL}{path}", headers=_auth_headers(), data=data or {}, files=files, timeout=TIMEOUT
        )
    except requests.exceptions.RequestException as exc:
        raise ApiError(f"Could not reach the backend at {BASE_URL}. Is it running? ({exc})") from exc
    return _handle_response(response)


def get_file(path: str) -> requests.Response:
    """For file downloads (PDF/CSV reports) — returns the raw response so the
    caller can pull .content and headers for st.download_button."""
    try:
        response = requests.get(f"{BASE_URL}{path}", headers=_auth_headers(), timeout=TIMEOUT)
    except requests.exceptions.RequestException as exc:
        raise ApiError(f"Could not reach the backend at {BASE_URL}. Is it running? ({exc})") from exc
    if not response.ok:
        raise ApiError(f"Could not download file (status {response.status_code})", response.status_code)
    return response


def static_url(relative_path: Optional[str]) -> Optional[str]:
    """Resolve a backend-relative static asset path (e.g. product images)
    to an absolute URL, mirroring resolveStaticUrl() in the original app."""
    if not relative_path:
        return None
    if relative_path.startswith("http://") or relative_path.startswith("https://"):
        return relative_path
    origin = BASE_URL.split("/api/")[0]
    return f"{origin}{relative_path}"
