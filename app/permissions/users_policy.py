from app.dependencies.permissions import RoleChecker

"""Aqui definimos la politica de permisos y a que modulo pertenecen
Ya esto se define de forma en crudo :D.
Tambien puedes usar los GUUIDS pero ya sera a tu criterio 
Recuerda importarlo y usalo como dependencia para que funcione.
"""
users_create = RoleChecker({"module": "users", "permission": "create"})

users_read = RoleChecker({"module": "users", "permission": "read"})

users_update = RoleChecker({"module": "users", "permission": "update"})

users_delete = RoleChecker({"module": "users", "permission": "delete"})

users_search = RoleChecker({"module": "users", "permission": "search"})
