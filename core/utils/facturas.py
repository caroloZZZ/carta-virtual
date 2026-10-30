"""
Generador de facturas PDF para Cuba
"""

import os
from io import BytesIO
from django.conf import settings
from django.template.loader import render_to_string
from xhtml2pdf import pisa


def generar_factura_pdf(factura):
    """Genera un PDF para la factura"""

    context = {
        "factura": factura,
        "restaurante": factura.restaurante,
        "transaccion": factura.transaccion,
        "pedido": factura.transaccion.pedido,
        "items": factura.transaccion.pedido.items.all(),
        "hoy": factura.creada_en.date(),
    }

    # Renderizar template HTML
    html_string = render_to_string("facturas/factura_template.html", context)

    # Crear PDF
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=pdf)

    if pisa_status.err:
        return None

    # Guardar PDF
    nombre_archivo = f"factura_{factura.numero_factura}.pdf"
    ruta_archivo = os.path.join(settings.MEDIA_ROOT, "facturas", "pdf", nombre_archivo)

    os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)

    with open(ruta_archivo, "wb") as f:
        f.write(pdf.getvalue())

    return nombre_archivo


def generar_xml_factura(factura):
    """Genera XML para factura electrónica (formato estandarizado para Cuba)"""
    from datetime import datetime

    xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<FacturaElectronica>
    <Encabezado>
        <NumeroFactura>{factura.numero_factura}</NumeroFactura>
        <FechaEmision>{factura.creada_en.strftime('%Y-%m-%dT%H:%M:%S')}</FechaEmision>
        <CAI>{factura.cai}</CAI>
    </Encabezado>
    <Emisor>
        <Nombre>{factura.restaurante.nombre}</Nombre>
        <RTN>{factura.restaurante.rtn or 'N/A'}</RTN>
        <Telefono>{factura.restaurante.telefono}</Telefono>
        <Direccion>{factura.restaurante.direccion}</Direccion>
    </Emisor>
    <Receptor>
        <Nombre>{factura.cliente_nombre}</Nombre>
        <RTN>{factura.rtn or 'Consumidor Final'}</RTN>
        <Telefono>{factura.cliente_telefono}</Telefono>
    </Receptor>
    <Detalle>
        <Subtotal>{factura.subtotal}</Subtotal>
        <Impuestos>{factura.impuestos}</Impuestos>
        <Propina>{factura.propina}</Propina>
        <Total>{factura.total}</Total>
    </Detalle>
</FacturaElectronica>"""

    # Guardar XML
    nombre_archivo = f"factura_{factura.numero_factura}.xml"
    ruta_archivo = os.path.join(settings.MEDIA_ROOT, "facturas", "xml", nombre_archivo)

    os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)

    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write(xml_template)

    return nombre_archivo
