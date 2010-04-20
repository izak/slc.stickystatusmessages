import datetime
from zope.component import getMultiAdapter
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName
from config import SSMKEY

def set_sticky_status_messages(folder, message, type):
    """ """
    portal_groups = getToolByName(folder, 'portal_groups')
    groups_and_members = []
    sharing = getMultiAdapter((folder, folder.REQUEST), name='sharing')
    for roles_dict in sharing.existing_role_settings():
        if roles_dict['disabled']:
            continue

        if roles_dict['roles']['Editor'] in ['acquired', True]:
            groups_and_members.append(roles_dict['id'])

    if not groups_and_members:
        return

    # Annotate a sticky message dict to all the groups with local roles on the
    # folder
    portal_membership = getToolByName(folder, 'portal_membership')
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
            'obj_title': folder.Title(),
            'obj_url': '/'.join(folder.getPhysicalPath()),
            'message': message,
            'timestamp': timestamp,
            'member': member.getId(),
            }
        sticky_messages[timestamp] = mdict
        annotations[SSMKEY] = sticky_messages


