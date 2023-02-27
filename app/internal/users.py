from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app import main
from app.schemas import user_schemas
from app.utilities.hashing import Hash
from app.queries.user_queries import (
    get_all_users_searching_by_name,
    get_current_user_info,
)
from app.queries.user_queries import get_user_by_email
from app.queries.user_queries import get_all_users_except_root_role_current_user
from app.queries.user_queries import get_one_user_with_role_info_by_id
from app.queries.user_queries import get_one_user_info_by_id
from app.queries.rol_queries import get_role_exist
from app.utilities.verify_request_value import check_request_value
from app.models.users import Users

extra = {"event.category": "app_log"}


class UsersActions:
    """Esta clase realiza operacions en usuarios.

    Podemos crear, actualizar ,eliminar y editar ademas de
     generar otras acciones adiciionales.
    """

    def __init__(
        self,
        db: Optional[Session] = None,
        request: Optional[user_schemas.UserCreate] = None,
        current_user: Optional[str] = None,
        start: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> None:
        self.db: Optional[Session] = db
        self.request: Optional[user_schemas.UserCreate] = request
        self.current_user: Optional[str] = current_user
        self.start: Optional[int] = start
        self.limit: Optional[int] = limit

    def current_user_profile(self, db: Session, current_user: str) -> JSONResponse:
        """Este metodo lo que hace es mostrar la informacion del usuario en session.

        #? Endpoint /users/profile GET
        Args:
            db (Session): Session para realizar acciones con SQLALCHEMY. Defaults to Depends().
            current_user (str): Este argumento es el ID del usuario el cual es un GUID
            se obtiene con la clase Authorize y el metodo get_jwt_subject()

        Returns:
            JSONResponse:  Nos devuelve una respuesta en JSON con la propiedad success
                en caso de tener exito nos mostarara la propiedad data con la informacion del
                usuario en session. En caso contrario nos mostrara la propiedad success y
                la propiedad msg.
        """
        #  We need to validate if the user and the role exist
        user = get_current_user_info(db, current_user)
        res = {"success": True, "data": user}
        return jsonable_encoder(res)

    def create_new_user(
        self, db: Session, current_user: str, request: user_schemas.UserCreate
    ) -> JSONResponse:
        """Este metodo lo que hace es crear un usuario.

        Se pide el current_user para tener llenados la informacion para los datos de auditoria.

        #? Endpoint /users/create POST

        Args:
            db (Session): Session para realizar acciones con SQLALCHEMY. Defaults to Depends().
            current_user (str): Este argumento es el ID del usuario el cual es un GUID
             se obtiene con la clase Authorize y el metodo get_jwt_subject()
            request (Pydantic model): Modelo de pydantic para recibir la informacion proporcionada
             por el frontend o el usuario.

        Returns:
            JSONResponse: Nos devuelve una respuesta en JSON con la propiedad success
             y la propiedad msg con sus respectivos valores.
             En caso contrario nos mostrara la propiedad success y la propiedad msg.
        """
        new_user = get_user_by_email(db, request.email)
        check_role = get_role_exist(db, request.role_id)
        if not check_role:
            main.logger.info(msg="Invalid role!", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "msg": "Invalid role!"},
            )
        if new_user is not None and new_user.is_deleted is False:
            # If the user is not deleted, we can not create it.
            # print("If the user is not deleted, we can not create it.")
            main.logger.info(msg="User already exists!", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"success": True, "msg": "User already exists!"},
            )

        new_user = Users(
            email=request.email.strip(),
            password=Hash().bcrypt(request.password),
            role_id=request.role_id,
            created_on=datetime.now(),
            created_by=current_user,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        main.logger.info(msg="User created succesfully!", extra=extra)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"success": True, "msg": "User created succesfully!"},
        )

    def get_all_users(
        self,
        db: Session,
        current_user: str,
        start: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> JSONResponse:
        """Este metodo cuenta todos los registros y paginar el listado de la informacion.

        #? ENDPOINT /users/ GET

        Args:
            db (Session): Session para realizar acciones con SQLALCHEMY. Defaults to Depends().
            start (int, optional): Este argumento sirve para
            indicar el inicio de nuestro paginador. Defaults to None.
            limit (int, optional): Este argumento sirve para
            indicar el limite de nuestro paginador. Defaults to None.

        Returns:
            JSONResponse: Nos devuelve una respuesta en JSON con la propiedad success
                en caso de tener exito nos mostarara la propiedad numRows con la cantidad de todos
                los registros y data con la informacion solicitada.
        """
        show_users = get_all_users_except_root_role_current_user(
            db, current_user, start, limit
        )

        total = get_all_users_except_root_role_current_user(
            db, current_user, start=None, limit=None
        )
        main.logger.info(msg="List of Users is display!", extra=extra)
        res = {"success": True, "numRows": total.count(), "data": show_users.all()}
        return jsonable_encoder(res)

    def get_one_user(self, db: Session, id: UUID) -> JSONResponse:
        """Realizar la busqueda de un registro por su id.

        #? ENDPOINT /users/{id} GET

        Args:
            db (Session): Session para realizar acciones con SQLALCHEMY. Defaults to Depends().
            id (UUID v4): Este argumento es del tipo UUID v4 si se ingresa algo que
            no se encuentre en este formato sera invalido.

        Returns:
            JSONResponse: Nos devuelve una respuesta en JSON con la propiedad success en
             caso de tener exito nos mostarara la propiedad data con la informacion del usuario.
        """
        user = get_one_user_with_role_info_by_id(db, id)
        if not user:
            main.logger.info(msg=f"User {id} not found!", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "msg": "Not Found"},
            )

        res = {"success": True, "data": user}
        main.logger.info(msg=f"User {id} is found!", extra=extra)
        return jsonable_encoder(res)

    def search_roles(
        self,
        db: Session,
        email: str,
        start: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict[str, Any]:
        """Busca elementos por sus nombres.

        Lista y cuenta los registros que tengan parecido al string que le has pasado.

        #? ENDPOINT /users/search/{role_name} GET

        Args:
            db (Session): Session para realizar acciones con SQLALCHEMY. Defaults to Depends().
            role_name (str): string para realiza la busqueda.
            start (Optional[int]): Este argumento sirve para indicar el inicio de nuestro paginador.
             Defaults to None.
            limit (Optional[int]): Este argumento sirve para indicar el limite de nuestro paginador.
             Defaults to None.

        Returns:
            JSONResponse: Nos devuelve una respuesta en JSON con la propiedad success en caso
             de tener exito nos mostarara la propiedad data con la informacion solicitada.
        """
        print(email)
        search = get_all_users_searching_by_name(db, email, start, limit)
        # count_search = get_all_roles_info(db, start=None, limit=None)
        count_search = get_all_users_searching_by_name(
            db, email, start=None, limit=None
        )
        main.logger.info(msg="List of Roles is display!", extra=extra)
        res = {"success": True, "numRows": count_search.count(), "data": search.all()}

        return res

    def update_user_info(
        self,
        db: Session,
        id: UUID,
        request: user_schemas.UpdateUser,
        current_user: str,
    ) -> JSONResponse:
        """Este metodo realiza la actualizacion de datos sobre un registro.

        Filtrado por su id, se pide el current_user para tener llenados la informacion
        para los datos de auditoria.

        #? ENDPOINT /users/{id} PUT

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
        # Buscamos a un user por su id, este no debe de estar marcado como eliminado
        user = get_one_user_info_by_id(db, id)
        # Si no existe el user, devolvemos un error
        if not user:
            main.logger.info(msg=f"User {id} not found!", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "msg": "Not Found"},
            )

        # Ahora se tiene que validar que exista el request.role_id
        check_role = get_role_exist(db, request.role_id)
        if not check_role:
            main.logger.info(msg=f"Role {request.role_id} is not valid!", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "msg": "Insert a valid Role"},
            )

        # We need validate if the email is unique
        if request.email != user.email:
            if get_user_by_email(db, request.email):
                main.logger.info(msg=f"{request.email} was taken!", extra=extra)
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"success": True, "msg": "Email was taken!"},
                )
        # Pero si lo encuentra. Actualiza!
        if not request.email:
            user.email = check_request_value(request.email, user.email)
        else:
            user.email = request.email.strip()

        user.is_active = check_request_value(request.is_active, user.is_active)
        user.role_id = request.role_id
        user.updated_by = current_user
        user.updated_on = datetime.now()
        db.add(user)
        db.commit()
        main.logger.info(msg=f"User {id} is updated!", extra=extra)
        return JSONResponse(
            status_code=202,
            content={
                "success": True,
                "msg": "Updated successfully",
            },
        )

    def delete_one_user(
        self, db: Session, id: UUID, current_user: str
    ) -> Optional[JSONResponse]:
        """Este metodo lo que hace es eliminar un registro (soft-deleted).

        Args:
            db (Session): _description_
            id (UUID): _description_
            current_user (str): _description_

        Returns:
            Optional[JSONResponse]: _description_
        Filtrandolo por su id en formato GUID V4

        #? ENDPOINT /users/{id}/delete/ DELETE
        Args:
            db (Session): Session para realizar acciones con SQLALCHEMY.
            Defaults to Depends().
            id (UUID v4): Este argumento es del tipo UUID v4 si se ingresa
            algo que no se encuentre en este formato sera invalido.
            current_user (str): Este argumento es el ID del usuario el cual
            es un GUID se obtiene con la clase Authorize y el metodo get_jwt_subject()

        Returns:
            Optional[JSONResponse]: status code 204 NO CONTENT para usar el método DELETE
             es necesario regresas NONE en caso de algun erro devolvemos un JSONRESPONSE.
        """
        user = get_one_user_info_by_id(db, id)

        if current_user == id.__str__():
            main.logger.info(
                msg=f"User {id} was trying to delete its self!", extra=extra
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"msg": "You can not deleted your self!!"},
            )

        if not user:
            main.logger.info(msg=f"User {id} not found", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "msg": "Not Found"},
            )

        user.is_deleted = True
        user.is_active = False
        user.updated_by = current_user
        user.updated_on = datetime.now()
        db.add(user)
        db.commit()
        main.logger.info(msg=f"User {id} it's deleted!", extra=extra)
        return None

    def update_password_user(
        self,
        db: Session,
        id: UUID,
        request: user_schemas.UpdatePass,
        current_user: str,
    ) -> JSONResponse:
        """Este metodo lo que hace es actualizar el campo del password de usuario.

        Filtrandolo por su id en formato UUID v4. Se pide el current_user para evitar
        que el usuario actualize su propio password usando esta funcion y endpoint.

        #? ENDPOINT /users/{id}/update/passwords PATCH

        Args:
            db (Session): Session para realizar acciones con SQLALCHEMY.
            Defaults to Depends().
            id (UUID v4): Este argumento es del tipo UUID v4 si se ingresa
            algo que no se encuentre en este formato sera invalido.
            request (Pydantic model): Modelo de pydantic para recibir
            la informacion proporcionada por el frontend o el usuario.
            current_user (str): Este argumento es el ID del usuario el
            cual es un GUID se obtiene con la clase Authorize y el metodo get_jwt_subject()

        Returns:
            JSONResponse: Nos devuelve una respuesta en JSON con la propiedad success
            y la propiedad msg con sus respectivos valores.
            En caso contrario nos mostrara la propiedad success y la propiedad msg.
        """
        # We need validate if the user exist
        user = get_one_user_info_by_id(db, id)
        # If the user is a current user, return error
        if current_user == id.__str__():
            main.logger.info(
                msg=f"User {id} cannot update self password in this endpoint!",
                extra=extra,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"success": True, "msg": "You can not update your password!!"},
            )

        if not user:
            main.logger.info(msg=f"User {id} not found!", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "msg": "Not Found"},
            )

        user.updated_by = current_user
        user.updated_on = datetime.now()
        user.password = Hash().bcrypt(request.new_password.strip())
        db.add(user)
        db.commit()
        main.logger.info(
            msg=f"the password from user {id} updated successfully!", extra=extra
        )
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"success": True, "msg": "Updated password successfully"},
        )

    def update_my_password(
        self, db: Session, request: user_schemas.UpdatePassMe, current_user: str
    ) -> JSONResponse:
        """Actualiza el campo del password del usuario en session.

        Como medida de seguridad se pide el password actual.
        Asi mismo se pide que se confirme el password nuevo.

        #? ENDPOINT /users/profile/update/password PATCH

        Args:
            db (Session): Session para realizar acciones con SQLALCHEMY.
            Defaults to Depends().
            request (Pydantic model): Modelo de pydantic para recibir la informacion
            proporcionada por el frontend o el usuario.
            current_user (str): Este argumento es el ID del usuario el cual es un GUID,
            se obtiene con la clase Authorize y el metodo get_jwt_subject()

        Returns:
            JSONResponse: Nos devuelve una respuesta en JSON con la propiedad success
            y la propiedad msg con sus respectivos valores. En caso contrario nos mostrara
            la propiedad success y la propiedad msg.
        """
        user = get_one_user_info_by_id(db, id=current_user)
        if not user:
            main.logger.info(msg=f"User {current_user} not found!", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "msg": "Not Found"},
            )
        if not Hash().verify(user.password.strip(), request.actual_password.strip()):
            main.logger.info(msg="Invalid credentials!", extra=extra)
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "msg": "Invalid Credentials"},
            )
        user.password = Hash().bcrypt(request.new_password.strip())
        user.updated_by = current_user
        user.updated_on = datetime.now()
        db.add(user)
        db.commit()
        main.logger.info(
            msg=f"the password from current user {id} updated successfully!",
            extra=extra,
        )
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"success": True, "msg": "Updated password successfully"},
        )
