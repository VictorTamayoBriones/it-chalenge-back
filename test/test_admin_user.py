#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json  # noqa
from typing import Any, Generator


import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


from app import main
from app.database.main import SessionLocal
from app.models.roles import Role
from app.models.users import Users
from app.models.module import Module
from app.models.actions import Actions
from app.models.role_actions import Role_Actions
from test import uuids_for_test
from test.list_of_items import all_actions

client = TestClient(app=main.app)


@pytest.fixture(scope="module")
def setup() -> Generator[Session, None, None]:
    """Generamos conexion y borramos todo al final.

    Yields:
        Generator[Session, None, None]: Conexion a la BD.
    """
    # setup conexion
    db = SessionLocal()
    yield db
    # teardown
    delete_role_actions = db.query(Role_Actions).all()
    for item in delete_role_actions:
        db.delete(item)
    db.flush()

    delete_actions = db.query(Actions).all()
    for a in delete_actions:
        db.delete(a)
        db.flush()
    db.commit()

    delete_modules = db.query(Module).all()
    for m in delete_modules:
        db.delete(m)
        db.flush()
    db.commit()

    delete_user = db.query(Users).all()
    for u in delete_user:
        db.delete(u)
        db.flush()
    db.commit()

    delete_role = db.query(Role).all()
    for r in delete_role:
        db.delete(r)
        db.flush()
    db.commit()


@pytest.mark.run(order=1)
def test_create_all(setup) -> None:
    """Creamos todo de forma no dinamica.

    Args:
        setup (Yield): Conexion a la BD
    """
    setup.bulk_save_objects(all_actions)
    setup.commit()


@pytest.fixture()
@pytest.mark.run(order=2)
def setUpToken() -> Generator[dict[str, Any], None, None]:
    """Generamos un token.

    Yields:
        Generator[dict[str, Any], None, None]: Generamos un hilo el cual contiene el token.
    """
    login_admin_user = {
        "email": f"{uuids_for_test.user_email}",
        "password": f"{uuids_for_test.user_password}",
    }
    response = client.post("/auth/signing", json=login_admin_user)
    header_user = {"Authorization": "Bearer " + response.json()["data"]["access_token"]}
    yield header_user


@pytest.fixture()
@pytest.mark.run(order=3)
def setUpRefreshToken() -> Generator[dict[str, Any], None, None]:
    """Generamos un refresh token.

    Yields:
        Generator[dict[str, Any], None, None]: Generamos un hilo el cual
         contiene el refresh token.
    """
    login_admin_user = {
        "email": f"{uuids_for_test.user_email}",
        "password": f"{uuids_for_test.user_password}",
    }
    response = client.post("/auth/signing", json=login_admin_user)
    header_refresh_user = {
        "Authorization": "Bearer " + response.json()["data"]["refresh_token"]
    }
    yield header_refresh_user


@pytest.mark.run(order=4)
def test_refresh_token(setUpRefreshToken) -> None:
    """Verificamos si funciona el Refresh Token.

    Args:
        setUpRefreshToken (Yield): Refresh Token
    """
    header = setUpRefreshToken
    response = client.get("/auth/refresh", headers=header)
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "data" in content
    assert "success" in content
    assert "access_token" in content["data"]
    assert "refresh_token" in content["data"]
    assert "user_email" in content["data"]
    assert "role_name" in content["data"]
    assert content["data"]["role_name"] == "test_admin"
    assert "permissions" in content["data"]


@pytest.mark.run(order=1)
@pytest.mark.run(order=5)
def test_user_profile(setUpToken):
    """Verificamos la informacion del usuario.

    Args:
        setUpToken (Yield): Token
    """
    header = setUpToken
    response = client.get("/profile", headers=header)
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "data" in content
    assert "success" in content
    assert "id" in content["data"]
    assert "email" in content["data"]
    assert "is_active" in content["data"]
    assert "role_id" in content["data"]
    assert "role_name" in content["data"]


