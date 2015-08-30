from enum import IntEnum


class MessageType( IntEnum ):
    normal = 0
    error = 1


def get_messages( request, context ):
    """
        Checks the session to see if there are messages to be displayed, and if so adds them to the context object (don't forget, it changes the object from where its called).
    """
    messages = request.session.get( 'MESSAGES' )

    if messages:

        context[ 'MESSAGES' ] = messages
        request.session[ 'MESSAGES' ] = []


def add_message( request, message, messageType= MessageType.normal ):
    """
        Add a message to the session (can be called multiple times).
        All the messages will be displayed the next time a page is loaded (when get_messages() is called).
    """
    if 'MESSAGES' not in request.session:
        request.session[ 'MESSAGES' ] = []

        # careful, if you have a list in the session, append operations aren't saved
        # need to copy the list to variable, do the operation and then add to the session
    messages = request.session[ 'MESSAGES' ]
    messages.append({
        'message': message,
        'type': messageType.name
    })
    request.session[ 'MESSAGES' ] = messages
