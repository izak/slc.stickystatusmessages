from zope.schema import Bool
from zope.interface import Interface
from slc.stickystatusmessages import StickyStatusMessageFactory as _

class IStickyStatusMessagesLayer(Interface):
    """Marker Interface used by as BrowserLayer
    """

class IStickyStatusMessagesSettings(Interface):
    """ Interface class that describes settings for plone.app.registry. """
    rolebased = Bool(
            title=_(u"Role Based Status Messages"),
            description=_(u"Use this option to enable or disable role based "
                          u"status messages."),
            required=True,
            default=True,
        )
