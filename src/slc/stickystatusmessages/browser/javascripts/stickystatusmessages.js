function close_sticky_message(mid) {
    var path = window.location.pathname;
    if (path.indexOf("portal_factory") != -1) {
        path = path.split('/portal_factory')[0];
    }
    else if (path.indexOf("credentials_cookie_auth/require_login") != -1) {
        path = path.split('/credentials_cookie_auth/require_login')[0];
    }
    path += '/@@StickyStatusMessagesAJAXView/delete_message';
    jQuery.ajax({
        url: path,
        cache: false,
        async: false,
        data: {
            message_id: mid,
            },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert('Error: could not permanently remove the messsage. Please try again later.');
            jQuery("dt[mid="+mid+"]").parent().fadeOut(500);
        },
        success: function() {
            jQuery("dt[mid="+mid+"]").parent().fadeOut(500);
        }
    });

}