@pytest.mark.parametrize(
    "email, password",
    [(f"{uuids_for_test.user_email}", f"{uuids_for_test.user_password}")],
)
@pytest.mark.run(order=6)
def test_login_valid_credentials(email: str, password: str) -> None:
    """Verificamos login con credenciales validas.

    Args:
        email (str): email for a user
        password (str): password for a user
    """
    user = {"email": email, "password": password}
    response = client.post("/auth/signing", json=user)
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "data" in content
    assert "success" in content
    assert "access_token" in content["data"]
    assert "refresh_token" in content["data"]
    assert "user_email" in content["data"]
    assert "role_name" in content["data"]
    assert "permissions" in content["data"]


@pytest.mark.parametrize(
    "endpoint",
    [
        ("/users/?start=asdjhhg&limit=asdasd"),
        ("/users/?start=0&limit=asdasd"),
        ("/users/?start=whdjgasd&limit=16"),
        ("/roles/?start=r0&limit=16"),
        ("/roles/?start=ttt16&limit=32"),
        ("/modules/?start=0&limit=16hjbjh"),
        ("/modules/?start=16&limit=3nn2"),
        ("/permissions/?start=0&limit=1·"),
        ("/permissions/?start=##&limit=32"),
        ("/actions/?start===&limit=16"),
        ("/actions/?start===16&limit=32"),
    ],
)
@pytest.mark.run(order=7)
def test_get_all_items_bad_queries_params(setUpToken, endpoint) -> None:
    """Verificamos validaciones en parametros de queries en rutas GET.

    Args:
        setUpToken (Yield): Token
        endpoint (str): ruta a la cual se ejecutara el test.
    """
    header = setUpToken
    response = client.get(endpoint, headers=header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    content = response.json()
    assert "detail" in content


@pytest.mark.parametrize(
    "endpoint",
    [
        ("/users/"),
        ("/users/?start=0&limit=16"),
        ("/users/?start=16&limit=32"),
        ("/roles/"),
        ("/roles/?start=0&limit=16"),
        ("/roles/?start=16&limit=32"),
        ("/modules/"),
        ("/modules/?start=0&limit=16"),
        ("/modules/?start=16&limit=32"),
        ("/permissions/"),
        ("/permissions/?start=0&limit=16"),
        ("/permissions/?start=16&limit=32"),
        ("/actions/"),
        ("/actions/?start=0&limit=16"),
        ("/actions/?start=16&limit=32"),
    ],
)
@pytest.mark.run(order=8)
def test_get_all_items(setUpToken, endpoint) -> None:
    """Verificamos obtencion de datos en rutas GET.

    Args:
        setUpToken (Yield): Token
        endpoint (str): ruta a la cual se ejecutara el test.
    """
    header = setUpToken
    response = client.get(endpoint, headers=header)
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "data" in content
    assert "success" in content
    assert "numRows" in content


@pytest.mark.parametrize(
    "endpoint",
    [
        ("/users/3520c0d0-35a3-4caf-803f-0e162ba1ef8e"),
        ("/roles/4e5a506c-1973-4cf6-ae52-716ecf4cb239"),
        ("/modules/446d0bd7-cfc7-4a89-8767-080d844e1453"),
        # ('/permissions/b93ad4c7-1590-407f-b311-7266b7f3989a'),
    ],
)
@pytest.mark.run(order=9)
def test_get_one_item(setUpToken, endpoint) -> None:
    """Verificamos la obtencion de un objeto en rutas GET.

    Args:
        setUpToken (Yield): Token
        endpoint (str): ruta a la cual se ejecutara el test.
    """
    header = setUpToken
    response = client.get(endpoint, headers=header)
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "data" in content
    assert "success" in content


@pytest.mark.parametrize(
    "endpoint",
    [
        ("/users/5bd962ba-0a4f-4d86-ab58-265d5a87f3cd"),
        ("/users/b0365aec-e1d5-4aa2-8fed-22dbd31fef58"),
        ("/roles/bc838273-b035-4bf4-99ec-d660e1ba6f49"),
        ("/roles/160af225-3b55-4fb0-8a8f-989ebff29eac"),
        ("/modules/e3a3c8b6-9206-401f-a1da-cc14705c75dc"),
        ("/modules/708c210d-1482-4a25-aac1-51ba494110df"),
        ("/actions/73e46ed9-c3c2-47bb-ab59-670d3899923e"),
        ("/actions/5cef3a61-b2ed-47a2-a33b-eaaced2a37fc"),
        ("/permissions/2c97dbf5-b92f-4d36-a521-f91278c3568b"),
        ("/permissions/5a8dc5b2-4174-482a-b900-49ace01c0752"),
    ],
)
@pytest.mark.run(order=10)
def test_get_one_item_fail(setUpToken, endpoint) -> None:
    """Verificamos la validaion al obtener un objeto en rutas GET.

    Args:
        setUpToken (Yield): Token
        endpoint (str): ruta a la cual se ejecutara el test.
    """
    header = setUpToken
    response = client.get(endpoint, headers=header)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "endpoint",
    [
        ("/users/5bd962ba-0a4-4d86-ab58-265d5a87f3cd"),
        ("/users/b0365aec-e1d5-4aa2-8fed-2dbd31fef58"),
        ("/roles/bc873-b035-4bf4-99ec-d660e1ba6f49"),
        ("/roles/160af225-3b55-4fb0-8a8f-9bff29eac"),
        ("/modules/e3a3c8b6-9206-401f-a1da-xdsfghj"),
        ("/modules/708c210d-1482-4a25-aac1-51ba4941"),
        ("/actions/73e46ed9-c3c2-47bb-ab5@@9-670d3899923e"),
        ("/actions/5cs33b-ed2a37fc"),
        ("/permissions/2c97dbf521f91278c356b"),
        ("/permissions/5a"),
    ],
)
def test_get_one_item_fail_format(setUpToken, endpoint) -> None:
    """Verificamos la validaion del UUID al obtener un objeto en rutas GET.

    Args:
        setUpToken (Yield): Token
        endpoint (str): ruta a la cual se ejecutara el test.
    """
    header = setUpToken
    response = client.get(endpoint, headers=header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "email, name, last_name, password, role_id",
    [
        (
            "test_user_1@gmail.com",
            "Test",
            "guest",
            "strongerpassword",
            f"{uuids_for_test.role_uuid}",
        ),
    ],
)
def test_user_post_endpoint(
    setUpToken, email: str, name: str, last_name: str, password: str, role_id: str
) -> None:
    """Create a test user.

    This function make a user succesfully.
    """
    header = setUpToken
    data = {
        "email": email,
        "name": name,
        "last_name": last_name,
        "password": password,
        "role_id": role_id,
    }
    response = client.post("/users/", headers=header, json=data)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.parametrize(
    "name, description",
    [
        ("guest", "lorem Ipsum is simply dummy text"),
    ],
)
def test_role_post_endpoint(setUpToken, name: str, description: str) -> None:
    """Create a test role.

    This function make a role succesfully.
    """
    header = setUpToken
    data = {
        "name": name,
        "description": description,
    }
    response = client.post("/roles/", headers=header, json=data)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.parametrize(
    "name, description",
    [
        ("guest", "lorem Ipsum is simply dummy text."),
    ],
)
def test_module_post_endpoint(setUpToken, name: str, description: str) -> None:
    """Create a test module.

    This function make a module succesfully.
    """
    header = setUpToken
    data = {
        "name": name,
        "description": description,
    }
    response = client.post("/modules/", headers=header, json=data)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.parametrize(
    "action_name, description, is_active",
    [
        ("read", "orem Ipsum is simply dummy text.", "True"),
    ],
)
def test_action_post_endpoint(
    setUpToken, action_name: str, description: str, is_active: bool
) -> None:
    """Create a test action.

    This function make a module succesfully.
    """
    header = setUpToken
    db = SessionLocal()

    module_id = db.query(Module).filter(Module.name == "guest").first()

    data = {
        "action_name": action_name,
        "description": description,
        "is_active": is_active,
        "module_id": module_id.id.__str__(),
    }
    response = client.post("/actions/", headers=header, json=data)
    assert response.status_code == status.HTTP_201_CREATED
    db.close()


