#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json  # noqa
from typing import Any, Generator
from uuid import UUID


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


@pytest.mark.parametrize(
    "endpoint",
    [
        ("/users/"),
        ("/users/?start=0&limit=16"),
        ("/users/?start=16&limit=32"),
    ],
)
@pytest.mark.run(order=3)
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
        (f"/users/{uuids_for_test.user_uuid}"),
        (f"/users/{uuids_for_test.second_user_uuid}"),
    ],
)
@pytest.mark.run(order=4)
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
    "email, password, role_id",
    [
        ("someone@email.com", "strongpassword", f"{uuids_for_test.second_role_uuid}"),
    ],
)
@pytest.mark.run(order=5)
def test_user_post_endpoint(
    setUpToken, email: str, password: str, role_id: UUID
) -> None:
    """Create a test user.

    This function make a user succesfully.
    """
    header = setUpToken
    data = {"email": email, "password": password, "role_id": role_id}
    response = client.post("/users/", headers=header, json=data)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.parametrize(
    "endpoint",
    [
        (f"/users/{uuids_for_test.second_user_uuid}"),
    ],
)
@pytest.mark.run(order=6)
def test_put_user(setUpToken, endpoint):
    """Update a user.

    Actualizamos un user existente.

    Args:
        setUpToken (Yield): Token
        endpoint (str): Endpoint a la que se hara el request.
    """
    header = setUpToken
    data = {
        "email": "otroeemail@email.com",
        "is_active": "true",
        "role_id": f"{uuids_for_test.role_uuid}",
    }
    response = client.put(endpoint, headers=header, json=data)
    assert response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.parametrize(
    "endpoint",
    [
        (f"/users/{uuids_for_test.second_user_uuid}"),
    ],
)
@pytest.mark.run(order=7)
def test_delete_user(setUpToken, endpoint):
    """Update a user.

    Actualizamos un user existente.

    Args:
        setUpToken (Yield): Token
        endpoint (str): Endpoint a la que se hara el request.
    """
    header = setUpToken
    response = client.delete(endpoint, headers=header)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.run(order=8)
def test_user_create_item_was_deleted(setUpToken) -> None:
    """Create a test user.

    This function make a user succesfully.
    """
    header = setUpToken
    data = {
        "email": "email@email.com",
        "password": "itsastrongerpassword",
        "role_id": f"{uuids_for_test.role_uuid}",
    }
    response = client.post("/users/", headers=header, json=data)
    main.logger.info(response)
    print(response)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.parametrize(
    "endpoint",
    [
        ("/users/search/test"),
        ("/users/search/test_admin"),
        ("/users/search/pre"),
    ],
)
@pytest.mark.run(order=9)
def test_get_one_item_by_email(setUpToken, endpoint) -> None:
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
        ("/users/search/"),
        (
            "/users/Lorem Ipsum is simply dummy text of the printing and typesetting industry"
        ),
    ],
)
@pytest.mark.run(order=10)
def test_bad_get_one_item_by_name(setUpToken, endpoint) -> None:
    """Verificamos que nos devuelva un error de validacion.

    Args:
        setUpToken (Yield): Token
        endpoint (str): ruta a la cual se ejecutara el test.
    """
    header = setUpToken
    response = client.get(endpoint, headers=header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
