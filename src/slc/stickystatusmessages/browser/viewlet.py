from Acquisition import aq_inner
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from slc.stickystatusmessages import utils
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
        groups = utils.get_local_groups(context)
        mlist = []
        for group in groups:
            annotations = IAnnotations(group)
            mlist = annotations.get(SSMKEY, [])

        return mlist

class AJAXView(BrowserView):
    implements(IAJAXView)

    def delete_message(self, mid):
        """ """

