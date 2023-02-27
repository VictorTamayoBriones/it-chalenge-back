from typing import Any, Optional
from uuid import UUID
from sqlalchemy import collate
from sqlalchemy.sql.expression import false
from sqlalchemy.orm import Session
from app.models.users import Users
from app.models.roles import Role


def get_role_exist(db: Session, request: UUID) -> Optional[tuple[Any]]:
    """Verifica si un rol existe en la bd.

    Args:
        db (Session): Session para realizar acciones con SQLALCHEMY.
        request (UUID): Identificador unico del objeto a buscar.

    Returns:
        Optional[tuple[Any]]: Informacion en lista de multiples objetos.
    """
    check_role = (
        db.query(Role)
        .filter(Role.id == request)
        .filter(Role.is_deleted == false())
        .first()
    )
    return check_role


def get_role_by_name(db: Session, request: Optional[str]) -> Optional[Any]:
    """Obten a un role por su nombre.

    Args:
        db (Session): Session para realizar acciones con SQLALCHEMY.
        request (str): Se pide una cadena de texto.

    Returns:
        Optional[Any]: Informacion de un objeto.
    """
    role = (
        db.query(Role)
        .filter(collate(Role.name, "utf8mb4_bin") == request)
        .filter(Role.is_deleted == false())
        .first()
    )
    return role


def get_all_roles_info(
    db: Session,
    start: Optional[int] = None,
    limit: Optional[int] = None,
) -> Any:
    """Obten todos los roles.

    Args:
        db (Session): Session para realizar acciones con SQLALCHEMY.
        start (Optional[int], optional):Este argumento sirve para
            indicar el inicio de nuestro paginador. Defaults to None.
        limit (Optional[int], optional): Este argumento sirve para
            indicar el limite de nuestro paginador. Defaults to None.

    Returns:
        Query[Any]: Se devuelve parte del query el cual se pueden agregar mas metodos
         de SQLAlchemy que sean compatibles con este tipo de query.
    """
    roles = (
        db.query(Role)
        .order_by(Role.name)
        .filter(Role.name != "super admin")
        .filter_by(is_deleted=False)
        .offset(start)
        .limit(limit)
    )
    return roles


def get_role_by_id(db: Session, id: UUID) -> Optional[Any]:
    """Obten un role por su ID.

    Args:
        db (Session): Session para realizar acciones con SQLALCHEMY.
        id (UUID): Identificador unico del objeto a buscar.

    Returns:
        Optional[Any]: _description_
    """
    show_role = (
        db.query(Role)
        .filter(Role.name != "super admin")
        .filter(Role.id == id)
        .filter_by(is_deleted=false())
        .first()
    )
    return show_role


def count_childs_registries(db: Session, id: UUID) -> int:
    """Cuenta registros asociados a la tabla users.

    Args:
        db (Session): Session para realizar acciones con SQLALCHEMY.
        id (UUID): Identificador unico del objeto a buscar.

    Returns:
        int: Regras el numero de regsitros encontrados.
    """
    count_registries = (
        db.query(Users)
        .filter(Users.role_id == id)
        .filter(Users.is_deleted == false())
        .count()
    )
    return count_registries


def get_role_with_users(
    db: Session,
    id: UUID,
    start: Optional[int] = None,
    limit: Optional[int] = None,
) -> Any:
    """Obten todos los usuarios asociados a un rol.

    Args:
        db (Session): Session para realizar acciones con SQLALCHEMY.
        id (UUID): Identificador unico del objeto a buscar.
        start (Optional[int], optional):Este argumento sirve para
            indicar el inicio de nuestro paginador. Defaults to None.
        limit (Optional[int], optional): Este argumento sirve para
            indicar el limite de nuestro paginador. Defaults to None.

    Returns:
        list[tuple[Any, ...]]: Devuelve una lista de objetos.
    """
    role_with_users = (
        db.query(
            Role.id,
            Role.name,
            Role.description,
            Role.is_active,
            Users.id.label("user_id"),
            Users.email.label("user_email"),
            Users.is_active.label("user_is_active"),
        )
        .join(Role, isouter=True)
        .filter(Role.id == id)
        .filter(Users.is_deleted == false())
        .filter(Role.is_deleted == false())
        .offset(start)
        .limit(limit)
    )
    return role_with_users


def get_all_roles_searching_by_name(
    db: Session,
    role_name: str,
    start: Optional[int] = None,
    limit: Optional[int] = None,
) -> Any:
    """Busca y obten elementos por su nombre.

    Args:
        db (Session): Session para realizar acciones con SQLALCHEMY.
        role_name (str): Se pide una cadena de texto.
        start (Optional[int], optional):Este argumento sirve para
            indicar el inicio de nuestro paginador. Defaults to None.
        limit (Optional[int], optional): Este argumento sirve para
            indicar el limite de nuestro paginador. Defaults to None.

    Returns:
        Query[Any]: Se devuelve parte del query el cual se pueden agregar mas metodos
         de SQLAlchemy que sean compatibles con este tipo de query.
    """
    search = (
        db.query(Role.id, Role.name, Role.description, Role.is_active)
        .filter(Role.name.ilike("%" + role_name + "%"))
        .filter(Role.name != "super admin")
        .filter(Role.is_deleted == false())
        .offset(start)
        .limit(limit)
    )
    return search
