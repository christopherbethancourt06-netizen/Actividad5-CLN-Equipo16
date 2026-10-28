"""Genera matriz_pruebas_base.csv y matriz_pruebas_PIA.csv a partir de la definición de los casos y de los resultados REALES
de pytest (archivos JUnit XML de evidencias/E7 y evidencias/E9). El «Resultado real» y el «Estado de ejecución» salen de la
ejecución: si una prueba no aparece en el XML el caso queda «Pendiente».

Uso desde la raíz del proyecto:  python herramientas/generar_matrices.py"""
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
JUNIT_LAB = RAIZ / 'evidencias' / 'E7' / 'junit_lab.xml'
JUNIT_PIA = RAIZ / 'evidencias' / 'E9' / 'junit_pia_u5.xml'

# --------------------------------------------------------------------------------------------- laboratorio base
# (id, regla, condiciones iniciales, entrada, acción, esperado, tipo de prueba, categoría, test, evidencia)
LAB = [
    ('LAB-01', 'Pedido regular sin descuento', 'Pedido NEW, cliente sin deuda', 'CP01: total 120, regular',
     'confirm()', 'CONFIRMED, cobro 120.00', 'Unitaria (dominio, datos CSV)', 'Éxito',
     'tests/test_casos_csv.py::test_confirmar_segun_csv[CP01]', 'E2'),
    ('LAB-02', 'Descuento VIP 15 %', 'Pedido NEW VIP, sin deuda', 'total 200, VIP', 'confirm()',
     'Descuento 30; cobro 170; estado CONFIRMED', 'Unitaria (dominio)', 'Éxito',
     'tests/test_order.py::test_pedido_vip_200_descuento_30_cobro_170', 'E2'),
    ('LAB-03', 'Pedido regular sin descuento', 'Pedido NEW regular, sin deuda', 'total 200, regular', 'confirm()',
     'Descuento 0; cobro 200; estado CONFIRMED', 'Unitaria (dominio)', 'Éxito',
     'tests/test_order.py::test_pedido_regular_200_sin_descuento_cobro_200', 'E2'),
    ('LAB-04', 'Descuento VIP 15 %', 'Pedido NEW VIP', 'total 1000, VIP (CP06)', 'confirm()',
     'Descuento 150; cobro 850', 'Unitaria (dominio)', 'Éxito',
     'tests/test_order.py::test_pedido_vip_1000_descuento_150_cobro_850', 'E2'),
    ('LAB-05', 'Persistencia con commit', 'Base SQLite en memoria vacía', 'id 2, total 250',
     'save() + commit(); lectura en sesión nueva', 'Registro id 2, total 250, estado NEW visible', 'Integración (SQLAlchemy)', 'Éxito',
     'tests/test_repository.py::test_guardar_pedido_id_2_total_250_commit_y_leer_en_sesion_nueva', 'E4'),
    ('LAB-06', 'Cobro con pasarela (aprobado)', 'Mock de pasarela responde True', 'total 200, VIP', 'checkout()',
     'Devuelve 170; charge() llamado una vez con 170; CONFIRMED', 'Unitaria con mock', 'Éxito',
     'tests/test_service.py::test_pago_aprobado_vip_200_cobra_170', 'E5'),
    ('LAB-07', 'Cancelación por administrador', 'Pedido NEW de otro usuario, 30 días', 'admin, estado NEW',
     'can_cancel()', 'Permitido', 'Unitaria (autorización)', 'Éxito',
     'tests/test_security.py::test_admin_cancela_pedido_new_de_otro_usuario', 'E6'),
    ('LAB-08', 'Cancelación por propietario < 24 h', 'Pedido NEW creado hace 1 h', 'propietario no admin',
     'can_cancel()', 'Permitido', 'Unitaria (autorización)', 'Éxito',
     'tests/test_security.py::test_matriz_autorizacion[SEG-04]', 'E6'),
    ('LAB-09', 'Total debe ser positivo', 'Pedido NEW', 'total 0', 'confirm()',
     'ValueError("total must be positive"); estado sigue NEW', 'Unitaria (dominio)', 'Error',
     'tests/test_order.py::test_total_cero_se_rechaza_y_el_pedido_sigue_new', 'E2'),
    ('LAB-10', 'Total debe ser positivo', 'Pedido NEW VIP', 'total -10', 'confirm()',
     'ValueError; estado sigue NEW', 'Unitaria (dominio)', 'Error',
     'tests/test_order.py::test_total_negativo_se_rechaza_y_el_pedido_sigue_new', 'E2'),
    ('LAB-11', 'Cliente con deuda no confirma', 'Pedido NEW VIP', 'total 500, deuda 250 (CP11)', 'confirm()',
     'CustomerHasDebt; estado NEW; sin descuento', 'Unitaria (dominio)', 'Error',
     'tests/test_order.py::test_cliente_con_deuda_no_confirma_y_no_aplica_descuento', 'E2'),
    ('LAB-12', 'No confirmar dos veces (TDD)', 'Pedido ya confirmado', 'total 100', 'confirm() dos veces',
     'ValueError("already confirmed")', 'Unitaria (dominio, TDD)', 'Error',
     'tests/test_order.py::test_cannot_confirm_twice', 'E3'),
    ('LAB-13', 'Cobro con pasarela (rechazado)', 'Mock de pasarela responde False', 'total 200, VIP', 'checkout()',
     'RuntimeError("payment rejected"); charge() llamado con 170', 'Unitaria con mock', 'Error',
     'tests/test_service.py::test_pago_rechazado_vip_200_intenta_cobrar_170_y_lanza_runtimeerror', 'E5'),
    ('LAB-14', 'Timeout de la pasarela', 'Mock lanza TimeoutError', 'total 120', 'checkout()',
     'TimeoutError propagado; un solo intento (sin reintentos implementados)', 'Unitaria con mock', 'Error',
     'tests/test_service.py::test_timeout_de_la_pasarela_se_propaga_sin_reintentos', 'E5'),
    ('LAB-15', 'Unicidad de id', 'Pedido id 1 confirmado en la base', 'id 1 repetido', 'save() + commit()',
     'IntegrityError; el registro original no cambia', 'Integración (SQLAlchemy)', 'Error',
     'tests/test_repository.py::test_restriccion_unicidad_id_duplicado', 'E4'),
    ('LAB-16', 'Total no nulo', 'Base vacía', 'total None', 'save() + commit()', 'IntegrityError; nada se guarda',
     'Integración (SQLAlchemy)', 'Error', 'tests/test_repository.py::test_restriccion_total_no_nulo', 'E4'),
    ('LAB-17', 'Rollback de cambios pendientes', 'Pedido 1 confirmado; pedido 2 enviado con flush()', 'id 1 y 2',
     'rollback()', 'Solo existe el pedido 1', 'Integración (SQLAlchemy)', 'Error',
     'tests/test_repository.py::test_rollback_deshace_solo_lo_no_confirmado', 'E4'),
    ('LAB-18', 'Tercero no autorizado', 'Pedido CONFIRMED de otro usuario, 5 min', 'usuario 2, no admin',
     'can_cancel()', 'Denegado', 'Unitaria (autorización)', 'Error',
     'tests/test_security.py::test_tercero_no_administrador_tampoco_dentro_de_24h', 'E6'),
    ('LAB-19', 'SHIPPED nunca se cancela', 'Pedido SHIPPED', 'administrador', 'can_cancel()', 'Denegado',
     'Unitaria (autorización)', 'Error', 'tests/test_security.py::test_shipped_denied_even_admin', 'E6'),
    ('LAB-20', 'Total mínimo positivo', 'Pedido NEW VIP', 'total 0.01 (CP07)', 'confirm()',
     'Descuento 0.00; cobro 0.01; CONFIRMED', 'Unitaria (dominio)', 'Límite',
     'tests/test_order.py::test_limite_total_minimo_positivo_vip', 'E2'),
    ('LAB-21', 'Deuda igual a cero', 'Pedido NEW', 'total 120, deuda 0', 'confirm()', 'Cobro 120 (permitido)',
     'Unitaria (dominio)', 'Límite', 'tests/test_order.py::test_limite_deuda_exactamente_cero_permite_confirmar', 'E2'),
    ('LAB-22', 'Deuda mínima positiva', 'Pedido NEW', 'total 120, deuda 0.01', 'confirm()', 'CustomerHasDebt',
     'Unitaria (dominio)', 'Límite', 'tests/test_order.py::test_limite_deuda_minima_positiva_bloquea', 'E2'),
    ('LAB-23', 'Redondeo del descuento VIP', 'Pedido NEW VIP', 'total 99.99 (CP12)', 'confirm()',
     'Descuento 15.00; cobro 84.99', 'Unitaria (dominio)', 'Límite',
     'tests/test_order.py::test_limite_redondeo_descuento_vip_99_99', 'E2'),
    ('LAB-24', 'Ventana de 24 h del propietario', 'Pedido NEW creado hace 24 h exactas', 'propietario no admin',
     'can_cancel()', 'Denegado (el límite no se incluye)', 'Unitaria (autorización)', 'Límite',
     'tests/test_security.py::test_propietario_exactamente_a_las_24_horas_se_rechaza', 'E6'),
    ('LAB-25', 'Ventana de 24 h del propietario', 'Pedido NEW creado hace 23:59:59', 'propietario no admin',
     'can_cancel()', 'Permitido', 'Unitaria (autorización)', 'Límite',
     'tests/test_security.py::test_propietario_un_segundo_antes_de_24_horas_se_permite', 'E6'),
    ('LAB-26', 'No confirmar dos veces (datos CSV)', 'Pedido 8 cargado con estado CONFIRMED', 'CP08: total 250',
     'confirm()', 'ValueError("already confirmed") (tras TDD; antes: CONFIRMED)', 'Unitaria (dominio, datos CSV)',
     'Límite', 'tests/test_casos_csv.py::test_confirmar_segun_csv[CP08]', 'E3'),
    ('LAB-27', 'Riesgo: confirmar antes del pago', 'Mock de pasarela responde False', 'total 200, VIP',
     'checkout()', 'El pedido NO debería quedar CONFIRMED si el pago se rechaza', 'Unitaria con mock (riesgo)',
     'Riesgo documentado',
     'tests/test_service.py::test_riesgo_pedido_no_deberia_quedar_confirmado_si_el_pago_se_rechaza', 'E5'),
]

