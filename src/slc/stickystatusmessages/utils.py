import datetime
from zope.component import getMultiAdapter
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName
from config import SSMKEY

def set_sticky_status_message(obj, message, type='info'):
    """ obj:  The object on which the operation occured and on which the
            sharing roles are defined that determine who receives the 
            sticky message.
        message: The message string
        type:    The message type string, i.e 'info', 'error' 
    """
    portal_groups = getToolByName(obj, 'portal_groups')
    groups_and_members = []
    sharing = getMultiAdapter((obj, obj.REQUEST), name='sharing')
    for roles_dict in sharing.existing_role_settings():
        if roles_dict['disabled']:
            continue

        if roles_dict['roles'].get('Editor') in ['acquired', True]:
            groups_and_members.append(roles_dict['id'])

    if not groups_and_members:
        return

    # Annotate a sticky message dict to all the groups with local roles on the
    # obj
    portal_membership = getToolByName(obj, 'portal_membership')
    current_member = portal_membership.getAuthenticatedMember().getId()
    timestamp = datetime.datetime.now().isoformat()

    members = []
    for group_or_member in groups_and_members:
        group = portal_groups.getGroupById(group_or_member)
        if group:
            members += group.getGroupMemberIds()
        else:
            members.append(group_or_member)

    if current_member in members:
        members.remove(current_member)

    for mid in members:
        member = portal_membership.getMemberById(mid)
        annotations = IAnnotations(member)
        # annotations[SSMKEY] = {}
        sticky_messages = annotations.get(SSMKEY, {})
        mdict= {
            'type': type,
            'message': message,
            'timestamp': timestamp,
            }
        sticky_messages[timestamp] = mdict
        annotations[SSMKEY] = sticky_messages


