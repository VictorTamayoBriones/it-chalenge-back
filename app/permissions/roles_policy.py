from app.dependencies.permissions import RoleChecker

"""Aqui definimos la politica de permisos y a que modulo pertenecen
Ya esto se define de forma en crudo :D.
Tambien puedes usar los GUUIDS pero ya sera a tu criterio 
Recuerda importarlo y usalo como dependencia para que funcione.
"""

roles_create = RoleChecker({"module": "roles", "permission": "create"})

roles_read = RoleChecker({"module": "roles", "permission": "read"})

roles_update = RoleChecker({"module": "roles", "permission": "update"})

roles_delete = RoleChecker({"module": "roles", "permission": "delete"})

roles_search = RoleChecker({"module": "roles", "permission": "search"})