# --------------------------------------------------------------------------------------------- PIA Eventos Nova
R1 = 'R1 Servicio adicional: mínimo 5 días naturales y orden de verificación'
R2 = 'R2 Anticipo: mínimo 30 % en 3 días hábiles; contacto y 24 h'
R3 = 'R3 Cambio tardío: < 7 días naturales, cargo por tarifa vigente separado del costo del proveedor'
R4 = 'R4 Pago de servicio adicional: 24 horas naturales desde la solicitud de pago'
RI = 'Integración: persistencia PostgreSQL y servicios externos simulados'
F1 = 'tests_u5/test_u5_r1_servicio_adicional_plazo.py'
F2 = 'tests_u5/test_u5_r2_anticipo.py'
F3 = 'tests_u5/test_u5_r3_cambio_tardio.py'
F4 = 'tests_u5/test_u5_r4_pago_servicio_adicional_24h.py'
FI = 'tests_u5/test_u5_integracion_persistencia_y_mocks.py'
# (id, regla, requisito, US/CA, precondiciones, entrada, rol, acción, esperado, tipo, categoría, test)
PIA = [
    ('PIA-01', R1, 'BN-004, SE-004, GL-015', 'US-025; CA-073, CA-075', 'Contratación confirmada; evento 20/11/2026 18:00',
     'Solicitud el 10/11/2026 09:00 (10 días)', 'Coordinador', 'Registrar solicitud y consultar disponibilidad',
     ('Registrada sin motivo; consulta a proveedores; Pendiente de aprobación del Cliente; importe = costo del proveedor '
      '(1 500.00), sin cargo propio'), 'Integración de servicios (memoria) + mock', 'Éxito',
     f'{F1}::test_pia01_solicitud_con_diez_dias_procede_y_consulta_proveedores'),
    ('PIA-02', R1, 'BN-004, SE-004, GL-015', 'US-025; CA-083', 'Contratación confirmada',
     'Solicitud el 15/11/2026 23:59 (5 días naturales por fecha)', 'Coordinador', 'Registrar solicitud',
     'Procede (Registrada)', 'Integración de servicios (memoria)', 'Límite',
     f'{F1}::test_pia02_limite_exactamente_cinco_dias_naturales_procede'),
    ('PIA-03', R1, 'BN-004, SE-004, GL-015', 'US-025; CA-083', 'Contratación confirmada',
     'Solicitud el 16/11/2026 00:00 (4 días)', 'Coordinador', 'Registrar solicitud',
     'No procedente por plazo insuficiente; no se consultan proveedores', 'Integración de servicios + mock', 'Error',
     f'{F1}::test_pia03_cuatro_dias_no_procede_y_no_se_buscan_proveedores'),
    ('PIA-03b', R1, 'BN-004, SE-004', 'US-025; CA-083', 'Solicitud ya No procedente por plazo',
     'Reintento de evaluar disponibilidad', 'Coordinador', 'evaluar_disponibilidad_servicio_adicional()',
     ('Se rechaza con el mismo mensaje de antes y NO se consulta a proveedores (hallazgo U5-H1, corregido el '
      '28/10/2026)'), 'Integración de servicios + mock (corrección U5-H1)', 'Error',
     f'{F1}::test_pia03b_solicitud_no_procedente_no_debe_consultar_proveedores_al_reintentar'),
    ('PIA-04', R1, 'BN-004, SE-004, GL-015', 'US-025; CA-083', 'Evento cancelado el 12/11/2026',
     'Solicitud el 17/11/2026 (3 días)', 'Coordinador', 'Registrar solicitud',
     'No procedente con el primer motivo: evento cancelado (no el de plazo)', 'Integración de servicios (memoria)',
     'Error', f'{F1}::test_pia04_evento_cancelado_se_informa_primero_aunque_falten_menos_de_cinco_dias'),
    ('PIA-05', R2, 'BN-009, SE-010; decisión B', 'US-009; CA-019', 'Contrato firmado el 01/10/2026; política comunicada',
     'Anticipo 3 000.00 (30 % de 10 000.00)', 'Administración', 'Registrar y verificar pago',
     'Pago Verificado; anticipo Liquidado; contratación confirmada; evento En organización',
     'Integración de servicios (memoria)', 'Éxito', f'{F2}::test_pia05_anticipo_exacto_del_30_por_ciento_confirma_la_contratacion'),
    ('PIA-06', R2, 'BN-009; decisión B', 'US-009; CA-019', 'Contrato firmado; política comunicada',
     'Anticipo 2 999.99 y después 0.01', 'Administración', 'Registrar y verificar pagos',
     'Con 2 999.99 el anticipo sigue Pendiente y no se confirma; con el complemento se liquida y se confirma',
     'Integración de servicios (memoria)', 'Límite',
     f'{F2}::test_pia06_un_centavo_menos_del_30_por_ciento_no_confirma_hasta_completar'),
    ('PIA-07', R2, 'BN-009; decisión B (B-2, B-3, B-4)', 'US-009; CA-019', 'Contrato firmado; política comunicada',
     'Anticipo 4 000.00 (40 %)', 'Administración', 'Registrar y verificar pago',
     'Requisito cubierto; sin devolución; saldo del contrato sigue en 7 000.00', 'Integración de servicios (memoria)',
     'Éxito', f'{F2}::test_pia07_anticipo_del_40_por_ciento_cubre_el_requisito_sin_devolucion_ni_abono_al_saldo'),
    ('PIA-08', R2, 'BN-009, SE-010, GL-060', 'US-010; CA-020', 'Firma jueves 01/10/2026 10:00; sin anticipo',
     'Seguimiento el 06/10 23:59:59 y el 07/10 00:00', 'Coordinador', 'Registrar seguimiento del anticipo',
     'Antes del límite exclusivo se rechaza; a las 00:00 del 07/10 se registra', 'Integración de servicios (memoria)',
     'Límite', f'{F2}::test_pia08_seguimiento_solo_despues_del_limite_exclusivo_de_tres_dias_habiles'),
    ('PIA-09', R2, 'BN-009, SE-010, GL-060', 'US-010; CA-021', 'Contacto registrado el 07/10/2026 09:00; sin pago',
     'Cierre en contacto + 24 h y en + 24 h 1 s', 'Coordinador', 'Cerrar la contratación por falta de anticipo',
     ('En + 24 h exactas se rechaza (límite inclusivo); después: contrato Cerrado sin confirmar y evento Cerrado sin '
      'contratación (no Cancelado)'), 'Integración de servicios (memoria)', 'Error',
     f'{F2}::test_pia09_sin_anticipo_24_horas_despues_del_contacto_se_cierra_sin_contratacion'),
    ('PIA-10', R3, 'BN-003, SE-003, GL-020', 'US-024; CA-061, CA-063', 'Contratación confirmada',
     'Cambio el 13/11/2026 18:00 (7 días); costo proveedor 800.00; tarifa ejemplo 500.00', 
     'Coordinador / Cliente / Administración', 'Registrar, evaluar, aprobar, autorizar, anexo y solicitud de pago',
     'Sin cargo tardío; solo la obligación del costo del proveedor', 'Integración de servicios (memoria)', 'Límite',
     f'{F3}::test_pia10_limite_siete_dias_exactos_sin_cargo_tardio'),
    ('PIA-11', R3, 'BN-003, SE-005, GL-025', 'US-024; CA-062, CA-063', 'Contratación confirmada',
     'Cambio el 14/11/2026 18:00 (6 días); costo 800.00; tarifa 500.00', 'Coordinador / Cliente / Administración',
     'Igual que PIA-10', 'Dos obligaciones independientes: cargo por cambio tardío 500.00 y costo del proveedor 800.00',
     'Integración de servicios (memoria)', 'Éxito',
     f'{F3}::test_pia11_seis_dias_genera_cargo_tardio_y_costo_del_proveedor_por_separado'),
    ('PIA-12', R3, 'BN-003, SE-005, GL-025', 'US-024; CA-062', 'Contratación confirmada',
     'Cambio a 3 días; proveedores responden no viable', 'Coordinador', 'Evaluar viabilidad y pedir pago',
     'No procedente; no se genera ninguna obligación (no se cobra el cargo)', 'Integración de servicios (memoria)',
     'Error', f'{F3}::test_pia12_cambio_tardio_no_viable_no_procede_y_no_cobra_el_cargo'),
    ('PIA-13', R3, 'BN-003, GL-060 (límite inclusivo en T)', 'CA-039', 'Contratación confirmada',
     'Solicitud de cambio el 20/11/2026 18:00 (inicio)', 'Coordinador', 'Registrar solicitud de cambio',
     'Rechazo: el cambio solo procede antes del inicio; no se registra solicitud', 'Integración de servicios (memoria)',
     'Error', f'{F3}::test_pia13_no_se_admiten_cambios_una_vez_iniciado_el_evento'),
    ('PIA-14', R4, 'BN-004, SE-004, GL-045', 'US-025; CA-080, CA-082', 'Solicitud de pago comunicada el 10/11/2026 09:00',
     'Pago 1 500.00 a las + 10 h', 'Administración / Coordinador', 'Registrar pago y confirmar servicio',
     'Servicio adicional Confirmado e incorporado al evento', 'Integración de servicios (memoria)', 'Éxito',
     f'{F4}::test_pia14_pago_dentro_de_las_24_horas_permite_confirmar_el_servicio'),
    ('PIA-15', R4, 'BN-004, GL-060', 'US-025; CA-080, CA-082', 'Solicitud de pago comunicada',
     'Pago efectuado en + 24 h exactas y registrado en + 30 h', 'Administración / Coordinador',
     'Intentar cierre por falta de pago y confirmar', 'No se cierra (límite inclusivo); el servicio se confirma',
     'Integración de servicios (memoria)', 'Límite',
     f'{F4}::test_pia15_limite_pago_en_la_hora_24_exacta_verificado_despues_no_cierra'),
    ('PIA-16', R4, 'BN-004, GL-060', 'US-025; CA-080', 'Solicitud de pago comunicada; sin pago',
     'Cierre en + 24 h 1 s', 'Coordinador', 'Cerrar por falta de pago',
     'Cerrada por falta de pago; obligación Sin efecto; no se puede confirmar ni se incorpora el servicio',
     'Integración de servicios (memoria)', 'Error',
     f'{F4}::test_pia16_sin_pago_un_segundo_despues_del_limite_se_cierra_por_falta_de_pago'),
    ('PIA-17', RI + ' (R2)', 'BN-009; decisión B', 'CA-019', 'Base PostgreSQL de pruebas vacía',
     'Anticipo 4 000.00', 'Administración', 'Ejecutar el caso y leerlo desde otro contenedor (reinicio)',
     'Anticipo Liquidado, pago Verificado, saldo 7 000.00 y contrato confirmado leídos desde PostgreSQL',
     'Integración (PostgreSQL)', 'Éxito', f'{FI}::test_pia17_anticipo_del_40_por_ciento_persiste_y_se_lee_tras_reiniciar'),
    ('PIA-18', RI + ' (R1)', 'BN-004, SE-004', 'CA-083', 'Base PostgreSQL de pruebas vacía',
     'Solicitud a 4 días', 'Coordinador', 'Registrar y leer tras reinicio',
     'No procedente con causa Plazo insuficiente persistida', 'Integración (PostgreSQL)', 'Error',
     f'{FI}::test_pia18_solicitud_no_procedente_por_plazo_persiste_con_su_motivo'),
    ('PIA-19', RI, 'ADR-004 (Unidad de trabajo)', '—', 'Base PostgreSQL de pruebas',
     'Dos solicitudes guardadas en transacciones distintas', 'Sistema', 'revertir() en una y confirmar() en otra',
     'La revertida no existe; la confirmada sí; el conteo aumenta en 1', 'Integración (PostgreSQL, transacciones)',
     'Límite', f'{FI}::test_pia19_rollback_de_la_unidad_de_trabajo_no_deja_rastro_y_commit_si'),
    ('PIA-20', RI + ' (R2)', 'BN-009', 'CA-019', 'Verificador de pagos simulado (Mock) responde False y luego True',
     'Anticipo 3 000.00, comprobante C-ANT', 'Administración', 'Registrar pago y volver a verificar',
     'Primero queda Registrado y no se confirma; tras la verificación se confirma; el mock recibe (C-ANT, 3 000.00)',
     'Unitaria/integración con mock', 'Error',
     f'{FI}::test_pia20_verificador_de_pagos_simulado_rechaza_y_luego_aprueba'),
    ('PIA-21', RI + ' (R1)', 'SE-004', 'CA-073, CA-074', 'Proveedor actual PV-1 no disponible; alternativa PV-9 disponible',
     'Solicitud a 10 días', 'Coordinador', 'Evaluar disponibilidad',
     'Consulta primero a PV-1 y después la general; elige PV-9', 'Integración con mock', 'Éxito',
     f'{FI}::test_pia21_consulta_primero_a_proveedores_actuales_y_despues_alternativas'),
]


