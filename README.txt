Introduction
============

StickyStatusMessages provides persistent status messages.

Normal status messages usually appear when a content item has been affected
(created, edited, removed, state changed etc.) in some way. They appear to the 
user effecting the change.

In the case of StickyStatusMessages, status messages now also appear to other
users, who have an interest (or stake) in the same content item. The other
users who are notified, are the ones with a local 'Editor' role on the object 
being affected.

They will receive a notification message (very similar to the existing status
messages) above the portal content, every time a content item (on which they
have the Editor role) has been changed.

These messages are 'sticky' in the sense that they are persistent. They have to
be removed manually by the user. This is very easy though, you simply click on
the [X] sign on the message itself and it will be removed.


