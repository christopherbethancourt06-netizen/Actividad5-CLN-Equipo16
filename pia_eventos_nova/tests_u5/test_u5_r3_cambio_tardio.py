"""R3 — Cambios: con siete días naturales o más no hay cargo de Eventos Nova; con menos de siete días se cobra el cargo por
cambio tardío (tarifa vigente al registrar la solicitud) solo si el cambio es viable, el Cliente lo acepta y se realiza. El
costo del proveedor se registra por separado. Una vez iniciado el evento no se admiten cambios.

Fuentes aprobadas: BN-003, SE-003, SE-005, GL-020, GL-025; US-024 con CA-061, CA-062 y CA-063; CA-039 (cambios solo antes del
inicio). La tarifa es un dato que informa el negocio: las pruebas usan 500.00 como ejemplo, no como monto aprobado."""
from datetime import timedelta

from domain.valores import ConceptoPago as CP
from domain.valores import Decision, ResultadoViabilidad
from domain.valores import EstadoSolicitudCambio as ESC

from apoyo_u5 import FECHA_EVENTO, contratado, importe

TARIFA_EJEMPLO = '500.00'
COSTO_PROVEEDOR = '800.00'


def _cambio_viable_hasta_pago(dias_antes):
    """Cambio con costo adicional del proveedor, viable, aprobado, autorizado, con anexo y solicitud de pago comunicada."""
    f = contratado()
    dia = FECHA_EVENTO - timedelta(days=dias_antes)
    sid = f.s.cambios.registrar_solicitud_cambio(f.evento_id, f.contrato_id, 'Ampliar horario', importe(TARIFA_EJEMPLO),
                                                 dia).datos['solicitud_id']
    f.s.cambios.evaluar_viabilidad_cambio(sid, ResultadoViabilidad(True), importe(COSTO_PROVEEDOR), dia)
    f.s.cambios.registrar_decision_cliente_cambio(sid, Decision('Cliente', True, dia))
    f.s.cambios.registrar_autorizacion_administracion_cambio(sid, Decision('Administración', True, dia))
    f.s.cambios.registrar_anexo_cambio(sid, 'Anexo del cambio', dia)
    f.d.despachar()
    r = f.s.pagos.comunicar_solicitud_pago_cambio(sid, dia)
    return f, sid, r


def _conceptos(f, sid):
    return {o.concepto: o.importe for o in f.ec().obligaciones_de(sid)}


def test_pia10_limite_siete_dias_exactos_sin_cargo_tardio():
    # Arrange + Act: 13/11 18:00 → 20/11 18:00 = siete días naturales
    f, sid, r = _cambio_viable_hasta_pago(7)
    # Assert
    assert r.exito
    assert f.repos.cambios.obtener_por_id(sid).aplica_cargo_tardio is False
    assert _conceptos(f, sid) == {CP.CAMBIO: importe(COSTO_PROVEEDOR)}            # solo el costo del proveedor


def test_pia11_seis_dias_genera_cargo_tardio_y_costo_del_proveedor_por_separado():
    f, sid, r = _cambio_viable_hasta_pago(6)
    assert r.exito
    assert f.repos.cambios.obtener_por_id(sid).aplica_cargo_tardio is True
    assert _conceptos(f, sid) == {CP.CARGO_CAMBIO_TARDIO: importe(TARIFA_EJEMPLO), CP.CAMBIO: importe(COSTO_PROVEEDOR)}


def test_pia12_cambio_tardio_no_viable_no_procede_y_no_cobra_el_cargo():
    f = contratado()
    dia = FECHA_EVENTO - timedelta(days=3)
    sid = f.s.cambios.registrar_solicitud_cambio(f.evento_id, f.contrato_id, 'Cambiar salón', importe(TARIFA_EJEMPLO),
                                                 dia).datos['solicitud_id']
    r = f.s.cambios.evaluar_viabilidad_cambio(sid, ResultadoViabilidad(False, 'Proveedor sin disponibilidad'), None, dia)
    pago = f.s.pagos.comunicar_solicitud_pago_cambio(sid, dia)
    assert r.exito
    assert f.repos.cambios.obtener_por_id(sid).estado == ESC.NO_PROCEDENTE
    assert not pago.exito                                                         # no hay nada que cobrar
    assert f.ec().obligaciones_de(sid) == []


def test_pia13_no_se_admiten_cambios_una_vez_iniciado_el_evento():
    f = contratado()
    r = f.s.cambios.registrar_solicitud_cambio(f.evento_id, f.contrato_id, 'Cambio de menú', importe(TARIFA_EJEMPLO),
                                               FECHA_EVENTO)                     # T: límite inclusivo, ya inició
    assert not r.exito
    assert 'antes del inicio' in r.mensaje
    assert f.repos.cambios.listar_por_evento_id(f.evento_id) == []                # no se registró ninguna solicitud
