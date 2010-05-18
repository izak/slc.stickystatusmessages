function close_all_sticky_message() {
    var path = window.location.href;
    if (path.indexOf("portal_factory") != -1) {
        path = path.split('/portal_factory')[0];
    }
    else if (path.indexOf("credentials_cookie_auth/require_login") != -1) {
        path = path.split('/credentials_cookie_auth/require_login')[0];
    }
    path += '/@@StickyStatusMessagesAJAXView/delete_all_messages';
    jQuery.ajax({
        url: path,
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert('Error: could not permanently remove the messsages. Please try again later.'+path);
            jQuery("div#sticky-status-messages").fadeOut(500);
        },
        success: function() {
            jQuery("div#sticky-status-messages").fadeOut(500);
        }
    });
}


function close_sticky_message(mid) {
    var path = window.location.href;
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
            alert('Error: could not permanently remove the messsage. Please try again later.'+path);
            jQuery("dt[mid="+mid+"]").parent().fadeOut(500);
        },
        success: function() {
            jQuery("dt[mid="+mid+"]").parent().fadeOut(500);
        }
    });

}
