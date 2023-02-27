from app.dependencies.permissions import RoleChecker

"""Aqui definimos la politica de permisos y a que modulo pertenecen
Ya esto se define de forma en crudo :D.
Tambien puedes usar los GUUIDS pero ya sera a tu criterio 
Recuerda importarlo y usalo como dependencia para que funcione.
"""

permissions_create = RoleChecker({"module": "permissions", "permission": "create"})

permissions_read = RoleChecker({"module": "permissions", "permission": "read"})

permissions_update = RoleChecker({"module": "permissions", "permission": "update"})

permissions_delete = RoleChecker({"module": "permissions", "permission": "delete"})

permissions_search = RoleChecker({"module": "permissions", "permission": "search"})
