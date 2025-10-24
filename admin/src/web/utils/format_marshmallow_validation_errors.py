def format_validation_errors(errors):
    """
    Formatea los errores de validación de Marshmallow al formato del PDF

    Args:
        errors: Dict de errores de Marshmallow

    Returns:
        Dict con formato {"error": {"code": "...", "message": "...", "details": {...}}}
    """
    details = {}

    for field, messages in errors.items():
        if isinstance(messages, list):
            details[field] = messages
        elif isinstance(messages, dict):
            # Para errores anidados
            details[field] = [str(v) for v in messages.values()] if messages else ["Invalid value"]
        else:
            details[field] = [str(messages)]

    return {
        "error": {
            "code": "invalid_data",
            "message": "Invalid input data",
            "details": details
        }
    }
