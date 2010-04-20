from zope.event import notify
from zope.component import getMultiAdapter
from zope.annotation.interfaces import IAnnotations
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from slc.stickystatusmessages.tests.base import TestCase
from slc.stickystatusmessages.config import SSMKEY

class TestChat(TestCase):
    """ Tests the babble/client/browser/chat.py module
    """

    def afterSetUp(self):
        self.loginAsPortalOwner()

        self.mt = mt = getToolByName(self.portal, 'portal_membership')

        mt.addMember('single_user', 'pw', ['Member'], [],
                     {'email': 'single_user@host.com',
                      'title': 'Single User'})

        # Create a folder with local roles 
        id = self.portal.invokeFactory('Folder', 'folder')
        folder = self.portal._getOb(id)
        folder.manage_setLocalRoles('single_user', ["Editor"])
        

    def test_deletion(self):
        """ """
        folder = self.portal.folder

        # Create the document in a folder where single_user has the
        # 'Editor' role
        id = folder.invokeFactory('Document', 'document')
        doc = folder._getOb(id)
        doc.setTitle('Document')
        notify(ObjectInitializedEvent(doc))

        message = u'Document <a href="/plone/folder/document">Document</a> ' \
                  u'created in <a href="/plone/folder"></a>'
        # Test that the standalone user received sticky messages
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')


        view = getMultiAdapter(
                    (folder, folder.REQUEST), 
                    name='StickyStatusMessagesAJAXView')

        view.delete_message(sticky_messages.values()[0]['timestamp'])
        self.assertEquals(len(sticky_messages.values()), 1)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestChat))
    return suite

