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

    return render_to_response('bookworm_app/profile/profile.html', context, context_instance=RequestContext(request))