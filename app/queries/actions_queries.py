from typing import Any, Optional
from uuid import UUID
from sqlalchemy.sql.expression import false
from sqlalchemy.orm import Session
from app.models.actions import Actions
from app.models.module import Module
from app.models.role_actions import Role_Actions


def get_action_by_action_name_and_module_id(db: Session, id: UUID, action_name: str):
    """Obten una accion buscandola por su module_id y su nombre.

    Args:
        db (Session): _description_
        id (UUID): _description_
        action_name (str): _description_

    Returns:
        _type_: _description_
    """
    action = (
        db.query(Actions)
        .filter(
            Actions.module_id == id,
            Actions.action_name == action_name,
        )
        .filter(Actions.is_deleted == false())
        .first()
    )
    return action


def get_all_actions_info(
    db: Session, start: Optional[int] = None, limit: Optional[int] = None
) -> Any:
    """Obten todas la info de todas las acciones.

    Args:
        db (Session): _description_
        start (Optional[int], optional): _description_. Defaults to None.
        limit (Optional[int], optional): _description_. Defaults to None.

    Returns:
        list[Any]: _description_
    """
    actions = (
        db.query(
            Actions.id,
            Actions.action_name,
            Actions.is_active,
            Actions.description,
            Actions.module_id,
            Module.name.label("module_name"),
        )
        .join(Module, isouter=True)
        .filter(Actions.is_deleted == false())
        .filter(Module.is_deleted == false())
        .offset(start)
        .limit(limit)
    )
    return actions


def get_action_and_module_info_by_id(
    db: Session, id: UUID
) -> Optional[tuple[Any, ...]]:
    """Obten la informacion de una accion por su ID.

    Args:
        db (Session): _description_
        id (UUID): _description_

    Returns:
        Optional[tuple[Any, ...]]: _description_
    """
    action = (
        db.query(
            Actions.id,
            Actions.action_name,
            Actions.is_active,
            Actions.description,
            Actions.module_id,
            Module.name.label("module_name"),
        )
        .join(Module, isouter=True)
        .filter(Actions.id == id)
        .filter(Actions.is_deleted == false())
        .filter(Module.is_deleted == false())
        .first()
    )
    return action


def get_action_info_by_id(db: Session, id: UUID):
    """Obten unicamente la info de una accion by ID.

    Args:
        db (Session): _description_
        id (UUID): _description_

    Returns:
        _type_: _description_
    """
    action = (
        db.query(Actions)
        .filter(Actions.id == id)
        .filter(Actions.is_deleted == false())
        .first()
    )
    return action


def check_actions_child_registries(db: Session, id: UUID) -> int:
    """Cuenta los registros hijos de actions.

    Args:
        db (Session): _description_
        id (UUID): _description_

    Returns:
        int: _description_
    """
    child_regestry = (
        db.query(Role_Actions)
        .filter(Role_Actions.actions_id == id)
        .filter(Role_Actions.is_deleted == false())
        .count()
    )
    return child_regestry
