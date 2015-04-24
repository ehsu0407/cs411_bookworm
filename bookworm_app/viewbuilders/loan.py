import json
from django.http import HttpResponse
from django.template.loader import render_to_string

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
    pending_list = get_pending_loans_list(request.user.id)

    # Get list of books owned by friends
    rows = get_friends_media_list(request)
    media_list = [{'uid':row[0], 'title':row[1], 'type':row[2].capitalize(), 'genre':row[3], 'status':row[4], 'owner':row[5], 'author':row[6], 'description':row[7], 'thumbnail':row[8], 'pending':1 if int(row[0]) in pending_list else 0} for row in rows]

    # Filter out checked out books
    new_media_list = []
    for media in media_list:
        if media['status'] == "Available":
            new_media_list.append(media)

    context['media_list'] = new_media_list[:20]
    return render_to_response('bookworm_app/loan.html', context, context_instance=RequestContext(request))


def get_post_response(request):
    context = {}

    # Check if action is passed, if not, just redirect to loan
    if('action' not in request.POST):
        return HttpResponseRedirect(reverse('loan'))

    # Check which action is required
    if(request.POST['action'] == 'send_loan_request' and 'unique_media_id' in request.POST):
        return get_send_loan_request_response(request)


    elif(request.POST['action'] == 'get_loan_search_results'):
        return get_loan_search_results_response(request)


def get_send_loan_request_response(request):
    context = {}

    # Verify unique_media_id is valid
    rows = get_friends_media_list(request)
    allowed_uids = [row[0] for row in rows]
    unique_media_id = int(request.POST['unique_media_id'])

    if(unique_media_id not in allowed_uids):
        # Invalid or not allowed media uid
        context['error'] = "Invalid media uid."
        return HttpResponse(json.dumps({'status': 'failure'}))

    # Check if there is a pending request for this media already
    c = connection.cursor()
    query = """
            SELECT * FROM loan WHERE unique_media_id = %s AND status = 'Pending' AND to_user_id = %s
            """
    c.execute(query, [unique_media_id, request.user.id])
    rows = c.fetchall()
    if(len(rows) > 0):
        # Already pending
        context['error'] = "Media uid request pending."
        return HttpResponse(json.dumps({'status': 'failure'}))

    # Passed validation, start new borrow request
    create_loan_request(request, unique_media_id)

    # Return to referrer address
    return HttpResponse(json.dumps({'status': 'success'}))


def get_loan_search_results_response(request):
    context = {}

    # Verify the query's length first
    if(len(request.POST['searchquery']) < 3):
        return HttpResponse(json.dumps({'status':'too_short'}))

    c = connection.cursor()

    # Get currently requested list
    pending_list = get_pending_loans_list(request.user.id)

    # Get search results
    query = """
            SELECT thumbnail, name, author, description, auth_user.username, status, user_owns_media.id FROM user_owns_media
            INNER JOIN
            (
                SELECT * FROM media
                WHERE name LIKE %s
            ) t1
            ON t1.id = user_owns_media.media_id
            LEFT JOIN auth_user
            ON auth_user.id = user_owns_media.user_id
            WHERE user_id != %s
            AND user_id IN
            (
            SELECT friend_id FROM friendlist WHERE user_id = %s
            )
            """
    c.execute(query, ['%' + request.POST['searchquery'] + '%', request.user.id,  request.user.id])
    rows = c.fetchall()

    search_results = []
    for row in rows:
        data = {
            'thumbnail':row[0],
            'title':row[1],
            'author':row[2],
            'description':row[3],
            'owner':row[4],
            'status':row[5],
            'pending':1 if int(row[6]) in pending_list else 0,
            'uid':int(row[6])
        }
        search_results.append(data)

    context['media_list'] = search_results

    search_results_html = render_to_string('bookworm_app/loan_search_results.html', context, context_instance=RequestContext(request))
    json_data = {'status': "success", 'search_results_html': search_results_html}

    return HttpResponse(json.dumps(json_data))


def get_pending_loans_list(user_id):
    # Get pending loans status
    c = connection.cursor()
    query = """
            SELECT unique_media_id FROM loan WHERE to_user_id = %s AND status = 'Pending'
            """
    c.execute(query, [user_id])
    rows = c.fetchall()
    pending_list = [int(row[0]) for row in rows]
    return pending_list


def create_loan_request(request, unique_media_id):
    c = connection.cursor()

    # Get media's owner's user id
    query = """
            SELECT user_id FROM user_owns_media WHERE id = %s
            """
    c.execute(query, [unique_media_id])
    rows = c.fetchall()
    from_user_id = rows[0][0]

    # Make the new request
    query = """
            INSERT INTO loan (status, from_user_id, to_user_id, unique_media_id, is_complete)
            VALUES ('Pending', %s, %s, %s, 0)
            """
    c.execute(query, [from_user_id, request.user.id, unique_media_id])
    return 1


def get_friends_media_list(request):
    c = connection.cursor()
    query = """
            SELECT user_owns_media.id, name, type, genre, status, username, author, description, thumbnail FROM user_owns_media
            LEFT JOIN media
            ON media.id = user_owns_media.media_id
            LEFT JOIN auth_user
            ON user_owns_media.user_id = auth_user.id
            WHERE active = 1 AND user_owns_media.user_id IN
            (
                SELECT friend_id FROM friendlist
                WHERE user_id = %s AND status = 1
            )
            """
    c.execute(query, [request.user.id])
    rows = c.fetchall()
    return rows