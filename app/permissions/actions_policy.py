from app.dependencies.permissions import RoleChecker

"""Aqui definimos la politica de permisos y a que modulo pertenecen
Ya esto se define de forma en crudo :D.
Tambien puedes usar los GUUIDS pero ya sera a tu criterio 
Recuerda importarlo y usalo como dependencia para que funcione.
"""
actions_create = RoleChecker({"module": "actions", "permission": "create"})

actions_read = RoleChecker({"module": "actions", "permission": "read"})

actions_update = RoleChecker({"module": "actions", "permission": "update"})

actions_delete = RoleChecker({"module": "actions", "permission": "delete"})

actions_search = RoleChecker({"module": "actions", "permission": "search"})
