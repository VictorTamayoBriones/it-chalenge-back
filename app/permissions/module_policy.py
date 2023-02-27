from app.dependencies.permissions import RoleChecker

"""Aqui definimos la politica de permisos y a que modulo pertenecen
Ya esto se define de forma en crudo :D.
Tambien puedes usar los GUUIDS pero ya sera a tu criterio 
Recuerda importarlo y usalo como dependencia para que funcione.
"""

modules_create = RoleChecker({"module": "modules", "permission": "create"})

modules_read = RoleChecker({"module": "modules", "permission": "read"})

modules_update = RoleChecker({"module": "modules", "permission": "update"})

modules_delete = RoleChecker({"module": "modules", "permission": "delete"})

modules_search = RoleChecker({"module": "modules", "permission": "search"})
