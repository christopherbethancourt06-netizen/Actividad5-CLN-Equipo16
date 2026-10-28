"""R2 — Anticipo: al menos el 30 % del costo de la propuesta aceptada, dentro de los tres días hábiles posteriores a la firma;
después, contacto del Coordinador y 24 horas naturales para pagar.

Fuentes aprobadas: BN-009, SE-010, GL-060 (días hábiles: límite EXCLUSIVO a las 00:00; ventanas de horas: límite INCLUSIVO);
US-009/US-010 con CA-019, CA-020 y CA-021; decisión B del cierre de alcance (el 30 % es un mínimo; el excedente no se devuelve
ni se aplica al saldo). Firma: jueves 01/10/2026 10:00 → los tres días hábiles son vie 02, lun 05 y mar 06; el límite exclusivo
es el miércoles 07/10/2026 a las 00:00. Costo total 10 000.00 → mínimo 3 000.00."""
from datetime import datetime, timedelta

from domain.valores import EstadoContrato, EstadoEvento
from domain.valores import EstadoObligacionPago as EO
from domain.valores import EstadoPago as EPg

from apoyo_u5 import T0, H, contratado, importe

LIMITE_TRES_DIAS_HABILES = datetime(2026, 10, 7, 0, 0)


def _pagar_anticipo(f, cantidad, comprobante, cuando=T0 + timedelta(days=1)):
    f.s.contratacion.registrar_comunicacion_politica_no_reembolso(f.contrato_id, T0)
    ob = f.obligacion('Anticipo')
    r = f.s.pagos.registrar_y_verificar_pago(f.ec_id, ob.obligacion_id, importe(cantidad), cuando, comprobante)
    f.d.despachar()
    return r


def _contrato(f):
    return f.repos.contratos.obtener_por_id(f.contrato_id)


def test_pia05_anticipo_exacto_del_30_por_ciento_confirma_la_contratacion():
    # Arrange
    f = contratado(confirmar=False)
    # Act
    r = _pagar_anticipo(f, '3000.00', 'C-30')
    # Assert
    assert r.exito and r.datos['estado'] == EPg.VERIFICADO.value
    assert f.obligacion('Anticipo').estado == EO.LIQUIDADA
    assert _contrato(f).estado == EstadoContrato.CONTRATACION_CONFIRMADA
    assert f.evento().estado == EstadoEvento.EN_ORGANIZACION


def test_pia06_un_centavo_menos_del_30_por_ciento_no_confirma_hasta_completar():
    f = contratado(confirmar=False)
    _pagar_anticipo(f, '2999.99', 'C-PARCIAL')
    assert f.obligacion('Anticipo').estado == EO.PENDIENTE                 # pago parcial: el anticipo sigue pendiente
    assert _contrato(f).estado == EstadoContrato.FIRMADO                   # la contratación NO se confirma
    f.s.pagos.registrar_y_verificar_pago(f.ec_id, f.obligacion('Anticipo').obligacion_id, importe('0.01'),
                                         T0 + timedelta(days=2), 'C-COMPLEMENTO')
    f.d.despachar()
    assert f.obligacion('Anticipo').estado == EO.LIQUIDADA
    assert _contrato(f).estado == EstadoContrato.CONTRATACION_CONFIRMADA


def test_pia07_anticipo_del_40_por_ciento_cubre_el_requisito_sin_devolucion_ni_abono_al_saldo():
    f = contratado(confirmar=False)
    _pagar_anticipo(f, '4000.00', 'C-40')
    ec = f.ec()
    assert f.obligacion('Anticipo').estado == EO.LIQUIDADA
    assert _contrato(f).estado == EstadoContrato.CONTRATACION_CONFIRMADA
    assert ec.devoluciones == []                                           # decisión B-3: sin devolución automática
    assert ec.saldo_pendiente_contrato() == importe('7000.00')             # decisión B-4: no se aplica al saldo


def test_pia08_seguimiento_solo_despues_del_limite_exclusivo_de_tres_dias_habiles():
    f = contratado(confirmar=False)
    antes = f.s.contratacion.dar_seguimiento_anticipo_pendiente(
        f.contrato_id, LIMITE_TRES_DIAS_HABILES - timedelta(seconds=1), 'Contacto', False)
    en_el_limite = f.s.contratacion.dar_seguimiento_anticipo_pendiente(
        f.contrato_id, LIMITE_TRES_DIAS_HABILES, 'Contacto telefónico', False)
    assert not antes.exito and 'tres días hábiles' in antes.mensaje      # martes 23:59:59 todavía está en plazo
    assert en_el_limite.exito                                            # miércoles 00:00 el plazo ya venció
    assert _contrato(f).seguimientos_anticipo == [(LIMITE_TRES_DIAS_HABILES, 'Contacto telefónico')]


def test_pia09_sin_anticipo_24_horas_despues_del_contacto_se_cierra_sin_contratacion():
    f = contratado(confirmar=False)
    contacto = LIMITE_TRES_DIAS_HABILES + 9 * H
    f.s.contratacion.dar_seguimiento_anticipo_pendiente(f.contrato_id, contacto, 'Contacto', False)
    en_el_limite = f.s.contratacion.dar_seguimiento_anticipo_pendiente(f.contrato_id, contacto + 24 * H, '', True)
    despues = f.s.contratacion.dar_seguimiento_anticipo_pendiente(
        f.contrato_id, contacto + 24 * H + timedelta(seconds=1), '', True)
    f.d.despachar()
    assert not en_el_limite.exito                                          # ventana de horas: límite inclusivo
    assert despues.exito
    assert _contrato(f).estado == EstadoContrato.CERRADO_SIN_CONFIRMAR
    assert f.evento().estado == EstadoEvento.CERRADO_SIN_CONTRATACION      # Cerrado sin contratación, no Cancelado
