import ipaddress

from django.conf import settings


def get_client_ip(request):
    """
    Return the client IP address for security auditing.

    By default, only REMOTE_ADDR is trusted.
    X-Forwarded-For is trusted only when REMOTE_ADDR
    belongs to an explicitly configured trusted proxy.
    """

    if not request:
        return None

    remote_addr = request.META.get("REMOTE_ADDR")

    if not remote_addr:
        return None

    trusted_proxy_ips = getattr(
        settings,
        "TRUSTED_PROXY_IPS",
        [],
    )

    try:
        remote_ip = ipaddress.ip_address(remote_addr)
    except ValueError:
        return remote_addr

    is_trusted_proxy = False

    for trusted_proxy in trusted_proxy_ips:
        try:
            if remote_ip in ipaddress.ip_network(
                trusted_proxy,
                strict=False,
            ):
                is_trusted_proxy = True
                break
        except ValueError:
            continue

    if not is_trusted_proxy:
        return remote_addr

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if not forwarded_for:
        return remote_addr

    client_ip = forwarded_for.split(",")[0].strip()

    try:
        ipaddress.ip_address(client_ip)
    except ValueError:
        return remote_addr

    return client_ip
