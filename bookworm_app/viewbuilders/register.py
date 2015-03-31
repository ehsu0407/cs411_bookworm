__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from bookworm_app.forms import RegisterForm

def get_response(request):
    registered = False
    if request.method == 'POST':
        register_form = RegisterForm(data=request.POST)

        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            email = register_form.cleaned_data['email']
            password = register_form.cleaned_data['password']
            first_name = register_form.cleaned_data['first_name']
            last_name = register_form.cleaned_data['last_name']

            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            registered = True

        else:
            print register_form.errors

    else:
        register_form = RegisterForm()

    return render_to_response('bookworm_app/register.html', {'register_form': register_form, 'registered': registered}, context_instance=RequestContext(request))