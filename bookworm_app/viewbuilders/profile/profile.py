__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.db import connection
from django.contrib.auth.models import User

from bookworm_app.viewbuilders.profile import myfeedback

def get_response(request):

    # Check if userid is passed in GET, if not, use current user's id
    user = request.user
    if('userid' in request.GET):
        user_list = User.objects.filter(id=int(request.GET['userid']))
        if(len(user_list) >= 1):
            user = user_list[0]

    # Get current user's data and put it into context
    username = user.username
    email = user.email
    password = user.password
    first_name = user.first_name
    last_name = user.last_name

    context = {'username': username,
               'email': email,
               'password': password,
               'first_name': first_name,
               'last_name': last_name,
               'is_cur_user': 1 if user.id == request.user.id else 0}

    # Get user statistics
    library_size = get_count_library_size(user.id)
    num_media_loaned_out = get_count_media_loaned_out(user.id)
    num_media_borrowing = get_count_media_borrowing(user.id)
    num_total_media_loaned_out = get_count_total_media_loaned_out(user.id)
    num_total_media_borrowing = get_count_total_media_borrowing(user.id)

    context['library_size'] = library_size
    context['num_media_loaned_out'] = num_media_loaned_out
    context['num_media_borrowing'] = num_media_borrowing
    context['num_total_media_loaned_out'] = num_total_media_loaned_out
    context['num_total_media_borrowing'] = num_total_media_borrowing

    # Get feedback history and average feedback rating
    avg_feedback_rating = myfeedback.get_avg_feedback_rating(user.id)
    feedback_history_list = myfeedback.get_last_10_feedback_list_rcvd(user.id)

    context['avg_feedback_rating'] = "%.2f" % avg_feedback_rating
    context['feedback_history_list'] = feedback_history_list

    return render_to_response('bookworm_app/profile/profile.html', context, context_instance=RequestContext(request))


def get_count_library_size(user_id):
    """Returns the size of the user's library"""
    c = connection.cursor()
    query = """
            SELECT COUNT(*) as count FROM user_owns_media
            WHERE user_id = %s
            """
    c.execute(query, [user_id])
    rows = c.fetchall()
    count = rows[0][0]

    return count


def get_count_media_loaned_out(user_id):
    """Returns the number of media the user currently has loaned out"""
    c = connection.cursor()
    query = """
            SELECT COUNT(*) as count FROM user_owns_media
            WHERE user_id = %s AND status = 'Checked Out'
            """
    c.execute(query, [user_id])
    rows = c.fetchall()
    count = rows[0][0]

    return count


def get_count_media_borrowing(user_id):
    """Returns the number of media the user currently is loaning"""
    c = connection.cursor()
    query = """
            SELECT COUNT(*) as count FROM loan
            WHERE to_user_id = %s AND status != 'Returned' AND status != 'Rejected' AND status != 'Pending'
            """
    c.execute(query, [user_id])
    rows = c.fetchall()
    count = rows[0][0]

    return count


def get_count_total_media_loaned_out(user_id):
    """Returns the number of media the user has ever loaned out"""
    c = connection.cursor()
    query = """
            SELECT COUNT(*) as count FROM loan
            WHERE from_user_id = %s AND status != 'Rejected' AND status != 'Pending'
            """
    c.execute(query, [user_id])
    rows = c.fetchall()
    count = rows[0][0]

    return count


def get_count_total_media_borrowing(user_id):
    """Returns the number of media the user has loaned"""
    c = connection.cursor()
    query = """
            SELECT COUNT(*) as count FROM loan
            WHERE to_user_id = %s AND status != 'Rejected' AND status != 'Pending'
            """
    c.execute(query, [user_id])
    rows = c.fetchall()
    count = rows[0][0]

    return count
