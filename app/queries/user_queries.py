from typing import Any, Optional
from uuid import UUID
from sqlalchemy.sql.expression import false, true
from sqlalchemy.orm import Session
from app.models.users import Users
from app.models.roles import Role


def get_current_user_info(db: Session, current_user: Any) -> Optional[tuple[Any, ...]]:
    """Verificar la info del usuario en Sesion.

    Args:
        db (Session):ession para realizar acciones con SQLALCHEMY. Defaults to Depends().
        current_user (str): Este argumento es el ID del usuario el cual es un GUID
            se obtiene con la clase Authorize y el metodo get_jwt_subject()

    Returns:
        Optional[tuple[Any, ...]]: Nos regresara Una tupla con la informacion del usuario.
    """
    user = (
        db.query(
            Users.id,
            Users.email,
            Users.role_id,
            Users.is_active,
            Users.password,
            Users.is_deleted,
            Users.role_id,
            Role.name.label("role_name"),
        )
        .join(Role, isouter=True)
        .filter(Users.id == current_user)
        .filter(Users.is_deleted == false())
        .filter(Users.is_active == true())
        .filter(Role.is_deleted == false())
        .first()
    )
    return user


def get_user_by_email(db: Session, request: Optional[str]) -> Optional[Any]:
    """Busca a un usuario por su email.

    Args:
        db (Session): _description_
        request (Optional[str]): _description_

    Returns:
        Optional[Any]: _description_
    """
    user = (
        db.query(Users)
        .filter(Users.email == request)
        .join(Role, isouter=True)
        .filter(Role.name != "super admin")
        .filter(Users.is_deleted == false())
        .first()
    )
    return user


def get_all_users_except_root_role_current_user(
    db: Session,
    current_user: str,
    start: Optional[int] = None,
    limit: Optional[int] = None,
) -> Any:
    """Regresa a todos los users excepto al current_user y al rol maximo.

    Args:
        db (Session): _description_
        current_user (str): _description_
        start (Optional[int], optional): _description_. Defaults to None.
        limit (Optional[int], optional): _description_. Defaults to None.

    Returns:
        list[tuple[Any, ...]]: _description_
    """
    show_all_users = (
        db.query(
            Users.id,
            Users.email,
            Users.is_active,
            Users.role_id,
            Role.name.label("role_name"),
        )
        .join(Role, isouter=True)
        .filter(Role.name != "super admin")
        .filter(Users.id != current_user)
        .filter(Users.is_deleted == false())
        .filter(Role.is_deleted == false())
        .offset(start)
        .limit(limit)
    )
    return show_all_users


def get_one_user_with_role_info_by_id(
    db: Session, id: UUID
) -> Optional[tuple[Any, ...]]:
    """Obten a un usuario con su rol por su ID.

    Args:
        db (Session): _description_
        id (UUID): _description_

    Returns:
        Optional[tuple[Any, ...]]: _description_
    """
    find_user = (
        db.query(
            Users.id,
            Users.email,
            Users.is_active,
            Users.role_id,
            Role.name.label("role_name"),
        )
        .join(Role, isouter=True)
        .filter(Users.id == id)
        .filter(Role.name != "super admin")
        .filter(Users.is_deleted == false())
        .filter(Role.is_deleted == false())
        .first()
    )
    return find_user


def get_one_user_info_by_id(db: Session, id: Optional[str]) -> Optional[Any]:
    """Obten la info de usuario usando su ID.

    Args:
        db (Session): _description_
        id (Optional[str]): _description_

    Returns:
        Optional[Any]: _description_
    """
    find_user_info = (
        db.query(Users).filter(Users.id == id).filter_by(is_deleted=False).first()
    )
    return find_user_info


def get_user_info_by_email(db: Session, email: str) -> Optional[tuple[Any, ...]]:
    """Obten la info de un usuario by email.

    Args:
        db (Session): _description_
        email (str): _description_

    Returns:
        Optional[tuple[Any, ...]]: _description_
    """
    find_user = (
        db.query(
            Users.id,
            Users.email,
            Users.role_id,
            Users.is_active,
            Users.password,
            Users.is_deleted,
            Role.name.label("role_name"),
        )
        .join(Role)
        .filter(Users.email == email)
        .filter(Users.is_active == true())
        .filter(Users.is_deleted == false())
        .first()
    )
    return find_user


def get_all_users_searching_by_name(
    db: Session,
    email: str,
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
        db.query(
            Users.id,
            Users.email,
            Users.is_active,
            Users.role_id,
            Role.name.label("role_name"),
        )
        .join(Role, isouter=True)
        .filter(Users.email.ilike("%" + email + "%"))
        .filter(Role.name != "super admin")
        .filter(Users.is_deleted == false())
        .filter(Role.is_deleted == false())
        .offset(start)
        .limit(limit)
    )
    return search
