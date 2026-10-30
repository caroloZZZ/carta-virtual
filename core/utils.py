import ipaddress


def is_private_ip(ip):
    """
    Devuelve True si la IP es privada (red local).
    Ejemplos: 192.168.x.x, 10.x.x.x, 172.16.x.x
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except ValueError:
        return False
