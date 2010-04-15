from Acquisition import aq_inner
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.common import ViewletBase
from slc.stickystatusmessages.config import SSMKEY
from interfaces import IStickyStatusMessagesViewlet
from interfaces import IAJAXView

class StickyStatusMessagesViewlet(ViewletBase):
    """ """
    implements(IStickyStatusMessagesViewlet)
    index = ViewPageTemplateFile('templates/stickystatusmessages.pt')

    def messages(self):
        """ """
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        if mtool.isAnonymousUser():
            return []

        member = mtool.getAuthenticatedMember()
        group_names = member.getGroups()
        msgs_dict = {}
        for gip in group_names:
            group = member.getGroupById(gip)
            annotations = IAnnotations(group)
            ssm = annotations.get(SSMKEY, {})
            msgs_dict.update(ssm.get(member.getId(), {}))

        return msgs_dict.values()


class StickyStatusMessagesAJAXView(BrowserView):
    implements(IAJAXView)

    def delete_message(self, message_id, group_id):
        """ """
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        if mtool.isAnonymousUser():
            return []

        member = mtool.getAuthenticatedMember()
        group = member.getGroupById(group_id)
        annotations = IAnnotations(group)
        ssm = annotations.get(SSMKEY, {})
        msg = ssm.get(member.getId(), {})
        if msg.has_key(message_id):
            del msg[message_id]
