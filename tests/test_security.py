"""Pruebas de autorización de can_cancel() con fechas FIJAS: `now` se pasa explícitamente, así que los resultados no
dependen del reloj del equipo. Política implementada (src/security.py):
1) SHIPPED nunca se cancela, ni por un administrador; 2) en otro estado, el administrador puede cancelar;
3) el propietario no administrador solo puede cancelar si han pasado MENOS de 24 horas (a las 24 h exactas ya no)."""
from datetime import datetime, timedelta, timezone

import pytest

from src import security
from src.security import can_cancel

CREADO = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)
PROPIETARIO, OTRO = 1, 2


# ---------------------------------------------------------------- pruebas originales, ahora con fechas fijas


def test_owner_within_24h():
    assert can_cancel("NEW", PROPIETARIO, PROPIETARIO, False, CREADO, CREADO + timedelta(hours=1))


def test_stranger_denied():
    assert not can_cancel("NEW", PROPIETARIO, OTRO, False, CREADO, CREADO)


def test_shipped_denied_even_admin():
    assert not can_cancel("SHIPPED", PROPIETARIO, PROPIETARIO, True, CREADO, CREADO)


def test_expired_denied():
    assert not can_cancel("NEW", PROPIETARIO, PROPIETARIO, False, CREADO, CREADO + timedelta(hours=25))


# ---------------------------------------------------------------- E6: casos solicitados


def test_admin_cancela_pedido_new_de_otro_usuario():
    assert can_cancel("NEW", owner_id=PROPIETARIO, user_id=99, is_admin=True,
                      created_at=CREADO, now=CREADO + timedelta(days=30))


def test_propietario_exactamente_a_las_24_horas_se_rechaza():
    assert not can_cancel("NEW", PROPIETARIO, PROPIETARIO, False, CREADO, CREADO + timedelta(hours=24))


def test_propietario_un_segundo_antes_de_24_horas_se_permite():
    assert can_cancel("NEW", PROPIETARIO, PROPIETARIO, False, CREADO, CREADO + timedelta(hours=24, seconds=-1))


def test_pedido_enviado_no_lo_cancela_ni_el_propietario_dentro_de_plazo():
    assert not can_cancel("SHIPPED", PROPIETARIO, PROPIETARIO, False, CREADO, CREADO + timedelta(minutes=5))


def test_tercero_no_administrador_tampoco_dentro_de_24h():
    assert not can_cancel("CONFIRMED", PROPIETARIO, OTRO, False, CREADO, CREADO + timedelta(minutes=5))


# ---------------------------------------------------------------- E6: matriz de autorización completa

MATRIZ = [
    # id,        rol,              estado,      usuario,      antigüedad,                       esperado
    ("SEG-01", "administrador", "NEW", 99, timedelta(days=30), True),
    ("SEG-02", "administrador", "CONFIRMED", 99, timedelta(hours=1), True),
    ("SEG-03", "administrador", "SHIPPED", 99, timedelta(hours=1), False),
    ("SEG-04", "propietario", "NEW", PROPIETARIO, timedelta(hours=1), True),
    ("SEG-05", "propietario", "CONFIRMED", PROPIETARIO, timedelta(hours=23, minutes=59, seconds=59), True),
    ("SEG-06", "propietario", "NEW", PROPIETARIO, timedelta(hours=24), False),
    ("SEG-07", "propietario", "NEW", PROPIETARIO, timedelta(hours=25), False),
    ("SEG-08", "propietario", "SHIPPED", PROPIETARIO, timedelta(minutes=5), False),
    ("SEG-09", "tercero", "NEW", OTRO, timedelta(minutes=5), False),
    ("SEG-10", "tercero", "CONFIRMED", OTRO, timedelta(hours=30), False),
]


@pytest.mark.parametrize("caso, rol, estado, usuario, antiguedad, esperado", MATRIZ, ids=[m[0] for m in MATRIZ])
def test_matriz_autorizacion(caso, rol, estado, usuario, antiguedad, esperado):
    es_admin = rol == "administrador"
    resultado = can_cancel(estado, PROPIETARIO, usuario, es_admin, CREADO, CREADO + antiguedad)
    assert resultado is esperado


# ---------------------------------------------------------------- valor por defecto de `now` sin depender del reloj real


class _RelojFijo(datetime):
    @classmethod
    def now(cls, tz=None):
        return CREADO + timedelta(hours=2)


def test_sin_now_usa_la_hora_actual_del_modulo(monkeypatch):
    monkeypatch.setattr(security, "datetime", _RelojFijo)
    assert can_cancel("NEW", PROPIETARIO, PROPIETARIO, False, CREADO)
    monkeypatch.setattr(_RelojFijo, "now", classmethod(lambda cls, tz=None: CREADO + timedelta(hours=24)))
    assert not can_cancel("NEW", PROPIETARIO, PROPIETARIO, False, CREADO)
