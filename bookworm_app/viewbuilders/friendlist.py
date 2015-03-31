__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.db import connection

def get_response(request):
    # Check if its a POST request, if so, perform appropiate actions
    if(request.method == 'POST'):
        return get_response_post(request)

    # Check the attributes and determine if an action is listed.
    if(request.GET.has_key('action')):

        # Action listed! Determine what action is listed and perform the appropiate instructions
        if(request.GET['action'] == 'removefriend'):
            return get_response_removefriend(request)

def get_response_post(request):
    context = {}
    # No post action passed? Error
    if(not 'action' in request.POST):
        context['error'] = "No post action."
        return render_to_response('bookworm_app/friendlist.html', context, context_instance=RequestContext(request))

    if(request.POST['action'] == 'removefriend'):
        context['success'] = 0
        context['action'] = 'removefriend'

        # Verify that friendid is passed
        if(not request.POST.has_key('friend_id')):
            context['error'] = "No friend id passed."
            return render_to_response('bookworm_app/friendlist.html', context, context_instance=RequestContext(request))

        # Verify that friendid is valid
        if(not is_friend(request.user.id, request.POST['friend_id'])):
            context['error'] = "Invalid friend id"
            return render_to_response('bookworm_app/friendlist.html', context, context_instance=RequestContext(request))

        # Remove the friend from the user's friendlist
        c = connection.cursor()
        query = """
                DELETE FROM friendlist WHERE user_id = {0} AND friend_id = {1}
                """.format(request.user.id, request.POST['friend_id'])
        c.execute(query)
        context['success'] = 1
        return HttpResponseRedirect("/profile") #TODO: Change this to render friendlist page and move friendlist from profile to friendlist page


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

def get_response_removefriend(request):
    context = {}
    context['action'] = 'removefriend'

    # Verify that friendid is passed
    if(not request.GET.has_key('friendid')):
        context['error'] = "No friend id passed."
        return render_to_response('bookworm_app/friendlist.html', context, context_instance=RequestContext(request))

    # Verify that friendid is valid
    if(not is_friend(request.user.id, request.GET['friendid'])):
        context['error'] = "Invalid friend id"
        return render_to_response('bookworm_app/friendlist.html', context, context_instance=RequestContext(request))

    # Get friend name
    c = connection.cursor()
    query = """
            SELECT first_name, last_name FROM auth_user WHERE id = {0}
            """.format(request.GET['friendid'])
    c.execute(query)
    rows = c.fetchall()
    friend_name = rows[0][0] + ' ' + rows[0][1]

    context['user_id'] = request.user.id
    context['friend_id'] = request.GET['friendid']
    context['friend_name'] = friend_name

    return render_to_response('bookworm_app/friendlist.html', context, context_instance=RequestContext(request))
