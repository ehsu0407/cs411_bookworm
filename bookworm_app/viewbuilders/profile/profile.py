__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.db import connection

from bookworm_app.viewbuilders.profile import myfeedback

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

    # Get feedback history and average feedback rating
    avg_feedback_rating = myfeedback.get_avg_feedback_rating(request.user.id)
    feedback_history_list = myfeedback.get_last_10_feedback_list_rcvd(request)

    context['avg_feedback_rating'] = "%.2f" % avg_feedback_rating
    context['feedback_history_list'] = feedback_history_list

    return render_to_response('bookworm_app/profile/profile.html', context, context_instance=RequestContext(request))

