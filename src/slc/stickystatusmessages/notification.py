from datetime import datetime
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from slc.stickystatusmessages.utils import set_sticky_status_message
from slc.stickystatusmessages.config import SSMKEY

from Products.CMFCore.utils import getToolByName

try:
    from Products.CMFNotification.interfaces import INotificationDelivery

    class StickyStatusNotificationDelivery(object):
        implements(INotificationDelivery)

        def notify(self, obj, user, what, label,
                           get_users_extra_bindings,
                           mail_template_extra_bindings,
                           mail_template_options):

            portal_membership = getToolByName(obj, 'portal_membership')
            member = portal_membership.getMemberById(user)
            if member is not None:
                timestamp = datetime.now().isoformat()
                annotations = IAnnotations(member)
                sticky_messages = annotations.get(SSMKEY, {})
                mdict= {
                    'type': 'info',
                    'message': what, # TODO a better message
                    'timestamp': timestamp,
                    }
                sticky_messages[timestamp] = mdict
                annotations[SSMKEY] = sticky_messages
                return 1
            return 0

except ImportError:
    pass
