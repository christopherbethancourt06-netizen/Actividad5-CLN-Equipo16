"""Pruebas del servicio de aplicación OrderService con una pasarela de pago SIMULADA (unittest.mock.Mock).

No se realiza ningún cobro real ni llamada de red: el doble de prueba solo expone `charge`, y la prueba decide qué
responde (True, False o una excepción)."""
from unittest.mock import Mock

import pytest

from src.application import OrderService
from src.domain import Order


def pasarela(respuesta=True, error=None):
    """Mock limitado a la interfaz real que usa OrderService (`charge`): un atributo mal escrito provoca error."""
    gateway = Mock(spec_set=["charge"])
    gateway.charge.return_value = respuesta
    if error is not None:
        gateway.charge.side_effect = error
    return gateway


# ---------------------------------------------------------------- pruebas originales


def test_gateway_approved():
    gateway = Mock()
    gateway.charge.return_value = True
    assert OrderService(gateway).checkout(Order(100)) == 100
    gateway.charge.assert_called_once_with(100)


def test_gateway_rejected():
    gateway = Mock()
    gateway.charge.return_value = False
    with pytest.raises(RuntimeError):
        OrderService(gateway).checkout(Order(100))


# ---------------------------------------------------------------- E5: pago aprobado y rechazado


def test_pago_aprobado_vip_200_cobra_170():
    # Arrange
    gateway = pasarela(True)
    order = Order(200, vip=True)
    # Act
    cobrado = OrderService(gateway).checkout(order)
    # Assert
    assert cobrado == 171
    gateway.charge.assert_called_once_with(170)
    assert order.status == "CONFIRMED"


def test_pago_rechazado_vip_200_intenta_cobrar_170_y_lanza_runtimeerror():
    gateway = pasarela(False)
    order = Order(200, vip=True)
    with pytest.raises(RuntimeError, match="payment rejected"):
        OrderService(gateway).checkout(order)
    gateway.charge.assert_called_once_with(170)


def test_timeout_de_la_pasarela_se_propaga_sin_reintentos():
    # El servicio no implementa reintentos ni circuit breaker: la excepción del proveedor llega al llamador
    # y la pasarela se invoca una sola vez.
    gateway = pasarela(error=TimeoutError("gateway timeout"))
    with pytest.raises(TimeoutError, match="gateway timeout"):
        OrderService(gateway).checkout(Order(120))
    assert gateway.charge.call_count == 1


def test_no_se_llama_a_la_pasarela_si_el_dominio_rechaza_el_total():
    gateway = pasarela(True)
    with pytest.raises(ValueError):
        OrderService(gateway).checkout(Order(0))
    gateway.charge.assert_not_called()


def test_no_se_cobra_dos_veces_un_pedido_ya_confirmado():
    gateway = pasarela(True)
    service = OrderService(gateway)
    order = Order(100)
    service.checkout(order)
    with pytest.raises(ValueError, match="already confirmed"):
        service.checkout(order)
    gateway.charge.assert_called_once_with(100)


# ---------------------------------------------------------------- E5: riesgo documentado (no corregido)


@pytest.mark.xfail(strict=True, reason="Riesgo documentado: checkout() confirma el pedido ANTES de conocer el "
                                       "resultado del pago; con el pago rechazado el pedido queda CONFIRMED.")
def test_riesgo_pedido_no_deberia_quedar_confirmado_si_el_pago_se_rechaza():
    gateway = pasarela(False)
    order = Order(200, vip=True)
    with pytest.raises(RuntimeError):
        OrderService(gateway).checkout(order)
    assert order.status != "CONFIRMED"
