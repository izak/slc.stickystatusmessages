from zope.interface import Interface
from zope.viewlet.interfaces import IViewlet

class IStickyStatusMessagesViewlet(IViewlet):
    """ """

    def messages(self):
        """ """ 


class IAJAXView(Interface):

    def delete_all_messages(self):
        """ Remove all the currently stored sticky messages by simply
            replacing the annotations with a new empty dict.
        """

    def delete_message(self, mid):
        """ """