@pytest.mark.parametrize(
    "description",
    [
        ("Lorem Ipsum is simply dummy text."),
    ],
)
def test_permission_post_endpoint(setUpToken, description: str) -> None:
    """Create a test permission.

    This function make a permission succesfully.
    """
    header = setUpToken
    db = SessionLocal()
    role_uuid = db.query(Role).filter(Role.name == "guest").first()
    ac_id = db.query(Actions).filter(Actions.action_name == "read").first()

    data = {
        "role_id": role_uuid.id.__str__(),
        "description": description,
        "actions_id": ac_id.id.__str__(),
    }
    response = client.post("/permissions/", headers=header, json=data)
    assert response.status_code == status.HTTP_201_CREATED
    db.close()


@pytest.mark.parametrize(
    "endpoint",
    [
        (f"/users/{uuids_for_test.second_user_uuid}"),
    ],
)
def test_put_user(setUpToken, endpoint):
    """Update a user.

    Actualizamos un usuario existente.

    Args:
        setUpToken (Yield): Token
        endpoint (str): Endpoint a la que se hara el request.
    """
    header = setUpToken
    data = {
        "name": "Pablo",
        "last_name": "Vazquez",
        "email": "don_polo@gmail.com",
        "password": "passwordconñ",
        "is_active": False,
        "role_id": f"{uuids_for_test.role_uuid}",
    }
    response = client.put(endpoint, headers=header, json=data)
    assert response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.parametrize(
    "endpoint",
    [
        (f"/roles/{uuids_for_test.second_role_uuid}"),
    ],
)
def test_put_role(setUpToken, endpoint):
    """Update a role.

    Actualizamos un rol existente.

    Args:
        setUpToken (Yield): Token
        endpoint (str): Endpoint a la que se hara el request.
    """
    header = setUpToken
    data = {"name": "premiun", "descrtiption": "Rol para usuarios premiun."}
    response = client.put(endpoint, headers=header, json=data)
    assert response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.parametrize(
    "endpoint",
    [
        (f"/modules/{uuids_for_test.module_premiun_uuid}"),
    ],
)
def test_put_module(setUpToken, endpoint):
    """Update a module.

    Actualizamos un modulo existente.

    Args:
        setUpToken (Yield): Token
        endpoint (str): Endpoint a la que se hara el request.
    """
    header = setUpToken
    data = {
        "name": "premiun",
        "description": "Hemos actualizado este campo claro que yes",
    }
    response = client.put(endpoint, headers=header, json=data)
    assert response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.parametrize(
    "endpoint",
    [
        (f"/actions/{uuids_for_test.action_create_premiun_uuid}"),
    ],
)
def test_put_action(setUpToken, endpoint):
    """Update a action.

    Actualizamos una accion existente.

    Args:
        setUpToken (_type_): _description_
        endpoint (_type_): _description_
    """
    header = setUpToken
    data = {
        "action_name": "read",
        "description": "ahora esta accion se llama leer",
        "is_active": False,
        "module_id": f"{uuids_for_test.module_premiun_uuid}",
    }
    response = client.put(endpoint, headers=header, json=data)
    assert response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.parametrize(
    "endpoint",
    [
        (f"/permissions/{uuids_for_test.permission_create_premiun_uuid}"),
    ],
)
def test_put_role_action(setUpToken, endpoint):
    """Update a permission.

    Actualizamos un permiso existente.

    Args:
        setUpToken (_type_): _description_
        endpoint (_type_): _description_
    """
    header = setUpToken
    data = {"description": "He cambiado la descripcion", "is_active": "true"}
    response = client.put(endpoint, headers=header, json=data)
    assert response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.parametrize(
    "actual_password, new_password, password_confirmation",
    [
        ("1234567890", "qwertyuiop", "1234567890"),
        ("test_password", "qwertyuiop", "1234567890"),
        ("strangepassword", "1234567890", "12345678s0"),
        ("another2134234password", "1267890", "12345678s0"),
    ],
)
def test_user_update_self_password_fail(
    setUpToken, actual_password: str, new_password: str, password_confirmation: str
) -> None:
    """Verificamos la validacion al modificar un password.

    Args:
        setUpToken (Yield): Token
        actual_password (str): ingresa el passowrd actual
        new_password (str): Ingresa el nuevo password
        password_confirmation (str): Confirma el password anterior
    """
    header = setUpToken
    data = {
        "actual_password": actual_password,
        "new_password": new_password,
        "password_confirmation": password_confirmation,
    }
    response = client.patch("/profile/update/password", headers=header, json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "actual_password, new_password, password_confirmation",
    [
        ("qwertyuiop", "1234567890", "1234567890"),
        ("strangepassword", "1234567890", "1234567890"),
    ],
)
def test_user_update_self_password_invalid_credentials(
    setUpToken, actual_password: str, new_password: str, password_confirmation: str
) -> None:
    """Verificamos la validacion al modificar un password.

    Args:
        setUpToken (Yield): Token
        actual_password (str): ingresa el passowrd actual
        new_password (str): Ingresa el nuevo password
        password_confirmation (str): Confirma el password anterior
    """
    header = setUpToken
    data = {
        "actual_password": actual_password,
        "new_password": new_password,
        "password_confirmation": password_confirmation,
    }
    response = client.patch("/profile/update/password", headers=header, json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "id",
    [
        (f"{uuids_for_test.permission_create_permission_uuid}"),
        (f"{uuids_for_test.permission_read_permission_uuid}"),
        (f"{uuids_for_test.permission_update_permission_uuid}"),
    ],
)
def test_permissions_delete_endpoint(setUpToken, id: str) -> None:
    """Elimanando modulos.

    Se eliminana los modulos en el orden indicado.

    Args:
        setUpToken (str): Bearer Token
        id (str): id del item al que se le ejcutara la accion.
    """
    header = setUpToken
    response = client.delete(f"/permissions/{id}", headers=header)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.parametrize(
    "endpoint",
    [
        ("/users/8e9ef6b9-99d7-4b4a-bfe0-35f3761cbd0f"),
        ("/actions/21190fa5-7014-482c-a131-c85732513181"),
        ("/modules/780c8ca7-d2d2-4d1e-baba-571ac0ead2fc"),
        ("/roles/6f18749e-2846-46eb-bcb3-fcb6ad4548e6"),
        ("/permissions/6f18749e-2846-46eb-bcb3-fcb6ad4548e6"),
    ],
)
def test_all_delete_endpoints_fail(setUpToken, endpoint: str) -> None:
    """Elimanando Items.

    Se eliminaran algunos elementos los cuales su ID no existe en la DB.

    Args:
        setUpToken (str): Bearer Token
        endpoint (str): url del item al que se le ejcutara la accion.
    """
    header = setUpToken
    response = client.delete(f"{endpoint}", headers=header)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "endpoint",
    [
        ("/users/9d7-4b4a-bfe0-35f3761cbd0f/"),
        ("/actions/SG9sYSBzb3kgcG9sbw==/"),
        ("/modules/ASDASDUYAGSHJac0ead2fc/"),
        ("/roles/6f18749e-2846-46eb-bcb3-fcb6ad456/"),
        ("/permissions/adsdfadfsf/"),
    ],
)
def test_all_delete_endpoints_uuid_format_fail(setUpToken, endpoint: str) -> None:
    """Elimanando Permisos.

    Se eliminaran algunos elementos los cuales No cumplen con el formato UUID v4.

    Args:
        setUpToken (str): Bearer Token
        endpoint (str): url del item al que se le ejcutara la accion.
    """
    header = setUpToken
    response = client.delete(f"{endpoint}", headers=header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "actual_password, new_password, password_confirmation",
    [
        (f"{uuids_for_test.user_password}", "1234567890", "1234567890"),
    ],
)
def test_user_update_self_password_fine(
    setUpToken, actual_password: str, new_password: str, password_confirmation: str
) -> None:
    """Verificamos la funcionalidad al modificar un password.

    Args:
        setUpToken (Yield): Token
        actual_password (str): ingresa el passowrd actual
        new_password (str): Ingresa el nuevo password
        password_confirmation (str): Confirma el password anterior
    """
    header = setUpToken
    data = {
        "actual_password": actual_password,
        "new_password": new_password,
        "password_confirmation": password_confirmation,
    }
    response = client.patch("/profile/update/password", headers=header, json=data)
    assert response.status_code == status.HTTP_202_ACCEPTED
