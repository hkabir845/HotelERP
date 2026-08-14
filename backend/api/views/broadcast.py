"""Broadcast message endpoints."""
import uuid
from datetime import datetime

from rest_framework.decorators import api_view, permission_classes
from api.auth.permissions import IsAuthenticatedWithModule as IsAuthenticated
from rest_framework.response import Response

from api.views import deny_if_no_tenant


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def messages(request):
    """Get broadcast messages (mock data)."""
    denied = deny_if_no_tenant(request.user)
    if denied:
        return denied

    current_user = request.user
    status_filter = request.query_params.get('status')
    search = request.query_params.get('search')

    messages_list = [
        {'id': 1, 'message_number': f"MSG-{str(uuid.uuid4())[:8].upper()}", 'subject': 'Welcome Message', 'content': 'Welcome to our hotel! We hope you enjoy your stay.', 'recipient_type': 'all_guests', 'recipients': ['All Inhouse Guests'], 'status': 'sent', 'sent_at': datetime.now().isoformat(), 'created_by': current_user.first_name + ' ' + current_user.last_name},
        {'id': 2, 'message_number': f"MSG-{str(uuid.uuid4())[:8].upper()}", 'subject': 'Staff Meeting Reminder', 'content': 'Reminder: Staff meeting tomorrow at 10 AM in the conference room.', 'recipient_type': 'staff', 'recipients': ['All Staff Members'], 'status': 'scheduled', 'sent_at': None, 'created_by': current_user.first_name + ' ' + current_user.last_name},
        {'id': 3, 'message_number': f"MSG-{str(uuid.uuid4())[:8].upper()}", 'subject': 'Maintenance Notice', 'content': 'Scheduled maintenance in the pool area from 2 PM to 4 PM today.', 'recipient_type': 'all_guests', 'recipients': ['All Inhouse Guests'], 'status': 'draft', 'sent_at': None, 'created_by': current_user.first_name + ' ' + current_user.last_name},
    ]

    filtered = messages_list
    if status_filter and status_filter != 'all':
        filtered = [m for m in filtered if m['status'] == status_filter]
    if search:
        filtered = [
            m for m in filtered
            if search.lower() in m['subject'].lower() or search.lower() in m['message_number'].lower()
        ]

    return Response({'messages': filtered})
