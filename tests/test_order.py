"""Pruebas unitarias del dominio (Order.confirm). Patrón Arrange–Act–Assert, sin base de datos ni servicios externos."""
import pytest

from src.domain import CustomerHasDebt, Order

# ---------------------------------------------------------------- pruebas originales del proyecto base


def test_vip_discount():
    o = Order(100, vip=True)
    assert o.confirm() == 85
    assert o.status == "CONFIRMED"


def test_regular_no_discount():
    assert Order(100).confirm() == 100


def test_customer_debt():
    with pytest.raises(CustomerHasDebt):
        Order(100).confirm(customer_debt=50)


@pytest.mark.parametrize("total", [0, -1])
def test_invalid_total(total):
    with pytest.raises(ValueError):
        Order(total).confirm()


# ---------------------------------------------------------------- E2: casos de éxito


def test_pedido_vip_200_descuento_30_cobro_170():
    # Arrange
    order = Order(200, vip=True)
    # Act
    importe = order.confirm()
    # Assert
    assert order.discount == 30
    assert importe == 170
    assert order.status == "CONFIRMED"


def test_pedido_regular_200_sin_descuento_cobro_200():
    # Arrange
    order = Order(200, vip=False)
    # Act
    importe = order.confirm()
    # Assert
    assert order.discount == 0
    assert importe == 200
    assert order.status == "CONFIRMED"


def test_pedido_vip_1000_descuento_150_cobro_850():
    order = Order(1000, vip=True)
    assert order.confirm() == 850
    assert order.discount == 150


# ---------------------------------------------------------------- E2: casos de error


def test_total_cero_se_rechaza_y_el_pedido_sigue_new():
    order = Order(0)
    with pytest.raises(ValueError, match="total must be positive"):
        order.confirm()
    assert order.status == "NEW"
    assert order.discount == 0


def test_total_negativo_se_rechaza_y_el_pedido_sigue_new():
    order = Order(-10, vip=True)
    with pytest.raises(ValueError, match="total must be positive"):
        order.confirm()
    assert order.status == "NEW"


def test_cliente_con_deuda_no_confirma_y_no_aplica_descuento():
    order = Order(500, vip=True)
    with pytest.raises(CustomerHasDebt, match="outstanding debt"):
        order.confirm(customer_debt=250)
    assert order.status == "NEW"
    assert order.discount == 0


# ---------------------------------------------------------------- E2: casos límite


def test_limite_total_minimo_positivo_vip():
    # 0.01 es el menor importe positivo con centavos: el 15 % redondeado a dos decimales es 0.00.
    order = Order(0.01, vip=True)
    assert order.confirm() == pytest.approx(0.01)
    assert order.discount == 0.0
    assert order.status == "CONFIRMED"


def test_limite_deuda_exactamente_cero_permite_confirmar():
    assert Order(120).confirm(customer_debt=0) == 120


def test_limite_deuda_minima_positiva_bloquea():
    with pytest.raises(CustomerHasDebt):
        Order(120).confirm(customer_debt=0.01)


def test_limite_redondeo_descuento_vip_99_99():
    # 15 % de 99.99 = 14.9985, que se redondea a 15.00; el cobro esperado es 84.99.
    order = Order(99.99, vip=True)
    assert order.confirm() == pytest.approx(84.99)
    assert order.discount == 15.0


def test_prioridad_total_invalido_antes_que_deuda():
    # El contrato del código valida primero el total: con total 0 y deuda se informa ValueError.
    with pytest.raises(ValueError):
        Order(0).confirm(customer_debt=100)


# ---------------------------------------------------------------- E3: TDD (Red → Green → Refactor)


def test_cannot_confirm_twice():
    order = Order(100)
    order.confirm()
    with pytest.raises(ValueError, match="already confirmed"):
        order.confirm()
