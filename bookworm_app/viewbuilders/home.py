__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response

def get_response(request):
    # Get current user's data and put it into context
    context = {}

    context['username'] = request.user.username

    return render_to_response('bookworm_app/home.html', context, context_instance=RequestContext(request))