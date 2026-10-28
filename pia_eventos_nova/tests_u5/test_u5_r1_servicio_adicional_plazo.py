"""R1 — Servicio adicional: al menos cinco días naturales de anticipación y orden de verificación.

Fuentes aprobadas: BN-004, SE-004 y GL-015 (BRD/glosario); US-025 con CA-083 (menos de cinco días: no procedente, sin buscar
proveedores) y CA-073/CA-075 (el costo es el del proveedor; Eventos Nova no cobra un cargo propio). Orden: 1) evento no
cancelado ni iniciado, 2) cinco días naturales, 3) saldo vencido; se registra solo el primer motivo.
Evento: viernes 20/11/2026 18:00."""
from datetime import datetime

import pytest

from domain.valores import CausaCierreSolicitud
from domain.valores import EstadoSolicitudServicioAdicional as ESA

from apoyo_u5 import FECHA_EVENTO, contratado, importe, mock_disponibilidad


def _solicitud(f, sid):
    return f.repos.adicionales.obtener_por_id(sid)


def test_pia01_solicitud_con_diez_dias_procede_y_consulta_proveedores():
    # Arrange
    disponibilidad = mock_disponibilidad()
    f = contratado(disponibilidad=disponibilidad)
    dia = datetime(2026, 11, 10, 9, 0)                                   # 10 días naturales antes del evento
    # Act
    r = f.s.adicionales.registrar_solicitud_servicio_adicional(f.evento_id, f.contrato_id, 'DJ', dia)
    eval_ = f.s.adicionales.evaluar_disponibilidad_servicio_adicional(r.datos['solicitud_id'], [], dia)
    # Assert
    s = _solicitud(f, r.datos['solicitud_id'])
    assert r.exito and r.datos['estado'] == ESA.REGISTRADA.value and r.datos['motivo'] == ''
    assert eval_.exito
    assert s.estado == ESA.PENDIENTE_APROBACION_CLIENTE
    disponibilidad.consultar.assert_called_with('DJ', FECHA_EVENTO, [])          # consulta general de proveedores
    assert s.importe_a_cobrar == importe('1500.00')                              # solo el costo del proveedor


def test_pia02_limite_exactamente_cinco_dias_naturales_procede():
    # 15/11 23:59 → 20/11: cinco días naturales por fecha calendario (4 días 18 h 1 min en horas reales).
    f = contratado(disponibilidad=mock_disponibilidad())
    r = f.s.adicionales.registrar_solicitud_servicio_adicional(f.evento_id, f.contrato_id, 'DJ',
                                                               datetime(2026, 11, 15, 23, 59))
    assert r.exito
    assert _solicitud(f, r.datos['solicitud_id']).estado == ESA.REGISTRADA


def test_pia03_cuatro_dias_no_procede_y_no_se_buscan_proveedores():
    disponibilidad = mock_disponibilidad()
    f = contratado(disponibilidad=disponibilidad)
    dia = datetime(2026, 11, 16, 0, 0)                                   # cuatro días naturales antes del evento
    r = f.s.adicionales.registrar_solicitud_servicio_adicional(f.evento_id, f.contrato_id, 'DJ', dia)
    s = _solicitud(f, r.datos['solicitud_id'])
    assert s.estado == ESA.NO_PROCEDENTE
    assert s.motivo_cierre.causa == CausaCierreSolicitud.PLAZO_INSUFICIENTE
    assert 'cinco días naturales' in r.datos['motivo']
    disponibilidad.consultar.assert_not_called()                         # CA-083: no continúa con la búsqueda


@pytest.mark.xfail(strict=True, reason="Hallazgo U5-H1: evaluar_disponibilidad_servicio_adicional() consulta al puerto "
                                       "de proveedores ANTES de que el dominio rechace la transición de una solicitud que "
                                       "ya es No procedente (CA-083 indica no continuar con la búsqueda).")
def test_pia03b_solicitud_no_procedente_no_debe_consultar_proveedores_al_reintentar():
    disponibilidad = mock_disponibilidad()
    f = contratado(disponibilidad=disponibilidad)
    dia = datetime(2026, 11, 16, 0, 0)
    sid = f.s.adicionales.registrar_solicitud_servicio_adicional(f.evento_id, f.contrato_id, 'DJ', dia).datos['solicitud_id']
    r = f.s.adicionales.evaluar_disponibilidad_servicio_adicional(sid, [], dia)
    assert not r.exito                                                   # el dominio sí rechaza el cambio de estado
    assert _solicitud(f, sid).estado == ESA.NO_PROCEDENTE
    disponibilidad.consultar.assert_not_called()                         # expectativa según CA-083


def test_pia04_evento_cancelado_se_informa_primero_aunque_falten_menos_de_cinco_dias():
    f = contratado(disponibilidad=mock_disponibilidad())
    cancelacion = f.s.cierre.gestionar_cancelacion_solicitada(f.evento_id, 'El Cliente cancela', datetime(2026, 11, 12, 9, 0))
    f.d.despachar()
    assert cancelacion.exito
    r = f.s.adicionales.registrar_solicitud_servicio_adicional(f.evento_id, f.contrato_id, 'DJ', datetime(2026, 11, 17, 9, 0))
    s = _solicitud(f, r.datos['solicitud_id'])
    assert s.estado == ESA.NO_PROCEDENTE
    assert s.motivo_cierre.causa == CausaCierreSolicitud.EVENTO_CANCELADO           # primer motivo; no el de plazo
    assert 'cancelado' in r.datos['motivo']
