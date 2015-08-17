var WebSite;
(function(WebSite) {


/**
 * Removes an html element.
 */
WebSite.removeElement = function( element )
{
element.parentNode.removeChild( element );
};


})(WebSite || (WebSite = {}));