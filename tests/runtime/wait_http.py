#!/usr/bin/env python3
from __future__ import annotations

import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def wait_http(url: str, timeout: int) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=5) as response:
                if response.status < 500:
                    return
        except HTTPError as error:
            if error.code < 500:
                return
            last_error = error
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
        time.sleep(1)
    raise SystemExit(f"Timed out waiting for {url}: {last_error}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: wait_http.py URL TIMEOUT_SECONDS")
    wait_http(sys.argv[1], int(sys.argv[2]))
