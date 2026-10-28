"""Pruebas de integración del repositorio SQLAlchemy con SQLite EN MEMORIA (no se usa ninguna base de datos real).

Cada prueba recibe un motor nuevo; al terminar se cierra la sesión y se libera el motor (engine.dispose()), de modo que
ninguna conexión queda abierta entre pruebas."""
import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.domain import Order
from src.repository import OrderRow, SqlOrderRepository, make_engine


@pytest.fixture
def engine():
    engine = make_engine()
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session


# ---------------------------------------------------------------- pruebas originales (con limpieza de recursos)


def test_repository_commit(session):
    SqlOrderRepository(session).save(1, Order(120))
    session.commit()
    assert session.scalar(select(OrderRow).where(OrderRow.id == 1)).total == 120


def test_repository_rollback(session):
    SqlOrderRepository(session).save(1, Order(120))
    session.rollback()
    assert session.scalar(select(OrderRow).where(OrderRow.id == 1)) is None


# ---------------------------------------------------------------- E4: guardado, commit y lectura


def test_guardar_pedido_id_2_total_250_commit_y_leer_en_sesion_nueva(engine):
    # Arrange + Act: se guarda y confirma en una sesión
    with Session(engine) as escritura:
        SqlOrderRepository(escritura).save(2, Order(250))
        escritura.commit()
    # Assert: otra sesión (sin el mapa de identidad de la primera) encuentra el registro
    with Session(engine) as lectura:
        fila = lectura.get(OrderRow, 2)
        assert fila is not None
        assert fila.id == 2
        assert fila.total == 250
        assert fila.status == "NEW"


def test_persiste_el_estado_confirmado_y_el_importe_original(engine):
    order = Order(200, vip=True)
    order.confirm()
    with Session(engine) as s:
        SqlOrderRepository(s).save(6, order)
        s.commit()
    with Session(engine) as s:
        fila = s.get(OrderRow, 6)
        assert (fila.total, fila.status) == (200, "CONFIRMED")


def test_rollback_deshace_solo_lo_no_confirmado(engine):
    with Session(engine) as s:
        repo = SqlOrderRepository(s)
        repo.save(1, Order(120))
        s.commit()                      # el pedido 1 queda confirmado en la base
        repo.save(2, Order(250))
        s.flush()                       # el INSERT del pedido 2 ya se envió, pero la transacción sigue abierta
        assert s.scalar(select(func.count()).select_from(OrderRow)) == 2
        s.rollback()                    # se descarta el pedido 2
    with Session(engine) as s:
        ids = s.scalars(select(OrderRow.id).order_by(OrderRow.id)).all()
        assert ids == [1]


def test_sin_commit_el_registro_no_persiste_al_cerrar_la_sesion(engine):
    with Session(engine) as s:
        SqlOrderRepository(s).save(3, Order(150))
        s.flush()
        # se cierra la sesión sin commit: SQLAlchemy revierte la transacción pendiente
    with Session(engine) as s:
        assert s.get(OrderRow, 3) is None


# ---------------------------------------------------------------- E4: restricciones de integridad


def test_restriccion_unicidad_id_duplicado(engine):
    with Session(engine) as s:
        SqlOrderRepository(s).save(1, Order(120))
        s.commit()
    with Session(engine) as s:
        SqlOrderRepository(s).save(1, Order(999))
        with pytest.raises(IntegrityError):
            s.commit()
        s.rollback()
    with Session(engine) as s:
        assert s.get(OrderRow, 1).total == 120          # el registro original no se sobrescribió


def test_restriccion_total_no_nulo(session):
    SqlOrderRepository(session).save(4, Order(None))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
    assert session.get(OrderRow, 4) is None
