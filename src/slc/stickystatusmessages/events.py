import logging
import utils
from Products.CMFCore.utils import getToolByName
from slc.stickystatusmessages import StickyStatusMessageFactory as _
log = logging.getLogger('slc.stickystatusmessages/events.py')


def object_copied_event(obj, evt):
    """ """
    log.info('object_copied_event')
    folder = obj.aq_parent
    message = _(
                '%s <a href="%s">%s</a> has been copied into <a href="%s">%s</a>' \
                                                % ( obj.portal_type, 
                                                    '/'.join(obj.getPhysicalPath()), 
                                                    obj.Title(), 
                                                    '/'.join(folder.getPhysicalPath()),
                                                    folder.Title())
                )
    utils.set_sticky_status_message(obj, message)


def object_moved_event(obj, evt):
    """ """
    if obj.isTemporary() or not evt.newParent or not evt.oldParent:
        return

    if 'portal_factory' in evt.oldParent.getPhysicalPath():
        return

    log.info('object_moved_event')
    folder = evt.newParent
    message = _(
                '%s <em>%s</em> moved into <a href="%s">%s</a>' \
                                        % ( obj.portal_type, 
                                            obj.Title(), 
                                            '/'.join(folder.getPhysicalPath()),
                                            folder.Title())
                )
    utils.set_sticky_status_message(obj, message)


def object_removed_event(obj, evt):
    """ """
    log.info('object_removed_event')
    folder = obj.aq_parent
    message = _(
                '%s <em>%s</em> removed from <a href="%s">%s</a>' \
                                        % ( obj.portal_type, 
                                            obj.Title(), 
                                            '/'.join(folder.getPhysicalPath()),
                                            folder.Title())
                )
    utils.set_sticky_status_message(obj, message)


def object_created_event(obj, evt):
    """ """
    log.info('object_created_event')
    folder = obj.aq_parent
    message = _(    
                '%s <a href="%s">%s</a> created in <a href="%s">%s</a>' \
                                    % ( obj.portal_type, 
                                        '/'.join(obj.getPhysicalPath()), 
                                        obj.Title(), 
                                        '/'.join(folder.getPhysicalPath()),
                                        folder.Title())
                )
    utils.set_sticky_status_message(obj, message)


def object_edited_event(obj, evt):
    """ """
    log.info('object_edited_event')
    folder = obj.aq_parent
    message = _(
                '%s <a href="%s">%s</a> edited in <a href="%s">%s</a>' \
                                    % ( obj.portal_type, 
                                        '/'.join(obj.getPhysicalPath()), 
                                        obj.Title(), 
                                        '/'.join(folder.getPhysicalPath()),
                                        folder.Title())
                )
    utils.set_sticky_status_message(obj, message)


def object_state_changed_event(obj, evt):
    """ """
    log.info('object_state_changed_event')
    folder = obj.aq_parent
    workflowTool = getToolByName(obj, "portal_workflow")
    chain = workflowTool.getChainFor(obj)
    status = workflowTool.getStatusOf(chain[0], obj)
    state = status["review_state"]
    message = _(
                'The workflow state of %s <a href="%s">%s</a> ' \
                'in <a href="%s">%s</a> has been changed to <em>%s</em>' \
                    % ( obj.portal_type, 
                        '/'.join(obj.getPhysicalPath()), 
                        obj.Title(), 
                        '/'.join(folder.getPhysicalPath()),
                        folder.Title(),
                        state, 
                        )
                )
    utils.set_sticky_status_message(obj, message)


