import json
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from bookworm_app.viewbuilders.shared import book_api_file

__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.db import connection

def get_response(request):
    # Check if post request
    if(request.method == "POST"):
        return get_post_response(request)

    context = {}
    c = connection.cursor()

    # Get list of already owned media
    query = """
            SELECT media_id FROM user_owns_media
            WHERE user_id = {0} AND active = 1
            """.format(request.user.id)
    c.execute(query)
    rows = c.fetchall()
    owned_list = [int(row[0]) for row in rows]

    # Get list of media and add it to context
    query = """
            SELECT * FROM (
                SELECT COUNT(*) as cnt, media_id FROM user_owns_media
                WHERE active = 1
                GROUP BY media_id
                ORDER BY cnt DESC
            ) t1
            LEFT JOIN media
            ON media.id = t1.media_id
            LIMIT 10
            """
    c.execute(query)
    rows = c.fetchall()

    media_list = [
        {
            'id':row[2],
            'type':row[3].capitalize(),
            'genre':row[4],
            'title':row[5],
            'author':row[6],
            'category':row[7],
            'descriptionShort':row[8][:256],
            'descriptionFull':row[8][256:],
            'thumbnail':row[9],
            'isbn13':row[10],
            'language':row[11],
            'pagecount':row[12],
            'publisheddate':row[13],
            'owned':1 if int(row[2]) in owned_list else 0
        } for row in rows
    ]

    context['media_list'] = media_list

    return render_to_response('bookworm_app/media.html', context, context_instance=RequestContext(request))


def get_post_response(request):
    if('action' in request.POST):
        if(request.POST['action'] == 'get_media_search_results'):
            return get_media_search_results_response(request)


def get_media_search_results_response(request):
    """Get response of searching google for a book string"""
    # Verify all needed data is there
    if('searchquery' in request.POST):

        # Verify the query's length first
        if(len(request.POST['searchquery']) < 3):
            return HttpResponse(json.dumps({'status':'too_short'}))

        # Determine if the book is already owned. If not owned or not found in database, allow add to library
        # Get list of already owned media
        c = connection.cursor()
        query = """
                SELECT isbn13 FROM user_owns_media
                LEFT JOIN media
                ON media.id = user_owns_media.media_id
                WHERE user_id = {0} AND active = 1
                """.format(request.user.id)
        c.execute(query)
        rows = c.fetchall()
        owned_list = [row[0] for row in rows]

        search_results = book_api_file.search(request.POST['searchquery'], '', '', '', '', 20);
        # print search_results

        results_list = []
        for book in search_results:
            vol_info = book['volumeInfo']
            isbn13 = None

            # Try to get the isbn13
            if('industryIdentifiers' not in vol_info):
                # Skip books without isbns
                continue

            else:
                for id in vol_info['industryIdentifiers']:
                    if(id['type'] == 'ISBN_13'):
                        isbn13 = id['identifier']

            if(isbn13 == None):
                continue

            book_data = {
                'title':vol_info['title'] if 'title' in vol_info else '',
                'author':vol_info['authors'][0] if 'authors' in vol_info else '',
                'descriptionShort':vol_info['description'][:256] if 'description' in vol_info else '',
                'descriptionFull':vol_info['description'][256:] if 'description' in vol_info else '',
                'isbn13':isbn13,
                'thumbnail_url':vol_info['imageLinks']['thumbnail'] if 'imageLinks' in vol_info else '',
                'owned':1 if isbn13 in owned_list else 0
            }
            results_list.append(book_data)

        context = {'results_list':results_list, 'searchquery':request.POST['searchquery']}

        search_results_html = render_to_string('bookworm_app/media_search_results.html', context, context_instance=RequestContext(request))
        json_data = {'status': "success", 'search_results_html': search_results_html}

        return HttpResponse(json.dumps(json_data))
