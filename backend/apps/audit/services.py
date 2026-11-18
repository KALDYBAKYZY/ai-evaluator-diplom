from apps.audit.models import AuditLog


def log_action(user, action: str, obj, meta: dict | None = None) -> AuditLog:
    return AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        entity=obj.__class__.__name__,
        entity_id=str(obj.pk),
        meta=meta or {},
    )
