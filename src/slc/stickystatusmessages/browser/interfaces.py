from zope.interface import Interface
from zope.viewlet.interfaces import IViewlet

class IStickyStatusMessagesViewlet(IViewlet):
    """ """

    def messages(self):
        """ """ 


class IAJAXView(Interface):

    def delete_message(self, mid):
        """ """
