"""Write audit trail rows for staff actions."""
from api.models.audit import AuditLog


def write_audit(tenant, user, action, entity, entity_id=None, reference='', details=''):
    if not tenant:
        return None
    return AuditLog.objects.create(
        tenant=tenant,
        user=user if getattr(user, 'is_authenticated', False) else None,
        action=action,
        entity=entity,
        entity_id=entity_id,
        reference=reference or '',
        details=details or '',
    )
