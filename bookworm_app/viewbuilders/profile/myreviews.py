__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import connection

def get_response(request):
    context = {}

    return render_to_response('bookworm_app/profile/myreviews.html', context, context_instance=RequestContext(request))
