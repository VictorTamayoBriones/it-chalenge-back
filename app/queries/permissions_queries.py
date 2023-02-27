from typing import Any, Optional
from uuid import UUID
from sqlalchemy.sql.expression import false, true
from sqlalchemy.orm import Session
from app.models.actions import Actions
from app.models.module import Module
from app.models.role_actions import Role_Actions
from app.models.roles import Role


def get_all_actions_modules(db: Session, id: UUID) -> list[tuple[Any, ...]]:
    """Obten un listado de acciones asociados a sus modulos buscando por el ID rol.

    Args:
        db (Session): _description_
        id (UUID): _description_

    Returns:
        list[tuple[Any, ...]]: _description_
    """
    permission = (
        db.query(
            Role_Actions.id.label("permission_id"),
            Module.name.label("module_name"),
            Actions.action_name,
        )
        .order_by(Module.name)
        .join(Role_Actions, isouter=False)
        .join(Module, isouter=False)
        .filter(Role_Actions.role_id == id.__str__())
        .filter(Role_Actions.actions_id == Actions.id.__str__())
        .filter(Actions.module_id == Module.id.__str__())
        .filter(Actions.is_active == true())
        .filter(Actions.is_deleted == false())
        .filter(Module.is_active == true())
        .filter(Module.is_deleted == false())
        .filter(Role_Actions.is_active == true())
        .filter(Role_Actions.is_deleted == false())
        .all()
    )
    return permission


def get_permissions_by_id_role_id_action(
    db: Session, id_role_user
) -> list[tuple[Any, ...]]:
    """Obten una lista de modulos con sus permisos.

    Args:
        db (Session): _description_
        id_role_user (_type_): _description_

    Returns:
        list[tuple[Any, ...]]: _description_
    """
    permissions = (
        db.query(Module.name, Actions.action_name)
        .order_by(Module.name)
        .join(Role_Actions, isouter=False)
        .join(Module, isouter=False)
        .filter(Role_Actions.role_id == id_role_user)
        .filter(Role_Actions.actions_id == Actions.id.__str__())
        .filter(Actions.module_id == Module.id.__str__())
        .filter(Actions.is_deleted == false())
        .filter(Actions.is_active == true())
        .filter(Module.is_deleted == false())
        .filter(Module.is_active == true())
        .filter(Role_Actions.is_deleted == false())
        .filter(Role_Actions.is_active == true())
        .all()
    )
    return permissions


def get_all_actions_assigned(
    db: Session,
    start: Optional[int] = None,
    limit: Optional[int] = None,
) -> Any:
    """Trae una lista de permisos.

    O si gustas entenderlo de traer una lista de acciones asigandas.

    Args:
        db (Session): _description_
        start (Optional[int], optional): _description_. Defaults to None.
        limit (Optional[int], optional): _description_. Defaults to None.

    Returns:
        list[tuple[Any, ...]]: _description_
    """
    actions = (
        db.query(
            Role_Actions.id,
            Role_Actions.actions_id,
            Role_Actions.is_active,
            Actions.action_name.label("action_name"),
            Role_Actions.role_id,
            Role.name.label("role_name"),
            Role_Actions.description,
        )
        .join(Role, Actions, isouter=True)
        .filter(Role_Actions.is_deleted == false())
        .offset(start)
        .limit(limit)
    )
    return actions


def get_one_role_action_by_id_with_action_info(
    db: Session, id: UUID
) -> Optional[tuple[Any, ...]]:
    """Elige un permiso por su ID.

    Args:
        db (Session): _description_
        id (UUID): _description_

    Returns:
        Optional[tuple[Any, ...]]: _description_
    """
    action = (
        db.query(
            Role_Actions.id,
            Role_Actions.actions_id,
            Role_Actions.is_active,
            Actions.action_name.label("action_name"),
            Role_Actions.role_id,
            Role.name.label("role_name"),
            Role_Actions.description,
        )
        .join(Role, Actions, isouter=True)
        .filter(Role_Actions.id == id)
        .filter(Role_Actions.is_deleted == false())
        .first()
    )
    return action


def get_one_role_action_by_role_id_action_id(
    db: Session, role_id: UUID, action_id: UUID
) -> Any:
    """Obten un permiso buscandolo por su role id y action id.

    Args:
        db (Session): _description_
        role_id (UUID): _description_
        action_id (UUID): _description_

    Returns:
        Query[Any]: Regreso un query parcial el cual puede ser empleado para
         mas comparaciones o agregar mas filtros de busquedas.
    """
    role_action = (
        db.query(Role_Actions)
        .filter(Role_Actions.role_id == role_id)
        .filter(Role_Actions.actions_id == action_id)
    )
    return role_action


def delete_one_role_action_by_id(db: Session, id: UUID) -> Any:
    """Query que sirve para filtar y ejecutar metodo delete o update.

    Args:
        db (Session): _description_
        id (UUID): _description_

    Returns:
        Query[Any]: _description_
    """
    permission = (
        db.query(Role_Actions)
        .filter(Role_Actions.id == id)
        .filter(Role_Actions.is_deleted == false())
    )
    return permission


def get_one_role_action_by_id(db: Session, id: UUID) -> Optional[Any]:
    """Busca un permiso por su id.

    Args:
        db (Session): _description_
        id (UUID): _description_

    Returns:
        Query[Any]: _description_
    """
    permission = (
        db.query(Role_Actions)
        .filter(Role_Actions.id == id)
        .filter(Role_Actions.is_deleted == false())
        .first()
    )
    return permission