def resultados(xml: Path) -> dict:
    """{'archivo::prueba[param]': (estado, detalle)} leído del JUnit XML de pytest."""
    if not xml.exists():
        return {}
    salida = {}
    for tc in ET.parse(xml).getroot().iter('testcase'):
        archivo = tc.get('classname').replace('.', '/') + '.py'
        clave = f"{archivo}::{tc.get('name')}"
        hijos = {c.tag: c for c in tc}
        if 'failure' in hijos or 'error' in hijos:
            c = hijos.get('failure', hijos.get('error'))
            salida[clave] = ('FAILED', (c.get('message') or '')[:400])
        elif 'skipped' in hijos:
            mensaje = hijos['skipped'].get('message') or ''
            tipo = 'XFAIL' if hijos['skipped'].get('type') == 'pytest.xfail' or 'xfail' in mensaje.lower() else 'SKIPPED'
            salida[clave] = (tipo, mensaje[:400])
        else:
            salida[clave] = ('PASSED', '')
    return salida


def fecha(xml: Path) -> str:
    """Fecha y hora de la ejecución registrada en el JUnit XML (atributo timestamp de pytest)."""
    if not xml.exists():
        return ''
    suite = next(ET.parse(xml).getroot().iter('testsuite'), None)
    marca = suite.get('timestamp', '') if suite is not None else ''
    return marca[:16].replace('T', ' ')


