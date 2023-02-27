from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.sql.expression import false, true
from sqlalchemy.orm import Session
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app import main
from app.queries.permissions_queries import (
    delete_one_role_action_by_id,
    get_all_actions_assigned,
    get_one_role_action_by_id,
    get_one_role_action_by_id_with_action_info,
)
from app.models.actions import Actions
from app.models.role_actions import Role_Actions
from app.models.roles import Role
from app.schemas import role_actions_schemas
from app.utilities.verify_request_value import check_request_value

extra = {"event.category": "app_log"}


class RoleActions:
    """Esta clase realiza operacions en RoleActions o Permisos.

    Podemos crear, actualizar ,eliminar y editar ademas de
     generar otras acciones adiciionales.
    """

    def __init__(
        self,
        db: Optional[Session] = None,
        request: Optional[role_actions_schemas.ShowRoleAction] = None,
        current_user: Optional[str] = None,
        start: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> None:
        self.db: Optional[Session] = db
        self.request: Optional[role_actions_schemas.ShowRoleAction] = request
        self.current_user: Optional[str] = current_user
        self.start: Optional[int] = start
        self.limit: Optional[int] = limit

    def show_all_actions_assigned(
        self,
        db: Session,
        start: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> JSONResponse:
        """Este metodo cuenta todos los registros y paginar el listado de la informacion.

        #? ENDPOINT /role-actions/ GET

        Args:
            db (Session): Session para realizar acciones con SQLALCHEMY. Defaults to Depends().
            start (int, optional): Este argumento sirve para
            indicar el inicio de nuestro paginador. Defaults to None.
            limit (int, optional): Este argumento sirve para
            indicar el limite de nuestro paginador. Defaults to None.

        Returns:
            JSONResponse:Nos devuelve una respuesta en JSON con la propiedad success
            en caso de tener exito nos mostarara la propiedad numRows con la cantidad de todos
            los registros y data con la informacion solicitada.

        """
        show_actions = get_all_actions_assigned(db, start, limit)

        total = get_all_actions_assigned(db, start=None, limit=None)
        main.logger.info(msg="List of Permissions is display!", extra=extra)

        res = {"success": True, "numRows": total.count(), "data": show_actions.all()}

        return jsonable_encoder(res)

    def show_one_role_action(self, db: Session, id: UUID) -> JSONResponse:
        """Este metodo lo que hace es realizar la busqueda de un registro por su id.

        #? ENDPOINT /role-actions/{id}

        Args:
            db (Session): Session para realizar acciones con SQLALCHEMY. Defaults to Depends().
            id (UUID v4): Este argumento es del tipo UUID v4 si se ingresa algo que
            no se encuentre en este formato sera invalido.

        Returns:
            JSONResponse: Nos devuelve una respuesta en JSON con la propiedad success
             en caso de tener exito nos mostarara la propiedad data
             con la informacion del usuario buscado.
        """
        show_action = get_one_role_action_by_id_with_action_info(db, id)

        if not show_action:
            main.logger.info(msg=f"Permission {id} not found!", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": True, "msg": "Not Found"},
            )

        res = {"success": True, "data": show_action}
        main.logger.info(msg=f"Permission {id} is found!", extra=extra)
        return jsonable_encoder(res)

    def assing_role_and_actions(
        self,
        db: Session,
        request: role_actions_schemas.assigned_action,
        current_user: str,
    ) -> JSONResponse:
        """Asignar una accion a un rol.

        Esta funcion lo que hace es asignar acciones a un rol

        #? ENPOINT /role-actions/assing/actions

        Args:
            request (role_actions_schemas.assigned_action):Schema con ID rol y ID action
            db (Session): Session para realizar acciones con SQLALCHEMY. Defaults to Depends().

        Returns:
            JSONResponse: Nos devuelve una respuesta en JSON con la propiedad success
             y la propiedad msg con sus respectivos valores.
             En caso contrario nos mostrara la propiedad success y la propiedad msg.
        """
        check_status = (
            db.query(Role_Actions)
            .filter(Role_Actions.role_id == request.role_id)
            .filter(Role_Actions.actions_id == request.actions_id)
        )
        if check_status.filter(Role_Actions.is_deleted == false()).first():
            main.logger.info(msg="Permission already exist!", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": True, "msg": "¡El permiso ya estaba asignado!"},
            )

        if check_status.filter(Role_Actions.is_deleted == true()).first():
            is_d = False
            check_status.update(
                {**request.dict(), "is_deleted": is_d, "updated_by": current_user}
            )
            db.commit()
            main.logger.info(msg="Permission created Successfully!", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"success": True, "msg": "¡Se a asignado un permiso!"},
            )

        else:
            check_role = (
                db.query(Role)
                .filter(Role.id == request.role_id)
                .filter(Role.is_deleted == false())
                .first()
            )
            if not check_role:
                main.logger.info(msg=f"Role {request.role_id} not found!", extra=extra)
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"success": False, "msg": "¡Rol inválido!"},
                )

            check_action = (
                db.query(Actions)
                .filter(Actions.id == request.actions_id)
                .filter(Actions.is_deleted == false())
                .first()
            )

            if not check_action:
                main.logger.info(
                    msg=f"Action {request.actions_id} not found!", extra=extra
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"success": False, "msg": "Acción inválida!"},
                )
            assing_action = Role_Actions(**request.dict(), created_by=current_user)
            db.add(assing_action)
            db.commit()
            main.logger.info(msg="Permission created successfully!", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"success": True, "msg": "¡Se a asignado un permiso!"},
            )

    def deleted_assing_role_and_actions(
        self, db: Session, id: UUID, current_user: str
    ) -> Optional[JSONResponse]:
        """Este metodo lo que hace es eliminar un registro (soft-deleted).

        Filtrandolo por su id en formato GUID V4

        #? ENDPOINT /role-actions/{id} DELETED

        Args:
            db (Session): Session para realizar acciones con SQLALCHEMY.
            Defaults to Depends().
            id (UUID v4): Este argumento es del tipo UUID v4 si se ingresa
            algo que no se encuentre en este formato sera invalido.
            current_user (str): Este argumento es el ID del usuario el cual
            es un GUID se obtiene con la clase Authorize y el metodo get_jwt_subject()

        Returns:
            Optional[JSONResponse]:status code 204 NO CONTENT para usar el método DELETE
             es necesario regresas NONE en caso de algun erro devolvemos un JSONRESPONSE.
        """
        role_action = delete_one_role_action_by_id(db, id)
        if not role_action.first():
            main.logger.info(msg=f"Permission {id} not found", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": True, "msg": "Not Found"},
            )

        role_action.update(
            {"is_deleted": True, "updated_by": current_user, "is_active": False}
        )
        main.logger.info(msg=f"Permission {id} it's deleted!", extra=extra)
        db.commit()
        return None

    def update_permission(
        self,
        db: Session,
        id: UUID,
        request: role_actions_schemas.update_assigned_action_desc,
        current_user: str,
    ) -> JSONResponse:
        """Este metodo realiza la actualizacion de datos sobre un registro.

        Filtrado por su id, se pide el current_user para tener llenados la informacion
        para los datos de auditoria.

        #? ENDPOINT /permissions/{id} PUT

        Args:
            db (Session): Session para realizar acciones con SQLALCHEMY.
            Defaults to Depends().
            id (UUID v4): Este argumento es del tipo UUID v4 si se ingresa
            algo que no se encuentre en este formato sera invalido.
            request (Pydantic model): Modelo de pydantic para recibir la
            informacion proporcionada por el frontend o el usuario.
            current_user (str): Este argumento es el ID del usuario el cual
            es un GUID se obtiene  con la clase Authorize y el metodo get_jwt_subject()

        Returns:
            JSONResponse: Nos devuelve una respuesta en JSON con la propiedad success
            y la propiedad msg con sus respectivos valores. En caso contrario nos mostrara
            la propiedad success y la propiedad msg.
        """
        #  Buscamos a un user por su id, este no debe de estar marcado como eliminado
        role_action = get_one_role_action_by_id(db, id)
        #  Si no existe el user, devolvemos un error
        if not role_action:
            main.logger.info(msg=f"Permission {id} not found!", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "msg": "Not Found"},
            )
        # print(request.description)
        # print(role_action)

        role_action.description = check_request_value(
            request.description, role_action.description
        )
        role_action.is_active = check_request_value(
            request.is_active, role_action.is_active
        )
        role_action.updated_by = current_user
        role_action.updated_on = datetime.now()
        # print(role_action)
        # print(request.description)

        db.add(role_action)
        db.commit()
        main.logger.info(msg="Permission Updated successfully!", extra=extra)
        return JSONResponse(
            status_code=202,
            content={
                "success": True,
                "msg": "Updated successfully",
            },
        )
