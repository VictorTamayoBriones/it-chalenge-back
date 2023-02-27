from typing import Any


def check_request_value(request_field: Any, item: Any):
    """Verifica e iguala el valor de un campo al existente.

    Args:
        request_field (Any): _description_
        item (Any): _description_

    Returns:
        _type_: _description_
    """
    if request_field is None or str(request_field).strip() == "":
        request_field = item
    return request_field