def real(esperado, estado, detalle):
    if estado == 'PASSED':
        return f'Coincide con el esperado: {esperado}'
    if estado == 'XFAIL':
        return 'No coincide (fallo esperado documentado): ' + detalle.replace('reason: ', '')
    if estado == 'Pendiente':
        return 'Pendiente de ejecución'
    return f'{estado}: {detalle}'


def main():
    lab_res, lab_fecha = resultados(JUNIT_LAB), fecha(JUNIT_LAB)
    filas = []
    for (id_, regla, cond, entrada, accion, esperado, tipo, cat, test, ev) in LAB:
        estado, detalle = lab_res.get(test, ('Pendiente', ''))
        filas.append({'ID': id_, 'Alcance': 'Laboratorio base U5', 'Regla comprobada': regla,
                      'Condiciones iniciales': cond, 'Datos de entrada': entrada, 'Acción ejecutada': accion,
                      'Resultado esperado': esperado, 'Resultado real': real(esperado, estado, detalle),
                      'Tipo de prueba': tipo, 'Categoría': cat, 'Estado de ejecución': estado,
                      'Fecha de ejecución': lab_fecha if estado != 'Pendiente' else '',
                      'Test automatizado': test, 'Evidencia': ev})
    escribir(RAIZ / 'matriz_pruebas_base.csv', filas)

    pia_res, pia_fecha = resultados(JUNIT_PIA), fecha(JUNIT_PIA)
    filas = []
    for (id_, regla, req, ca, pre, entrada, rol, accion, esperado, tipo, cat, test) in PIA:
        estado, detalle = pia_res.get(test, ('Pendiente', ''))
        filas.append({'ID': id_, 'Alcance': 'PIA Eventos Nova (código real del equipo)', 'Regla': regla,
                      'Requisito de origen': req, 'Historia / criterio de aceptación': ca, 'Precondiciones': pre,
                      'Entrada': entrada, 'Rol': rol, 'Acción ejecutada': accion, 'Resultado esperado': esperado,
                      'Resultado real': real(esperado, estado, detalle), 'Tipo de prueba': tipo, 'Categoría': cat,
                      'Test asociado': 'pia_eventos_nova/Eventosnova/' + test, 'Estado de ejecución': estado,
                      'Fecha de ejecución': pia_fecha if estado != 'Pendiente' else '', 'Evidencia': 'E9'})
    escribir(RAIZ / 'matriz_pruebas_PIA.csv', filas)


def escribir(ruta: Path, filas):
    with ruta.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    conteo = {}
    for fila in filas:
        conteo[fila['Estado de ejecución']] = conteo.get(fila['Estado de ejecución'], 0) + 1
    print(f'{ruta.name}: {len(filas)} casos {conteo}')


if __name__ == '__main__':
    main()
