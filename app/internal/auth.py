import datetime

from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse

from sqlalchemy import func
from sqlalchemy.sql.expression import false, true
from sqlalchemy.orm import Session
from fastapi_another_jwt_auth import AuthJWT

from app import main
from app.models.actions import Actions
from app.models.module import Module
from app.models.role_actions import Role_Actions
from app.schemas import schemas_config
from app.utilities.hashing import Hash
from app.queries.user_queries import get_current_user_info
from app.queries.user_queries import get_user_info_by_email
from app.utilities.list_module_action import make_list_module_action
from app.dependencies.data_conexion import get_db

extra = {"event.category": "auth"}


class AuthActions:
    """Esta clase tiene los metodos necesarios para hacer Auth."""

    def user_login(
        self,
        request: schemas_config.Login,
        db: Session = Depends(get_db),
        Authorize: AuthJWT = Depends(),
    ) -> JSONResponse:
        """Log a User.

        Este metodo lo que realizara es la creacion del JWT Token
         agregando dentro de el informacion,con sus roles y permisos.
         Esto filtrando que en realidad exista el usuario en la BD.

        #? Endpoint /auth/singing POST

        Args:
            request (schemas_config.Login): Esquema con el cual hacemos un request
             el cual nos pide el email y el password.
            db (Session): Sesion de SQLAlchemy para poder realizar consultas la BD.
             Defaults to Depends(get_db).
            Authorize (AuthJWT, optional): Dependecia y metodo de la clase FastAPI_users,
             para generar nuestro token. Defaults to Depends().

        Returns:
            JSONResponse: Nos devuelve un JSON con la propiedad success y otro objeto llamado data
             con el access_token y el refresh_token.

        """
        try:
            user = get_user_info_by_email(db, request.email)
            if not user:
                main.logger.info(
                    msg=f"Invalid Credentials {request.email}", extra=extra
                )
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "msg": "Invalid Credentials"},
                )

            if not Hash().verify(user.password, request.password):
                main.logger.info(
                    msg=f"Invalid Credentials {request.email}", extra=extra
                )
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "msg": "Invalid Credentials"},
                )

            if user.is_deleted is True:
                main.logger.info(
                    msg=f"Invalid Credentials {request.email}", extra=extra
                )
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "msg": "Invalid Credentials"},
                )

            if user.is_active is False:
                main.logger.info(
                    msg=f"Invalid Credentials {request.email}", extra=extra
                )
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "msg": "Invalid Credentials"},
                )

            result_permission = (
                db.query(func.lower(Module.name), func.lower(Actions.action_name))
                .order_by(Module.name)
                .join(Role_Actions, isouter=False)
                .join(Module, isouter=False)
                .filter(Role_Actions.role_id == user.role_id.__str__())
                .filter(Role_Actions.actions_id == Actions.id)
                .filter(Actions.module_id == Module.id)
                .filter(Actions.is_active == true())
                .filter(Actions.is_deleted == false())
                .filter(Module.is_deleted == false())
                .filter(Module.is_active == true())
                .filter(Role_Actions.is_deleted == false())
                .all()
            )

            permissions = make_list_module_action(result_permission)

            expires = datetime.timedelta(hours=2)
            expires_fresh = datetime.timedelta(hours=4)

            #  We need to convert user.id to string to be able to use it as a subject

            another_claims = {
                "role": user.role_id.__str__(),
                "is_active": user.is_active,
                "permissions": permissions,
            }
            access_token = Authorize.create_access_token(
                subject=user.id.__str__(),
                user_claims=another_claims,
                expires_time=expires,
            )
            refresh_token = Authorize.create_refresh_token(
                subject=user.id.__str__(),
                user_claims=another_claims,
                expires_time=expires_fresh,
            )

            res = {
                "success": True,
                "data": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_email": user.email,
                    "role_name": user.role_name,
                    "permissions": permissions,
                },
            }
            main.logger.info(msg=f"Success login {request.email}", extra=extra)
            return JSONResponse(res)
        except Exception as e:
            main.logger.info(msg=f"Failed login {request.email}", extra=extra)
            main.logger.error(msg=f"An exception occurred: {e}", extra=extra)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"success": False, "msg": "Bad Request"},
            )

    def refresh_token(
        self, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()
    ) -> JSONResponse:
        """Método refresh_token.

        Este método lo que hace es generar un refresh token para asi obtener
         un nuevo access token en caso de que nuestra session haya caducado.

        #? Endpoint /auth/refresh GET

        Args:
            db (Session): Sesion de SQLAlchemy para poder realizar consultas la BD.
             Defaults to Depends(get_db).
            Authorize (AuthJWT, optional): Dependecia y metodo de la clase FastAPI_users
             para generar nuestro token. Defaults to Depends().

        Return
            JSONResponse: Nos devuelve una respuesta en JSON con la propiedad success
             en caso de tener exito nos mostarara nuestros nuevos tokens.
             En caso contrario lo único que hara sera regresarnos un JSON
             con la propiedad success y msg.
        """
        try:
            Authorize.jwt_refresh_token_required()
            current_user = Authorize.get_jwt_subject()

            if not current_user:
                main.logger.info(msg="Could not refresh access token!", extra=extra)
                return JSONResponse(
                    status_code=status.HTTP_421_MISDIRECTED_REQUEST,
                    content={"success": True, "msg": "Could not refresh access token!"},
                )

            validate_current_user = get_current_user_info(db, current_user)

            if not validate_current_user or validate_current_user is None:
                main.logger.info(
                    msg=f"Invalidate user {validate_current_user.email} ", extra=extra
                )
                return JSONResponse(
                    status_code=421,
                    content={
                        "success": False,
                        "msg": "The user belonging to this token no logger exist",
                    },
                )

            """
                The jwt_refresh_token_required() function insures a valid refresh
                token is present in the request before running any code below that function.
                we can use the get_jwt_subject() function to get the subject of the refresh
                token, and use the create_access_token() function again to make a new access token
            """
            result_permission = (
                db.query(func.lower(Module.name), func.lower(Actions.action_name))
                .order_by(Module.name)
                .join(Role_Actions, isouter=False)
                .join(Module, isouter=False)
                .filter(Role_Actions.role_id == validate_current_user.role_id.__str__())
                .filter(Role_Actions.actions_id == Actions.id)
                .filter(Actions.module_id == Module.id)
                .filter(Actions.is_active == true())
                .filter(Actions.is_deleted == false())
                .filter(Module.is_active == true())
                .filter(Module.is_deleted == false())
                .filter(Role_Actions.is_active == true())
                .filter(Role_Actions.is_deleted == false())
                .all()
            )

            permissions = make_list_module_action(result_permission)

            expires = datetime.timedelta(hours=2)
            expires_fresh = datetime.timedelta(hours=4)

            another_claims = {
                "role": validate_current_user.role_id.__str__(),
                "is_active": validate_current_user.is_active,
                "permissions": permissions,
            }
            new_access_token = Authorize.create_access_token(
                subject=validate_current_user.id.__str__(),
                user_claims=another_claims,
                expires_time=expires,
            )
            new_refresh_token = Authorize.create_refresh_token(
                subject=validate_current_user.id.__str__(),
                user_claims=another_claims,
                expires_time=expires_fresh,
            )
            main.logger.info(
                msg=f"Refreshing Session at user {validate_current_user.email}",
                extra=extra,
            )
            return JSONResponse(
                {
                    "success": True,
                    "data": {
                        "access_token": new_access_token,
                        "refresh_token": new_refresh_token,
                        "user_email": validate_current_user.email,
                        "role_name": validate_current_user.role_name,
                        "permissions": permissions,
                    },
                }
            )
        except Exception as e:
            error = e.__class__.__name__
            main.logger.info(msg=f"An exception occurred: {error}", extra=extra)

            if error == "MissingTokenError":
                main.logger.info(msg=f"An exception occurred: {error}", extra=extra)
                raise HTTPException(
                    status_code=status.HTTP_421_MISDIRECTED_REQUEST,
                    detail={"status": False, "msg": "Please provide refresh token"},
                )
            main.logger.error(msg=f"An exception occurred: {error}", extra=extra)
            raise HTTPException(
                status_code=status.HTTP_421_MISDIRECTED_REQUEST,
                detail={"status": False, "msg": error},
            )
