__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response
from bookworm_app.forms import RegisterForm
from django.contrib.auth import update_session_auth_hash

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

    # Check if request type is post, if so, verify and update user profile.
    updated = False
    if request.method == 'POST':
        register_form = RegisterForm(data=request.POST)

        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            email = register_form.cleaned_data['email']
            password = register_form.cleaned_data['password']
            first_name = register_form.cleaned_data['first_name']
            last_name = register_form.cleaned_data['last_name']

            # Update all user attributes
            user = request.user
            user.username = username
            user.email = email
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            updated = True
            update_session_auth_hash(request, user)

        else:
            print register_form.errors

    else:
        register_form = RegisterForm(initial={'username': username,
                                              'email': email,
                                              'first_name': first_name,
                                              'last_name': last_name})

    context['updated'] = updated
    context['register_form'] = register_form
    return render_to_response('bookworm_app/profile/edit.html', context, context_instance=RequestContext(request))