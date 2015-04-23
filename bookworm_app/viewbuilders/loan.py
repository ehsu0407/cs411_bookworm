__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import connection

def get_response(request):
    context = {}

    # Check if post request
    if(request.method == "POST"):
        return get_post_response(request)

    # Default page
    # Get pending loans status
    c = connection.cursor()
    query = """
            SELECT unique_media_id FROM loan WHERE to_user_id = {0} AND status = 'Pending'
            """.format(request.user.id)
    c.execute(query)
    rows = c.fetchall()
    pending_list = [int(row[0]) for row in rows]

    # Get list of books owned by friends
    rows = get_friends_media_list(request)
    media_list = [{'uid':row[0], 'title':row[1], 'type':row[2].capitalize(), 'genre':row[3], 'status':row[4], 'owner':row[5], 'pending':1 if int(row[0]) in pending_list else 0} for row in rows]

    context['media_list'] = media_list
    return render_to_response('bookworm_app/loan.html', context, context_instance=RequestContext(request))


def get_post_response(request):
    context = {}

    # Check if action is passed, if not, just redirect to mymedia
    if('action' not in request.POST):
        return HttpResponseRedirect(reverse('loan'))

    # Check which action is required
    if(request.POST['action'] == 'send_loan_request' and 'unique_media_id' in request.POST):

        # Verify unique_media_id is valid
        rows = get_friends_media_list(request)
        allowed_uids = [row[0] for row in rows]
        unique_media_id = int(request.POST['unique_media_id'])

        if(unique_media_id not in allowed_uids):
            # Invalid or not allowed media uid
            context['error'] = "Invalid media uid."
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        # Check if there is a pending request for this media already
        c = connection.cursor()
        query = """
                SELECT * FROM loan WHERE unique_media_id = {0} AND status = 'Pending'
                """.format(unique_media_id)
        c.execute(query)
        rows = c.fetchall()
        if(len(rows) > 0):
            # Already pending
            context['error'] = "Media uid request pending."
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        # Passed validation, start new borrow request
        create_loan_request(request, unique_media_id)

        # Return to referrer address
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

def create_loan_request(request, unique_media_id):
    c = connection.cursor()

    # Get media's owner's user id
    query = """
            SELECT user_id FROM user_owns_media WHERE id = {0}
            """.format(unique_media_id)
    c.execute(query)
    rows = c.fetchall()
    from_user_id = rows[0][0]

    # Make the new request
    query = """
            INSERT INTO loan (status, from_user_id, to_user_id, unique_media_id, is_complete)
            VALUES ('Pending', {0}, {1}, {2}, 0)
            """.format(from_user_id, request.user.id, unique_media_id)
    c.execute(query)
    return 1

def get_friends_media_list(request):
    c = connection.cursor()
    query = """
            SELECT user_owns_media.id, name, type, genre, status, username FROM user_owns_media
            LEFT JOIN media
            ON media.id = user_owns_media.media_id
            LEFT JOIN auth_user
            ON user_owns_media.user_id = auth_user.id
            WHERE user_owns_media.user_id IN
            (
                SELECT friend_id FROM friendlist
                WHERE user_id = {0} AND status = 1
            )
            """.format(request.user.id)
    c.execute(query)
    rows = c.fetchall()
    return rows