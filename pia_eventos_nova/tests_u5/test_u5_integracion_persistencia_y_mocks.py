"""Integración U5 sobre Eventos Nova: persistencia real (PostgreSQL de PRUEBAS, `TEST_DATABASE_URL` terminada en «_test») y
servicios externos sustituidos por dobles de prueba (unittest.mock) en los puertos IVerificadorPagos e
IConsultaDisponibilidadProveedor.

Las pruebas de PostgreSQL se OMITEN si la base de pruebas no está disponible, salvo que EVENTOSNOVA_REQUIERE_BD=1 (entonces
fallan), igual que la suite existente del equipo (tests/apoyo_bd.py). Cada prueba vacía las tablas de la base de pruebas al
comenzar y libera la composición al terminar."""
from datetime import datetime, timedelta
from unittest.mock import call

import pytest
import sqlalchemy as sa

from domain.valores import CausaCierreSolicitud, DisponibilidadProveedor, EstadoContrato
from domain.valores import EstadoObligacionPago as EO
from domain.valores import EstadoPago as EPg
from domain.valores import EstadoSolicitudServicioAdicional as ESA
from infrastructure.composicion import construir

from apoyo_u5 import FECHA_EVENTO, T0, contratado, importe, mock_disponibilidad, mock_verificador


# ---------------------------------------------------------------- PostgreSQL de pruebas
@pytest.fixture
def motor():
    from infrastructure.persistencia.preparacion import limpiar_base_de_pruebas

    from apoyo_bd import motor_de_pruebas  # SkipTest (o fallo con EVENTOSNOVA_REQUIERE_BD=1)
    m = motor_de_pruebas()
    limpiar_base_de_pruebas(m)
    return m


@pytest.fixture
def persistente(motor):
    """Fábrica de contenedores persistentes que comparten la base; cada uno simula un proceso distinto (reinicio)."""
    from infrastructure.persistencia.composicion_persistente import construir_persistente
    creados = []

    def nuevo(disponibilidad=None):
        c = construir_persistente(motor=motor, disponibilidad=disponibilidad)
        creados.append(c)
        return c
    yield nuevo
    for c in creados:
        c.cerrar()


def _contar(motor, tabla):
    with motor.connect() as con:
        return con.execute(sa.text(f'select count(*) from "{tabla}"')).scalar()


def test_pia17_anticipo_del_40_por_ciento_persiste_y_se_lee_tras_reiniciar(persistente, motor):
    # Arrange + Act (proceso 1): contratación con anticipo de 4 000.00
    f = contratado(app=persistente(), confirmar=False)
    f.s.contratacion.registrar_comunicacion_politica_no_reembolso(f.contrato_id, T0)
    f.s.pagos.registrar_y_verificar_pago(f.ec_id, f.obligacion('Anticipo').obligacion_id, importe('4000.00'),
                                         T0 + timedelta(days=1), 'C-40')
    f.d.despachar()
    # Assert (proceso 2): lo confirmado está en PostgreSQL
    otro = persistente()
    ec = otro.repos.estados_cuenta.obtener_por_id(f.ec_id)
    anticipo = next(o for o in ec.obligaciones.values() if o.concepto.value == 'Anticipo')
    assert anticipo.estado == EO.LIQUIDADA
    assert [(p.importe, p.estado) for p in ec.pagos] == [(importe('4000.00'), EPg.VERIFICADO)]
    assert ec.saldo_pendiente_contrato() == importe('7000.00')
    assert otro.repos.contratos.obtener_por_id(f.contrato_id).estado == EstadoContrato.CONTRATACION_CONFIRMADA
    assert _contar(motor, 'pago') == 1


def test_pia18_solicitud_no_procedente_por_plazo_persiste_con_su_motivo(persistente):
    f = contratado(app=persistente(mock_disponibilidad()))
    sid = f.s.adicionales.registrar_solicitud_servicio_adicional(f.evento_id, f.contrato_id, 'DJ',
                                                                 datetime(2026, 11, 16, 0, 0)).datos['solicitud_id']
    leida = persistente().repos.adicionales.obtener_por_id(sid)
    assert leida.estado == ESA.NO_PROCEDENTE
    assert leida.motivo_cierre.causa == CausaCierreSolicitud.PLAZO_INSUFICIENTE


