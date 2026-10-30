"""
Configuración de pasarelas de pago para Cuba
"""

PAYMENT_CONFIG = {
    # Transfermóvil (Cuba)
    "transfermovil": {
        "enabled": True,
        "name": "Transfermóvil",
        "logo": "/static/images/transfermovil.png",
        "comision": 0,  # Porcentaje de comisión
        "min_amount": 1.00,
        "max_amount": 1000.00,
        "config": {
            "api_url": "https://api.transfermovil.cu/v1/",
            "merchant_id": "",
            "api_key": "",
        },
    },
    # EnZona (Cuba)
    "enzona": {
        "enabled": True,
        "name": "EnZona",
        "logo": "/static/images/enzona.png",
        "comision": 2.5,  # 2.5% de comisión
        "min_amount": 1.00,
        "max_amount": 5000.00,
        "config": {
            "api_url": "https://api.enzona.cu/v1/",
            "consumer_key": "",
            "consumer_secret": "",
            "access_token": "",
        },
    },
    # Tarjetas Internacionales (Visa/Mastercard)
    "tarjeta": {
        "enabled": True,
        "name": "Tarjeta Internacional",
        "logo": "/static/images/cards.png",
        "comision": 3.5,  # 3.5% de comisión
        "min_amount": 5.00,
        "max_amount": 10000.00,
        "config": {
            "provider": "stripe",  # stripe, paypal, etc.
            "api_key": "",
            "secret_key": "",
        },
    },
    # Efectivo
    "efectivo": {
        "enabled": True,
        "name": "Efectivo",
        "logo": "/static/images/cash.png",
        "comision": 0,
        "min_amount": 0.01,
        "max_amount": 10000.00,
    },
}

# Configuración de impuestos para Cuba
TAX_CONFIG = {
    "iva": 0.10,  # 10% IVA (ajustable)
    "aplica_iva": True,
    "moneda": "CUP",
    "simbolo_moneda": "$",
    "decimales": 2,
}
