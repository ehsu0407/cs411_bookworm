from django.conf.urls import patterns, include, url
from django.contrib import admin

from bookworm_app import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cs411_bookworm.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'bookworm_app.views.landing', name='landing'),

    url(r'^home/', 'bookworm_app.views.home', name='home'),

    url(r'^profile/addfriend', 'bookworm_app.views.profile_add_friend', name='add_friend'),
    url(r'^profile/edit', 'bookworm_app.views.profile_edit', name='profile_edit'),
    url(r'^profile/mymedia', 'bookworm_app.views.profile_mymedia', name='profile_mymedia'),
    url(r'^profile/myfriends', 'bookworm_app.views.profile_myfriends', name='profile_myfriends'),
    url(r'^profile/myloan', 'bookworm_app.views.profile_myloan', name='profile_myloan'),
    url(r'^profile/myreviews', 'bookworm_app.views.profile_myreviews', name='profile_myreviews'),
    url(r'^profile/myfeedback', 'bookworm_app.views.profile_myfeedback', name='profile_myfeedback'),
    url(r'^profile/', 'bookworm_app.views.profile', name='profile'),

    url(r'^media/', 'bookworm_app.views.media', name='media'),
    url(r'^reviews/', 'bookworm_app.views.reviews', name='reviews'),
    url(r'^loan/', 'bookworm_app.views.loan', name='loan'),
    url(r'^register/', 'bookworm_app.views.register', name='register'),
    url(r'^accounts/login/', 'django.contrib.auth.views.login', name="login"),
    url(r'^accounts/logout/', 'django.contrib.auth.views.logout', {'next_page': '/'}, name="logout"),
    url(r'^admin/', include(admin.site.urls)),
)
