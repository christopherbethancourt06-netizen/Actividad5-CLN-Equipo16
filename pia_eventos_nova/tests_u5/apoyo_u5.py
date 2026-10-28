"""Escenarios comunes de las pruebas U5. Reutilizan `Flujo` (tests/apoyo_flujo.py), que recorre con los servicios reales la
contratación de un evento. Fechas fijas: firma T0 = jueves 01/10/2026 10:00; evento el viernes 20/11/2026 a las 18:00;
costo total de la propuesta = 10 000.00, por lo que el 30 % del anticipo es 3 000.00."""
from datetime import datetime, timedelta
from decimal import Decimal as D
from unittest.mock import Mock

from application.puertos import IConsultaDisponibilidadProveedor, IVerificadorPagos
from domain.valores import ConceptoPago, CondicionesServicio, Decision, DisponibilidadProveedor, Importe, TipoSolicitud
from infrastructure.composicion import construir

from apoyo_flujo import FECHA_EVENTO, T0, Flujo

__all__ = [
    'FECHA_EVENTO',
    'T0',
    'H',
    'contratado',
    'datetime',
    'importe',
    'mock_disponibilidad',
    'mock_verificador',
    'servicio_adicional_hasta_pago',
]

H = timedelta(hours=1)
COSTO_PROVEEDOR = '1500.00'


def importe(x) -> Importe:
    return Importe(D(str(x)))


def mock_disponibilidad(disponible=True, costo=COSTO_PROVEEDOR):
    """Doble del puerto IConsultaDisponibilidadProveedor (servicio externo de proveedores)."""
    m = Mock(spec=IConsultaDisponibilidadProveedor)
    m.consultar.return_value = [DisponibilidadProveedor('PV-9', disponible, importe(costo),
                                                        CondicionesServicio('DJ 4 horas'))] if disponible else []
    return m


def mock_verificador(resultado=True):
    """Doble del puerto IVerificadorPagos (verificación bancaria del comprobante)."""
    m = Mock(spec=IVerificadorPagos)
    m.verificar.return_value = resultado
    return m


def contratado(app=None, disponibilidad=None, confirmar=True) -> Flujo:
    """Evento con contrato firmado en T0; con `confirmar` también tiene el anticipo de 3 000.00 verificado."""
    return Flujo(app or construir(disponibilidad)).contratar(confirmar=confirmar)


def servicio_adicional_hasta_pago(f: Flujo, dia: datetime, costo=COSTO_PROVEEDOR):
    """Solicitud de servicio adicional registrada en `dia`, con proveedor disponible, aprobada por el Cliente, autorizada por
    Administración, con anexo y con la solicitud de pago comunicada en `dia`. Devuelve (solicitud_id, obligacion_id)."""
    s = f.s.adicionales
    sid = s.registrar_solicitud_servicio_adicional(f.evento_id, f.contrato_id, 'DJ', dia).datos['solicitud_id']
    s.evaluar_disponibilidad_servicio_adicional(sid, [], dia)
    s.registrar_aprobacion_cliente_servicio_adicional(sid, Decision('Cliente', True, dia))
    s.registrar_autorizacion_administracion_servicio_adicional(sid, Decision('Administración', True, dia))
    s.registrar_anexo_servicio_adicional(sid, 'Anexo DJ', dia)
    f.d.despachar()
    ob = f.s.pagos.comunicar_solicitud_pago(TipoSolicitud.SERVICIO_ADICIONAL, sid, ConceptoPago.SERVICIO_ADICIONAL,
                                            importe(costo), dia).datos['obligacion_id']
    return sid, ob
