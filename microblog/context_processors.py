from microblog.models import POST_MAX_LENGTH


def post( request ):
    return {
        'post_max_length': POST_MAX_LENGTH
    }