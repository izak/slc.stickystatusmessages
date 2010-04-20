from zope.event import notify
from zope.annotation.interfaces import IAnnotations
from Products.Archetypes.event import ObjectEditedEvent
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
        self.gt = gt = getToolByName(self.portal, 'portal_groups')
        self.md = md = getToolByName(self.portal, 'portal_memberdata')

        # Create a new Member
        mt.addMember('group_user', 'pw', ['Member'], [],
                     {'email': 'group_user@host.com',
                      'title': 'Group User'})

        mt.addMember('single_user', 'pw', ['Member'], [],
                     {'email': 'single_user@host.com',
                      'title': 'Single User'})

        mt.addMember('uninvolved_user', 'pw', ['Member'], [],
                     {'email': 'uninvolved_user@host.com',
                      'title': 'Uninvolved User'})

        # Create a group
        self.gt.addGroup('group')
        group = self.gt.getGroupById('group')
        group.addMember('group_user')

        # Create a folder with local roles 
        id = self.portal.invokeFactory('Folder', 'folder')
        folder = self.portal._getOb(id)
        folder.manage_setLocalRoles('single_user', ["Editor"])
        folder.manage_setLocalRoles('group', ["Editor"])
        
        # Create a neutral folder
        self.portal.invokeFactory('Folder', 'folder2')

    def test_creation(self):
        """ """
        folder = self.portal.folder

        # Create the document in the user's folder, where no one else has local
        # roles
        id = self.folder.invokeFactory('Document', 'document')
        doc = self.folder._getOb(id)
        doc.setTitle('Document')
        notify(ObjectInitializedEvent(doc))

        # Test that the users didn't get a message
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        single_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        single_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


        # Now create the document in a folder where other users have the
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

        # Test that the group user received sticky messages
        group_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(group_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the creator of the document does not receive any sticky
        # messages
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


    def test_creation_with_portal_factory(self):
        """ When Archetypes are created via portal_factory, IObjectMovedEvent
            events are thrown a number of times before IObjectInitializedEvent
            is thrown.

            We don't want them to create sticky messages because this is object
            creation, not moving.

            I try here to replicate creation through portal_factory together
            with all the notifications.
        """
        # Create the document in the user's folder, where no one else has local
        # roles
        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        foo = temp_object.portal_factory.doCreate(temp_object, 'foo')
        foo.processForm(values={'title': 'Document Title'})

        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


        # Create the document in the shared folder
        folder = self.portal.folder
        temp_object = folder.restrictedTraverse('portal_factory/Document/tmp_id')
        foo = temp_object.portal_factory.doCreate(temp_object, 'foo')
        foo.processForm(values={'title': 'Document Title'})

        message = u'Document <a href="/plone/folder/foo">Document Title</a> ' \
                  u'created in <a href="/plone/folder"></a>' 
        
        # Test that the standalone user received sticky messages
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')

        # Create a folder with local roles 
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


    def test_deletion(self):
        """ """
        folder = self.portal.folder

        id = folder.invokeFactory('Document', 'document')
        doc = folder._getOb(id)
        doc.setTitle('Document')
        doc.setDescription('Document Description')
        doc.setText('Document Body Text')

        folder.manage_delObjects(['document'])

        message = u'Document <em>Document</em> removed from ' \
                  u'<a href="/plone/folder"></a>'
        # Test that the standalone user received sticky messages
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the group user received sticky messages
        group_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(group_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


    def test_editing(self):
        """ """
        folder = self.portal.folder

        id = folder.invokeFactory('Document', 'document')
        doc = folder._getOb(id)
        doc.setTitle('Document')
        doc.setDescription('Document Description')
        doc.setText('Document Body Text')

        doc.edit(Title='New Title')
        notify(ObjectEditedEvent(doc))

        message = u'Document <a href="/plone/folder/document">Document</a> ' \
                  u'edited in <a href="/plone/folder"></a>'
        # Test that the standalone user received sticky messages
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the group user received sticky messages
        group_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(group_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


    def test_copy(self):
        """ """
        folder = self.portal.folder

        id = self.folder.invokeFactory('Document', 'document')
        doc = self.folder._getOb(id)
        doc.setTitle('Document')
        notify(ObjectInitializedEvent(doc))

        key = self.folder.manage_copyObjects(['document'])

        # Now copy the document in a folder where other users have the
        # 'Editor' role
        folder.manage_pasteObjects(key)

        message = u'Document <a href="/plone/folder/document">Document</a> ' \
                  u'has been copied into <a href="/plone/folder"></a>'
        # Test that the standalone user received sticky messages
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the group user received sticky messages
        group_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(group_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the creator of the document does not receive any sticky
        # messages
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


    def test_move(self):
        """ """
        self.loginAsPortalOwner()

        id = self.portal.folder2.invokeFactory('Document', 'document')
        doc = self.portal.folder2._getOb(id)
        doc.setTitle('Document')
        notify(ObjectInitializedEvent(doc))
        import transaction
        sp = transaction.savepoint()

        key = self.portal.folder2.manage_cutObjects(['document'])

        # Now copy the document in a folder where other users have the
        # 'Editor' role
        folder = self.portal.folder
        folder.manage_pasteObjects(key)

        message = u'Document <em>Document</em> moved into ' \
                  u'<a href="/plone/folder"></a>'
        # Test that the standalone user received sticky messages
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the group user received sticky messages
        group_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(group_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the creator of the document does not receive any sticky
        # message
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        sp.rollback()



    def test_state_change(self):
        """ """
        folder = self.portal.folder
        id = folder.invokeFactory('Document', 'document')
        doc = folder._getOb(id)
        doc.setTitle('Document')

        workflowTool = getToolByName(folder, "portal_workflow")
        workflowTool.doActionFor(doc, "submit")
        # wfs = workflowTool.getWorkflowsFor(doc)
        # for wf in wfs:
        #     wf.notifySuccess(doc, 'submit', None)
        #     notify(ActionSucceededEvent(doc, wf, 'submit', None))

        message = u'The workflow state of Document ' \
                  u'<a href="/plone/folder/document">Document</a> ' \
                  u'in <a href="/plone/folder"></a> has been changed ' \
                  u'to <em>pending</em>'
        # Test that the standalone user received sticky messages
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the group user received sticky messages
        group_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(group_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the creator of the document does not receive any sticky
        # messages
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestChat))
    return suite

from zope.annotation.interfaces import IAnnotations
from Products.Archetypes.event import ObjectEditedEvent
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
        self.gt = gt = getToolByName(self.portal, 'portal_groups')
        self.md = md = getToolByName(self.portal, 'portal_memberdata')

        # Create a new Member
        mt.addMember('group_user', 'pw', ['Member'], [],
                     {'email': 'group_user@host.com',
                      'title': 'Group User'})

        mt.addMember('single_user', 'pw', ['Member'], [],
                     {'email': 'single_user@host.com',
                      'title': 'Single User'})

        mt.addMember('uninvolved_user', 'pw', ['Member'], [],
                     {'email': 'uninvolved_user@host.com',
                      'title': 'Uninvolved User'})

        # Create a group
        self.gt.addGroup('group')
        group = self.gt.getGroupById('group')
        group.addMember('group_user')

        # Create a folder with local roles 
        id = self.portal.invokeFactory('Folder', 'folder')
        folder = self.portal._getOb(id)
        folder.manage_setLocalRoles('single_user', ["Editor"])
        folder.manage_setLocalRoles('group', ["Editor"])
        
        # Create a neutral folder
        self.portal.invokeFactory('Folder', 'folder2')

    def test_creation(self):
        """ """
        folder = self.portal.folder

        # Create the document in the user's folder, where no one else has local
        # roles
        id = self.folder.invokeFactory('Document', 'document')
        doc = self.folder._getOb(id)
        doc.setTitle('Document')
        notify(ObjectInitializedEvent(doc))

        # Test that the users didn't get a message
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        single_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        single_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


        # Now create the document in a folder where other users have the
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

        # Test that the group user received sticky messages
        group_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(group_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the creator of the document does not receive any sticky
        # messages
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


    def test_creation_with_portal_factory(self):
        """ When Archetypes are created via portal_factory, IObjectMovedEvent
            events are thrown a number of times before IObjectInitializedEvent
            is thrown.

            We don't want them to create sticky messages because this is object
            creation, not moving.

            I try here to replicate creation through portal_factory together
            with all the notifications.
        """
        # Create the document in the user's folder, where no one else has local
        # roles
        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        foo = temp_object.portal_factory.doCreate(temp_object, 'foo')
        foo.processForm(values={'title': 'Document Title'})

        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


        # Create the document in the shared folder
        folder = self.portal.folder
        temp_object = folder.restrictedTraverse('portal_factory/Document/tmp_id')
        foo = temp_object.portal_factory.doCreate(temp_object, 'foo')
        foo.processForm(values={'title': 'Document Title'})

        message = u'Document <a href="/plone/folder/foo">Document Title</a> ' \
                  u'created in <a href="/plone/folder"></a>' 
        
        # Test that the standalone user received sticky messages
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')

        # Create a folder with local roles 
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


    def test_deletion(self):
        """ """
        folder = self.portal.folder

        id = folder.invokeFactory('Document', 'document')
        doc = folder._getOb(id)
        doc.setTitle('Document')
        doc.setDescription('Document Description')
        doc.setText('Document Body Text')

        folder.manage_delObjects(['document'])

        message = u'Document <em>Document</em> removed from ' \
                  u'<a href="/plone/folder"></a>'
        # Test that the standalone user received sticky messages
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the group user received sticky messages
        group_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(group_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


    def test_editing(self):
        """ """
        folder = self.portal.folder

        id = folder.invokeFactory('Document', 'document')
        doc = folder._getOb(id)
        doc.setTitle('Document')
        doc.setDescription('Document Description')
        doc.setText('Document Body Text')

        doc.edit(Title='New Title')
        notify(ObjectEditedEvent(doc))

        message = u'Document <a href="/plone/folder/document">Document</a> ' \
                  u'edited in <a href="/plone/folder"></a>'
        # Test that the standalone user received sticky messages
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the group user received sticky messages
        group_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(group_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


    def test_copy(self):
        """ """
        folder = self.portal.folder

        id = self.folder.invokeFactory('Document', 'document')
        doc = self.folder._getOb(id)
        doc.setTitle('Document')
        notify(ObjectInitializedEvent(doc))

        key = self.folder.manage_copyObjects(['document'])

        # Now copy the document in a folder where other users have the
        # 'Editor' role
        folder.manage_pasteObjects(key)

        message = u'Document <a href="/plone/folder/document">Document</a> ' \
                  u'has been copied into <a href="/plone/folder"></a>'
        # Test that the standalone user received sticky messages
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the group user received sticky messages
        group_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(group_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the creator of the document does not receive any sticky
        # messages
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


    def test_move(self):
        """ """
        self.loginAsPortalOwner()

        id = self.portal.folder2.invokeFactory('Document', 'document')
        doc = self.portal.folder2._getOb(id)
        doc.setTitle('Document')
        notify(ObjectInitializedEvent(doc))
        import transaction
        sp = transaction.savepoint()

        key = self.portal.folder2.manage_cutObjects(['document'])

        # Now copy the document in a folder where other users have the
        # 'Editor' role
        folder = self.portal.folder
        folder.manage_pasteObjects(key)

        message = u'Document <em>Document</em> moved into ' \
                  u'<a href="/plone/folder"></a>'
        # Test that the standalone user received sticky messages
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the group user received sticky messages
        group_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(group_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the creator of the document does not receive any sticky
        # message
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        sp.rollback()



    def test_state_change(self):
        """ """
        folder = self.portal.folder
        id = folder.invokeFactory('Document', 'document')
        doc = folder._getOb(id)
        doc.setTitle('Document')

        workflowTool = getToolByName(folder, "portal_workflow")
        workflowTool.doActionFor(doc, "submit")
        # wfs = workflowTool.getWorkflowsFor(doc)
        # for wf in wfs:
        #     wf.notifySuccess(doc, 'submit', None)
        #     notify(ActionSucceededEvent(doc, wf, 'submit', None))

        message = u'The workflow state of Document ' \
                  u'<a href="/plone/folder/document">Document</a> ' \
                  u'in <a href="/plone/folder"></a> has been changed ' \
                  u'to <em>pending</em>'
        # Test that the standalone user received sticky messages
        single_user = self.mt.getMemberById('single_user')
        annotations = IAnnotations(single_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the group user received sticky messages
        group_user = self.mt.getMemberById('group_user')
        annotations = IAnnotations(group_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 1)
        self.assertEquals(sticky_messages.values()[0]['message'], message)
        self.assertEquals(sticky_messages.values()[0]['type'], 'info')

        # Test that the creator of the document does not receive any sticky
        # messages
        uninvolved_user = self.mt.getMemberById('uninvolved_user')
        annotations = IAnnotations(uninvolved_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)

        # Test that the creator of the document does not receive any sticky
        # messages
        current_user = self.mt.getAuthenticatedMember()
        annotations = IAnnotations(current_user)
        sticky_messages = annotations.get(SSMKEY, {})
        self.assertEquals(len(sticky_messages.values()), 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestChat))
    return suite

