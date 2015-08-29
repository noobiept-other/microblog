var WebSite;
(function(WebSite) {


var POST_IDENTIFIER = null;
var MESSAGE_CONTAINER = null;


window.addEventListener( 'load', function()
{
$( '#PostDialog' ).on( 'hide.bs.modal', function( event )
    {
    POST_IDENTIFIER = null;
    });
$( '#RemoveDialog' ).on( 'hide.bs.modal', function( event )
    {
    POST_IDENTIFIER = null;
    });

MESSAGE_CONTAINER = document.getElementById( 'MessageContainer' );
});


/**
 * Removes an html element.
 */
WebSite.removeElement = function( element )
{
element.parentNode.removeChild( element );
};


/**
 * @param postIdentifier (optional) Identifier of the post we're replying too. If not provided then its a new independent post.
 */
WebSite.openPostDialog = function( postIdentifier )
{
if ( typeof postIdentifier !== 'undefined' )
    {
    POST_IDENTIFIER = postIdentifier;
    }

$( '#PostDialog' ).modal( 'show' );
};


/**
 * Confirm the post removal.
 */
WebSite.openRemoveDialog = function( postIdentifier )
{
POST_IDENTIFIER = postIdentifier;

$( '#RemoveDialog' ).modal( 'show' );
};


/**
 * Adds a post, and redirects to it.
 */
WebSite.addPost = function( event )
{
var text = document.getElementById( 'PostText' );
var image = document.getElementById( 'PostImage' );
var button = event.target;
var prevButtonText = button.innerHTML;

    // get the relevant data
var data = new FormData();

if ( text.value === '' )
    {
    $( '#PostDialog' ).modal( 'hide' );
    WebSite.addErrorMessage( "Can't post empty messages." );
    return;
    }

else
    {
    data.append( 'text', text.value );
    }

if ( image.files.length > 0 )
    {
    data.append( 'image', image.files[ 0 ] );
    }

if ( POST_IDENTIFIER !== null )
    {
    data.append( 'postIdentifier', POST_IDENTIFIER );
    }


button.innerHTML = 'Posting..';

$.ajax({
        method: 'POST',
        url: '/post/add',
        data: data,
        processData: false,
        contentType: false,
        success: function( data, textStatus, jqXHR )
            {
            window.location = data.url;
            },
        error: function( jqXHR, textStatus, errorThrown )
            {
            console.log( textStatus, errorThrown );
            WebSite.addErrorMessage( 'Failed to send the message.' );

            $( '#PostDialog' ).modal( 'hide' );
            button.innerHTML = prevButtonText;
            }
    });
};


/**
 * Remove the post specified in the 'POST_IDENTIFIER' variable.
 */
WebSite.removePost = function( event )
{
var button = event.target;
var data = new FormData();
var prevButtonText = button.innerHTML;

data.append( 'postIdentifier', POST_IDENTIFIER );

button.innerHTML = 'Removing..';

$.ajax({
        method: 'POST',
        url: '/post/remove?next=' + window.location.pathname,
        data: data,
        processData: false,
        contentType: false,
        success: function( data, textStatus, jqXHR )
            {
            window.location = data.url;
            },
        error: function( jqXHR, textStatus, errorThrown )
            {
            console.log( jqXHR, textStatus, errorThrown );
            WebSite.addErrorMessage( 'Failed to remove the message.' );

            $( '#RemoveDialog' ).modal( 'hide' );
            button.innerHTML = prevButtonText;
            }
    });
};


/**
 * Show a message below the menu.
 */
WebSite.addMessage = function( text )
{
var message = document.createElement( 'p' );

message.className = 'Message';
message.title = 'Click to Remove'
message.addEventListener( 'click', function( event )
    {
    WebSite.removeElement( this );
    });
message.innerHTML = text;

MESSAGE_CONTAINER.appendChild( message );

return message;
};


/**
 * Show an error message below the menu.
 */
WebSite.addErrorMessage = function( text )
{
var message = WebSite.addMessage( text );
message.classList.add( 'Message-error' );

return message;
};


})(WebSite || (WebSite = {}));


/**
 * Make sure the csrf token is sent with every asynchronous request.
 */
jQuery(document).ajaxSend(function(event, xhr, settings)
{
function getCookie(name)
    {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
    }

function sameOrigin(url)
    {
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
    }

function safeMethod(method)
    {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    // Send the token to same-origin, relative URLs only.
    // Send the token only if the method warrants CSRF protection
    // Using the CSRFToken value acquired earlier
if ( !safeMethod(settings.type) && sameOrigin(settings.url) )
    {
    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});