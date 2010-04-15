from Products.CMFCore.utils import getToolByName

def get_local_groups(context):
    """ Get all the groups with local roles in this context
    """
    users_and_groups = context.users_with_local_role('Editor')
    portal_groups = getToolByName(context, 'portal_groups')
    groups = []
    for i in users_and_groups:
        group = portal_groups.getGroupById(i)
        if group is not None:
            groups.append(group)

    return groups
