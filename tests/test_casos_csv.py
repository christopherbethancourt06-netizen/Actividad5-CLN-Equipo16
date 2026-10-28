"""Pruebas parametrizadas con los datos DIDÁCTICOS del profesor (datos_prueba/*.csv), leídos expresamente con csv.DictReader.

Los CSV no se cargan solos ni sustituyen a la base SQLite en memoria de las pruebas de repositorio. Los datos son
ficticios. El caso CP08 está marcado en el CSV como «comportamiento actual; ampliar con TDD»: después del ciclo
Red–Green–Refactor el resultado esperado de ese caso es ValueError("already confirmed") (ver tests/test_order.py)."""
import csv
from pathlib import Path
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from src.application import OrderService
from src.domain import CustomerHasDebt, Order
from src.repository import OrderRow, SqlOrderRepository, make_engine

DATOS = Path(__file__).resolve().parent.parent / "datos_prueba"

# Resultado esperado de CP08 después del ciclo TDD (el CSV original describe el comportamiento anterior).
ESPERADO_TRAS_TDD = {"CP08": "ValueError: already confirmed"}


def _leer(nombre):
    with (DATOS / nombre).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


PEDIDOS = {fila["pedido_id"]: fila for fila in _leer("pedidos_prueba.csv")}
CASOS = _leer("casos_de_prueba.csv")


def _pedido(fila):
    return Order(float(fila["total"]), vip=fila["es_vip"] == "1", status=fila["estado_inicial"])


@pytest.mark.parametrize("caso", [c for c in CASOS if c["accion"] == "confirmar"], ids=lambda c: c["caso_id"])
def test_confirmar_segun_csv(caso):
    fila = PEDIDOS[caso["pedido_id"]]
    order = _pedido(fila)
    esperado = ESPERADO_TRAS_TDD.get(caso["caso_id"], caso["resultado_esperado"])
    deuda = float(fila["deuda_cliente"])

    if esperado.startswith("CONFIRMED"):
        cobro = float(esperado.split("cobro")[1])
        assert order.confirm(customer_debt=deuda) == pytest.approx(cobro)
        assert order.status == "CONFIRMED"
    elif esperado == "CustomerHasDebt":
        with pytest.raises(CustomerHasDebt):
            order.confirm(customer_debt=deuda)
        assert order.status == fila["estado_inicial"]
    else:
        tipo, _, mensaje = esperado.partition(":")
        assert tipo == "ValueError"
        with pytest.raises(ValueError, match=mensaje.strip() or None):
            order.confirm(customer_debt=deuda)


def test_cp13_pago_rechazado_segun_csv():
    caso = next(c for c in CASOS if c["caso_id"] == "CP13")
    assert caso["resultado_esperado"] == "RuntimeError: payment rejected"
    gateway = Mock(spec_set=["charge"])
    gateway.charge.return_value = False
    with pytest.raises(RuntimeError, match="payment rejected"):
        OrderService(gateway).checkout(_pedido(PEDIDOS["1"]))
    gateway.charge.assert_called_once_with(120)


@pytest.mark.parametrize("caso_id, confirmar, visible", [("CP14", True, True), ("CP15", False, False)])
def test_cp14_cp15_commit_y_rollback_segun_csv(caso_id, confirmar, visible):
    assert any(c["caso_id"] == caso_id for c in CASOS)
    engine = make_engine()
    try:
        with Session(engine) as s:
            SqlOrderRepository(s).save(1, _pedido(PEDIDOS["1"]))
            s.commit() if confirmar else s.rollback()
        with Session(engine) as s:
            assert (s.get(OrderRow, 1) is not None) is visible
    finally:
        engine.dispose()
