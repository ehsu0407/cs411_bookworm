__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import connection

def get_response(request):
    context = {}

    # Default page
    # Get active loans
    c = connection.cursor()
    query = """
            SELECT user_owns_media.id, media.name, auth_user.username, loan.status FROM loan
            LEFT JOIN user_owns_media
            ON user_owns_media.id = loan.unique_media_id
            LEFT JOIN media
            ON media.id = user_owns_media.media_id
            LEFT JOIN auth_user
            ON auth_user.id = loan.from_user_id
            WHERE loan.to_user_id = {0} AND loan.status != 'Complete'
            """.format(request.user.id)
    c.execute(query)
    rows = c.fetchall()
    active_list = [{'id':int(row[0]), 'title':row[1], 'owner':row[2], 'status':row[3]} for row in rows]

    context['active_list'] = active_list
    return render_to_response('bookworm_app/profile/myloan.html', context, context_instance=RequestContext(request))