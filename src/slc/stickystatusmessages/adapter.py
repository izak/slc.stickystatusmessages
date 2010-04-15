import datetime
from zope.annotation.interfaces import IAnnotations
from zope.i18n import translate

from Products.statusmessages.adapter import StatusMessage
from Products.statusmessages import STATUSMESSAGEKEY
from Products.statusmessages.adapter import _encodeCookieValue

from config import SSMKEY
import utils

import logging
logger = logging.getLogger('statusmessages')

class StickyStatusMessage(StatusMessage):
    """Adapter for the BrowserRequest to handle status messages.
    
    Let's make sure that this implementation actually fulfills the
    'IStatusMessage' API.

      >>> from zope.interface.verify import verifyClass
      >>> verifyClass(IStatusMessage, StatusMessage)
      True
    """
    def add(self, text, type=u'info'):
        """Add a status message.
        """
        context = self.context
        text = translate(text, context=context)

        object = context['PARENTS'][0]
        groups = utils.get_local_groups(object)

        # Annotate a sticky message dict to all the groups with local roles on the
        # object
        if groups:
            timestamp = datetime.datetime.now().isoformat()

            for group in groups:
                group_annotations = IAnnotations(group)
                message = {
                    'type': type,
                    'obj_title': object.Title(),
                    'obj_url': '/'.join(object.getPhysicalPath()),
                    'message': text,
                    'timestamp': timestamp,
                    'group': group.getId(),
                    }
                ssm = group_annotations.get(SSMKEY, None)
                member_ids = group.getGroupMemberIds()
                for mid in member_ids:
                    msgdict = ssm.get(mid, {})
                    msgdict[timestamp] = message
                    ssm[mid] = msgdict

                group_annotations[SSMKEY] = ssm

        annotations = IAnnotations(context)

        old = annotations.get(STATUSMESSAGEKEY,
                              context.cookies.get(STATUSMESSAGEKEY))
        value = _encodeCookieValue(text, type, old=old)
        context.response.setCookie(STATUSMESSAGEKEY, value, path='/')
        annotations[STATUSMESSAGEKEY] = value


