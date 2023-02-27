from typing import Any, Optional
from uuid import UUID
from sqlalchemy.sql.expression import false
from sqlalchemy.orm import Session
from app.models.actions import Actions
from app.models.module import Module


def get_module_by_name(db: Session, name: Optional[str]):
    """Obten un modulo por su nombre.

    Args:
        db (Session): _description_
        name (Optional[str]): _description_

    Returns:
        _type_: _description_
    """
    module = (
        db.query(Module)
        .filter(Module.name == name)
        .filter(Module.is_deleted == false())
        .first()
    )
    return module


def get_all_modules_info(
    db: Session, start: Optional[int] = None, limit: Optional[int] = None
) -> Any:
    """Obten todos los modulos.

    Args:
        db (Session): _description_
        start (Optional[int], optional): _description_. Defaults to None.
        limit (Optional[int], optional): _description_. Defaults to None.

    Returns:
        list[Any]: _description_
    """
    modules = db.query(Module).filter_by(is_deleted=False).offset(start).limit(limit)
    return modules


def get_one_module_info(db: Session, id: UUID):
    """Obten un modulo by id.

    Args:
        db (Session): _description_
        id (UUID): _description_

    Returns:
        _type_: _description_
    """
    module = (
        db.query(Module).filter(Module.id == id).filter_by(is_deleted=False).first()
    )
    return module


def count_child_module_registries(db: Session, id: UUID) -> int:
    """Cuenta cuantos registros hijos tiene modulos.

    Args:
        db (Session): _description_
        id (UUID): _description_

    Returns:
        int: _description_
    """
    actions = (
        db.query(Actions)
        .filter(Actions.module_id == id)
        .filter(Actions.is_deleted == false())
        .count()
    )
    return actions


def get_modules_with_actions_by_id(
    db: Session,
    id: UUID,
    start: Optional[int] = None,
    limit: Optional[int] = None,
) -> Any:
    """Obten modulos con acciones por su ID.

    Args:
        db (Session): _description_
        id (UUID): _description_
        start (Optional[int], optional): _description_. Defaults to None.
        limit (Optional[int], optional): _description_. Defaults to None.

    Returns:
        list[tuple[Any, ...]]: _description_
    """
    modules_acctions = (
        db.query(
            Module.id,
            Module.name,
            Module.description,
            Module.is_active,
            Actions.id.label("action_id"),
            Actions.action_name.label("action_name"),
            Actions.is_active.label("action_is_active"),
        )
        .join(Module, isouter=True)
        .filter(Module.id == id)
        .filter(Actions.is_deleted == false())
        .filter(Module.is_deleted == false())
        .offset(start)
        .limit(limit)
    )
    return modules_acctions
