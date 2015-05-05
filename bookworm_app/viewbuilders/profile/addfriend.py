import json
from django.http import HttpResponse
from django.template.loader import render_to_string

__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.db import connection

def get_response(request):
    context = {}
    error_message = ""
    c = connection.cursor()

    # Check if request type is post
    if(request.method == 'POST'):

        if(request.POST['action'] == "get_friend_search_results"):

            # Verify the query's length first
            if(len(request.POST['searchquery']) <= 0):
                return HttpResponse(json.dumps({'status':'too_short'}))

            # Get user list and put it into context.
            query = """
                    SELECT id, username, first_name, last_name, email
                    FROM auth_user
                    WHERE auth_user.id NOT IN
                    (
                        SELECT friend_id FROM friendlist
                        WHERE user_id = %s
                    )
                    AND id != %s AND username LIKE %s
                    """
            c.execute(query, [request.user.id, request.user.id, '%' + request.POST['searchquery'] + '%'])
            rows = c.fetchall()

            user_list = [{'id':row[0], 'username':row[1],'first_name':row[2], 'last_name':row[3], 'email':row[4]} for row in rows]

            context['user_list'] = user_list
            context['searchquery'] = request.POST['searchquery']
            search_results_html = render_to_string('bookworm_app/profile/addfriend_search_results.html', context, context_instance=RequestContext(request))
            json_data = {'status': "success", 'search_results_html': search_results_html}

            return HttpResponse(json.dumps(json_data))

        if(request.POST['action'] == "add_friend" and request.POST["friend_id"] is not None):
            friend_id = int(request.POST['friend_id'])

            # Verify if valid user id
            query = "SELECT * FROM auth_user WHERE id = {0}".format(friend_id)
            c.execute(query)
            rows = c.fetchall()
            if(len(rows) > 0):

                # Verify not already on friends list.
                query = "SELECT * FROM friendlist WHERE user_id = {0} and friend_id = {1}".format(request.user.id, friend_id)
                c.execute(query)
                rows = c.fetchall()
                if(len(rows) == 0):

                    # Check if friend_id already requested user as a friend. If so, automatically set as mutual friends
                    query = "SELECT * FROM friendlist WHERE user_id = {1} and friend_id = {0}".format(request.user.id, friend_id)
                    c.execute(query)
                    rows = c.fetchall()

                    if(len(rows) == 0):
                        # Create new friend request
                        query = "INSERT INTO friendlist (user_id, friend_id, status) VALUES ({0}, {1}, {2})".format(request.user.id, friend_id, 0)
                        c.execute(query)

                    else:
                        # Create new mutual friend
                        query = """
                                UPDATE friendlist SET status = 1 WHERE user_id = {0} AND friend_id = {1}
                                """.format(friend_id, request.user.id)
                        c.execute(query)

                        query = "INSERT INTO friendlist (user_id, friend_id, status) VALUES ({1}, {0}, 1)".format(friend_id, request.user.id)
                        c.execute(query)

                    json_data = {'status': "success"}
                    return HttpResponse(json.dumps(json_data))

                else:
                    error_message = "User already added as a friend!"
            else:
                error_message = "Invalid user id."

    context['error_message'] = error_message

    return render_to_response('bookworm_app/profile/addfriend.html', context, context_instance=RequestContext(request))