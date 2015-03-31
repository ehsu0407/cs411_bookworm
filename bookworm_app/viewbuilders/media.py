__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.db import connection

def get_response(request):
    context = {}
    c = connection.cursor()

    # Get list of already owned media
    query = """
            SELECT media_id FROM user_owns_media
            WHERE user_id = {0}
            """.format(request.user.id)
    c.execute(query)
    rows = c.fetchall()
    owned_list = [int(row[0]) for row in rows]

    # Get list of media and add it to context
    query = """
            SELECT * FROM media
            """
    c.execute(query)
    rows = c.fetchall()

    media_list = [{'id':row[0], 'type':row[1].capitalize(), 'genre':row[2], 'title':row[3], 'owned':1 if int(row[0]) in owned_list else 0} for row in rows]
    context['media_list'] = media_list

    return render_to_response('bookworm_app/media.html', context, context_instance=RequestContext(request))