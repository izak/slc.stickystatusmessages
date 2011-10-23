from datetime import datetime
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from zope.i18n import interpolate
from slc.stickystatusmessages import StickyStatusMessageFactory as _
from slc.stickystatusmessages.utils import set_sticky_status_message
from slc.stickystatusmessages.config import SSMKEY

from Products.CMFCore.utils import getToolByName

_messages = {
    'item_creation': _('Item <a href="$u">$t</a> has been created'),
    'item_modification': _('Item <a href="$u">$t</a> has been modified'),
    'item_removal': _('Item $t has been removed'),
    'wf_transition': _('Status of <a href="$u">$t</a> has changed, it is now $s'),
    'member_registration': _('Member $m registered'),
    'member_modification': _('Member $m was modified'),
    'discussion_item_creation': _('<a href="$u">Discussion item</a> was created'),
}

try:
    from Products.CMFNotification.interfaces import INotificationDelivery

    class StickyStatusNotificationDelivery(object):
        implements(INotificationDelivery)

        @property
        def description(self):
            return _(u'sticky_status_notification_delivery_description',
                       default=u'Notify using status messages')

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

                # Create mapping for interpolation
                mapping = {
                    'u': obj.absolute_url(),
                    't': obj.Title(),
                    's': mail_template_options['current_state'],
                    'm': str(mail_template_options.get('member'))
                }

                msg = interpolate(_messages[what], mapping)

                mdict= {
                    'type': 'info',
                    'message': msg,
                    'timestamp': timestamp,
                    }
                sticky_messages[timestamp] = mdict
                annotations[SSMKEY] = sticky_messages
                return 1
            return 0

except ImportError:
    pass
