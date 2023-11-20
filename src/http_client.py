import httpx

def no_proxy():
    return httpx.AsyncClient(proxies={})