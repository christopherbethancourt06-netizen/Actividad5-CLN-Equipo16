"""R4 — Pago de un servicio adicional: 24 horas naturales desde la comunicación de la solicitud de pago; si al vencer el plazo
el Cliente no pagó, la solicitud se cierra por falta de pago. Cuenta la fecha en que el Cliente pagó, no la del registro o la
verificación de Administración. Límite inclusivo de las ventanas de horas (GL-060).

Fuentes aprobadas: BN-004, SE-004, GL-045, GL-060; US-025 con CA-080 y CA-082. La solicitud de pago se comunica el
10/11/2026 a las 09:00 (diez días antes del evento)."""
from datetime import datetime, timedelta

from domain.valores import EstadoObligacionPago as EO
from domain.valores import EstadoSolicitudServicioAdicional as ESA

from apoyo_u5 import H, contratado, importe, mock_disponibilidad, servicio_adicional_hasta_pago

COMUNICACION = datetime(2026, 11, 10, 9, 0)


def _escenario():
    f = contratado(disponibilidad=mock_disponibilidad())
    sid, ob = servicio_adicional_hasta_pago(f, COMUNICACION)
    return f, sid, ob


def _estado(f, sid):
    return f.repos.adicionales.obtener_por_id(sid).estado


def test_pia14_pago_dentro_de_las_24_horas_permite_confirmar_el_servicio():
    # Arrange
    f, sid, ob = _escenario()
    # Act
    f.s.pagos.registrar_y_verificar_pago(f.ec_id, ob, importe('1500.00'), COMUNICACION + 10 * H, 'C-SA-1')
    r = f.s.adicionales.confirmar_servicio_adicional(sid, COMUNICACION + 11 * H)
    f.d.despachar()
    # Assert
    assert r.exito
    assert _estado(f, sid) == ESA.CONFIRMADA
    assert any(sc.servicio == 'DJ' for sc in f.evento().servicios.values())       # se incorporó al Evento


def test_pia15_limite_pago_en_la_hora_24_exacta_verificado_despues_no_cierra():
    f, sid, ob = _escenario()
    assert not f.s.adicionales.cerrar_servicio_adicional_por_falta_de_pago(sid, COMUNICACION + 24 * H).exito
    f.s.pagos.registrar_y_verificar_pago(f.ec_id, ob, importe('1500.00'), COMUNICACION + 24 * H, 'C-SA-2',
                                         registrado_en=COMUNICACION + 30 * H)      # Administración registra 6 h después
    assert not f.s.adicionales.cerrar_servicio_adicional_por_falta_de_pago(sid, COMUNICACION + 31 * H).exito
    assert f.s.adicionales.confirmar_servicio_adicional(sid, COMUNICACION + 31 * H).exito


def test_pia16_sin_pago_un_segundo_despues_del_limite_se_cierra_por_falta_de_pago():
    f, sid, ob = _escenario()
    r = f.s.adicionales.cerrar_servicio_adicional_por_falta_de_pago(sid, COMUNICACION + 24 * H + timedelta(seconds=1))
    f.d.despachar()
    assert r.exito
    assert _estado(f, sid) == ESA.CERRADA_FALTA_PAGO
    assert f.ec().obligaciones[ob].estado == EO.SIN_EFECTO
    assert not f.s.adicionales.confirmar_servicio_adicional(sid, COMUNICACION + 25 * H).exito
    assert not any(sc.servicio == 'DJ' for sc in f.evento().servicios.values())   # el servicio no se realiza
