__author__ = 'Eddie'

from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

# viewbuilder imports
from bookworm_app.viewbuilders import register as view_register

from bookworm_app.viewbuilders.profile import profile as view_profile
from bookworm_app.viewbuilders.profile import edit as view_profile_edit
from bookworm_app.viewbuilders.profile import addfriend as view_profile_add_friend
from bookworm_app.viewbuilders.profile import mymedia as view_profile_mymedia
from bookworm_app.viewbuilders.profile import myloan as view_profile_myloan
from bookworm_app.viewbuilders.profile import myfriends as view_profile_myfriends
from bookworm_app.viewbuilders.profile import myreviews as view_profile_myreviews
from bookworm_app.viewbuilders.profile import myfeedback as view_profile_myfeedback

from bookworm_app.viewbuilders import home as view_home
from bookworm_app.viewbuilders import media as view_media
from bookworm_app.viewbuilders import loan as view_loan


# Create your views here.
def landing(request):
    context = {}
    # Redirect the user away from the landing page to his profile if user is already logged in.
    if request.user.is_authenticated():
        return HttpResponseRedirect('/home')
    else:
        return render_to_response('bookworm_app/landing.html', context, context_instance=RequestContext(request))

def register(request):
    return view_register.get_response(request)

@login_required
def home(request):
    return view_home.get_response(request)

@login_required
def profile(request):
    return view_profile.get_response(request)

@login_required
def profile_edit(request):
    return view_profile_edit.get_response(request)

@login_required
def profile_add_friend(request):
    return view_profile_add_friend.get_response(request)

@login_required
def profile_mymedia(request):
    return view_profile_mymedia.get_response(request)

@login_required
def profile_myloan(request):
    return view_profile_myloan.get_response(request)

@login_required
def profile_myfriends(request):
    return view_profile_myfriends.get_response(request)

@login_required
def profile_myreviews(request):
    return view_profile_myreviews.get_response(request)

@login_required
def profile_myfeedback(request):
    return view_profile_myfeedback.get_response(request)

@login_required
def media(request):
    return view_media.get_response(request)

@login_required
def reviews(request):
    context = {}
    return render_to_response('bookworm_app/reviews.html', context, context_instance=RequestContext(request))

@login_required
def loan(request):
    return view_loan.get_response(request)
