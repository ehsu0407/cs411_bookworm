__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import connection

def get_response(request):
    # Check for post data
    if(request.method == 'POST'):
        return get_post_response(request)

    # Get current user's media data and put it into context
    context = {}
    c = connection.cursor()
    query = """
            SELECT media.id, name, type, genre FROM user_owns_media
            LEFT JOIN media
            ON user_owns_media.media_id = media.id
            WHERE user_owns_media.user_id = {0} AND user_owns_media.active = 1
            """.format(request.user.id)
    c.execute(query)
    rows = c.fetchall()

    media_list = [{'id':row[0], 'title':row[1], 'type':row[2].capitalize(), 'genre':row[3]} for row in rows]
    context['media_list'] = media_list

    return render_to_response('bookworm_app/profile/mymedia.html', context, context_instance=RequestContext(request))

def get_post_response(request):
    context = {}

    # Check if action is passed, if not, just redirect to mymedia
    if('action' not in request.POST):
        return HttpResponseRedirect(reverse('profile_mymedia'))

    # Check which action is required
    if(request.POST['action'] == 'add_media_to_list' and 'media_id' in request.POST):
        # Add media to user owned list

        c = connection.cursor()
        # If invalid media_id, just return to mymedia with an error message.
        if(not is_valid_media(request.POST['media_id'])):
            context['error'] = "Invalid media_id"
            return render_to_response('bookworm_app/profile/mymedia.html', context, context_instance=RequestContext(request))

        # Now verify that media_id was not already added to account
        media_id = int(request.POST['media_id'])
        query = """
                SELECT * FROM  user_owns_media
                WHERE user_id = {0} AND media_id = {1} AND active = 1
                """.format(request.user.id, media_id)
        c.execute(query)
        rows = c.fetchall()
        if(len(rows) > 0):
            # Media already added, return to mymedia with an error message
            context['error'] = "Media already added."
            return render_to_response('bookworm_app/profile/mymedia.html', context, context_instance=RequestContext(request))

        # Otherwise, add media to owned list.
        query = """
                INSERT INTO user_owns_media (user_id, media_id, status, active)
                VALUES ({0}, {1}, 'Available', 1)
                """.format(request.user.id, media_id)
        c.execute(query)

        # Return to the referring page.
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    if(request.POST['action'] == 'remove_media_from_list' and 'media_id' in request.POST):
        # Remove media from user list

        c = connection.cursor()
        # Check if media_id is valid
        if(not is_valid_media(request.POST['media_id'])):
            context['error'] = "Invalid media_id."
            return render_to_response('bookworm_app/profile/mymedia.html', context, context_instance=RequestContext(request))

        # Check if media_id is actually on user's list
        media_id = int(request.POST['media_id'])
        query = """
                SELECT * FROM user_owns_media
                WHERE user_id = {0} AND media_id = {1} AND active = 1
                """.format(request.user.id, media_id)
        c.execute(query)
        rows = c.fetchall()
        if(len(rows) == 0):
            # User does not have this media on his list!
            context['error'] = "User does not have this media added."
            return render_to_response('bookworm_app/profile/mymedia.html', context, context_instance=RequestContext(request))

        # Remove the media from user's list
        query = """
                UPDATE user_owns_media SET active = 0 WHERE user_id = {0} AND media_id = {1}
                """.format(request.user.id, media_id)
        c.execute(query)

        # Return to the referring page.
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

def is_valid_media(media_id):
    """Given a media_id, returns True if it is valid, false otherwise."""
    # Verify the media id first
    try:
        media_id = int(media_id)
    except:
        return False

    c = connection.cursor()
    query = """
            SELECT * FROM media WHERE id = {0}
            """.format(media_id)
    c.execute(query)
    rows = c.fetchall()

    # If invalid media_id, return false
    if(len(rows) == 0):
        return False
    return True