def test_pia19_rollback_de_la_unidad_de_trabajo_no_deja_rastro_y_commit_si(persistente, motor):
    c = persistente()
    f = contratado(app=c)
    antes = _contar(motor, 'solicitud_servicio_adicional')
    from domain.solicitudes import SolicitudServicioAdicional
    from domain.valores import AnticipacionSolicitud

    def solicitud(id_):
        return SolicitudServicioAdicional(id_, f.evento_id, f.contrato_id, f.ec_id, 'Foto',
                                          AnticipacionSolicitud(datetime(2026, 11, 1, 9, 0), FECHA_EVENTO))
    revertida, confirmada = solicitud('SA-U5-ROLLBACK'), solicitud('SA-U5-COMMIT')
    c.uow.iniciar(); c.uow.registrar(revertida); c.repos.adicionales.guardar(revertida)
    c.uow.revertir()                                          # rollback: se descarta el INSERT
    c.uow.iniciar(); c.uow.registrar(confirmada); c.repos.adicionales.guardar(confirmada)
    c.uow.confirmar()                                         # commit
    assert persistente().repos.adicionales.obtener_por_id('SA-U5-ROLLBACK') is None
    assert persistente().repos.adicionales.obtener_por_id('SA-U5-COMMIT') is not None
    assert _contar(motor, 'solicitud_servicio_adicional') == antes + 1


# ---------------------------------------------------------------- servicios externos simulados (sin PostgreSQL)
def test_pia20_verificador_de_pagos_simulado_rechaza_y_luego_aprueba():
    # Arrange: el verificador externo (banco) responde «no verificado» en el primer intento
    app = construir()
    verificador = mock_verificador(False)
    app.servicios.pagos.verificador = verificador
    f = contratado(app=app, confirmar=False)
    f.s.contratacion.registrar_comunicacion_politica_no_reembolso(f.contrato_id, T0)
    ob = f.obligacion('Anticipo').obligacion_id
    # Act 1
    r = f.s.pagos.registrar_y_verificar_pago(f.ec_id, ob, importe('3000.00'), T0 + timedelta(days=1), 'C-ANT')
    f.d.despachar()
    # Assert 1: el pago queda solo Registrado y la contratación no se confirma
    verificador.verificar.assert_called_once_with('C-ANT', importe('3000.00'))
    assert r.datos['estado'] == EPg.REGISTRADO.value
    assert f.repos.contratos.obtener_por_id(f.contrato_id).estado == EstadoContrato.FIRMADO
    # Act 2: Administración vuelve a verificar y el banco confirma
    verificador.verificar.return_value = True
    r2 = f.s.pagos.verificar_pago_registrado(f.ec_id, r.datos['pago_id'], T0 + timedelta(days=2))
    f.d.despachar()
    assert r2.exito
    assert verificador.verificar.call_count == 2
    assert f.repos.contratos.obtener_por_id(f.contrato_id).estado == EstadoContrato.CONTRATACION_CONFIRMADA


def test_pia21_consulta_primero_a_proveedores_actuales_y_despues_alternativas():
    disponibilidad = mock_disponibilidad()
    disponibilidad.consultar.side_effect = [
        [DisponibilidadProveedor('PV-1', False)],                                   # el proveedor actual no puede
        mock_disponibilidad().consultar.return_value,                               # alternativa PV-9 disponible
    ]
    f = contratado(disponibilidad=disponibilidad)
    dia = datetime(2026, 11, 10, 9, 0)
    sid = f.s.adicionales.registrar_solicitud_servicio_adicional(f.evento_id, f.contrato_id, 'DJ', dia).datos['solicitud_id']
    f.s.adicionales.evaluar_disponibilidad_servicio_adicional(sid, ['PV-1'], dia)
    assert disponibilidad.consultar.call_args_list == [call('DJ', FECHA_EVENTO, ['PV-1']), call('DJ', FECHA_EVENTO, [])]
    s = f.repos.adicionales.obtener_por_id(sid)
    assert s.disponibilidad.proveedor_id == 'PV-9'
    assert s.estado == ESA.PENDIENTE_APROBACION_CLIENTE
