__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.db import connection

def get_response(request):
    # Get current user's data and put it into context
    username = request.user.username
    email = request.user.email
    password = request.user.password
    first_name = request.user.first_name
    last_name = request.user.last_name

    context = {'username': username,
               'email': email,
               'password': password,
               'first_name': first_name,
               'last_name': last_name}

    # Get user's friendlist and put it into context.
    c = connection.cursor()
    query = """
            SELECT username, first_name, last_name, email, auth_user.id FROM friendlist
            LEFT JOIN auth_user
            ON friendlist.friend_id = auth_user.id
            WHERE friendlist.user_id = {0}
            """.format(str(request.user.id))
    c.execute(query)
    rows = c.fetchall()
    rows = [{'username':row[0],'first_name':row[1], 'last_name':row[2], 'email':row[3], 'id':row[4]} for row in rows]

    context['friend_list'] = rows

    return render_to_response('bookworm_app/profile/profile.html', context, context_instance=RequestContext(request))