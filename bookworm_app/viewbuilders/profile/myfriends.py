__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import connection

def get_response(request):
    # Check if its a POST request, if so, perform appropiate actions
    if(request.method == 'POST'):
        return get_response_post(request)

    context = {}

    # Get user's friendlist and put it into context.
    c = connection.cursor()
    query = """
            SELECT username, first_name, last_name, email, auth_user.id, friendlist.status FROM friendlist
            LEFT JOIN auth_user
            ON friendlist.friend_id = auth_user.id
            WHERE friendlist.user_id = {0}
            """.format(str(request.user.id))
    c.execute(query)
    rows = c.fetchall()
    rows = [{'username':row[0],'first_name':row[1], 'last_name':row[2], 'email':row[3], 'id':row[4], 'status':row[5]} for row in rows]

    # Split the friend_list into mutual and pending
    mutual_friends = []
    pending_friends = []

    for row in rows:
        if row['status'] == 1:
            # Mutual
            mutual_friends.append(row)
        else:
            # Pending
            pending_friends.append(row)

    context['friend_list'] = mutual_friends
    context['pending_friend_list'] = pending_friends

    return render_to_response('bookworm_app/profile/myfriends.html', context, context_instance=RequestContext(request))

def get_response_post(request):
    context = {}
    # No post action passed? Error
    if(not 'action' in request.POST):
        context['error'] = "No post action."
        return render_to_response('bookworm_app/profile/myfriends.html', context, context_instance=RequestContext(request))

    if(request.POST['action'] == 'removefriend'):
        context['success'] = 0
        context['action'] = 'removefriend'

        # Verify that friendid is passed
        if(not request.POST.has_key('friend_id')):
            context['error'] = "No friend id passed."
            return render_to_response('bookworm_app/profile/myfriends.html', context, context_instance=RequestContext(request))

        # Verify that friendid is valid
        if(not is_friend(request.user.id, request.POST['friend_id'])):
            context['error'] = "Invalid friend id"
            return render_to_response('bookworm_app/profile/myfriends.html', context, context_instance=RequestContext(request))

        # Remove the friend from the user's friendlist
        c = connection.cursor()
        query = """
                DELETE FROM friendlist WHERE user_id = {0} AND friend_id = {1}
                """.format(request.user.id, request.POST['friend_id'])
        c.execute(query)
        context['success'] = 1
        return HttpResponseRedirect("/profile/myfriends")

def is_friend(user_id, friend_id):
    """Returns true if user_id has friend_id as a friend. False other wise"""
    # Clean inputs
    try:
        user_id = int(user_id)
        friend_id = int(friend_id)
    except:
        return False

    # Create connection and make check
    c = connection.cursor()
    query = """
            SELECT * FROM friendlist WHERE user_id = {0} AND friend_id = {1}
            """.format(user_id, friend_id)
    c.execute(query)
    rows = c.fetchall()
    if(len(rows) > 0):
        return True
    return False
