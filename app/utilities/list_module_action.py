from typing import Any, Dict


def make_list_module_action(list_permission: list[tuple[Any, ...]]) -> dict[str, Any]:
    """Genera una lista de modulos que contengan una lista de acciones.

    Args:
        list_permission (list[tuple[Any, ...]]): _description_

    Returns:
        dict[str, Any]: _description_
    """
    permissions: Dict[str, Any] = {}
    for permission, action in list_permission:
        # print(permission, action)
        if permission not in permissions:
            permissions[permission] = []

        if action not in permissions[permission]:
            permissions[permission].append(action)
    return permissions
