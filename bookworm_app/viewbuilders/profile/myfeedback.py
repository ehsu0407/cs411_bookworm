__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import connection

def get_response(request):
    # Check if its a POST request, if so, perform appropriate actions
    if(request.method == 'POST'):
        return get_response_post(request)

    context = {}

    # Get feedback lists
    pending_received_list = get_pending_loaned_from_feedback_list(request)
    pending_sent_list = get_pending_loaned_to_feedback_list(request)
    last_10_feedback_list_rcvd = get_last_10_feedback_list_rcvd(request)
    last_10_feedback_list_sent = get_last_10_feedback_list_sent(request)

    # Calculate feedback stats
    avg_feedback_rating = get_avg_feedback_rating(request.user.id)
    amt_feedback_received = get_feedback_count(request.user.id)

    context['pending_received_list'] = pending_received_list
    context['pending_sent_list'] = pending_sent_list
    context['last_10_feedback_list_rcvd'] = last_10_feedback_list_rcvd
    context['last_10_feedback_list_sent'] = last_10_feedback_list_sent

    context['avg_feedback_rating'] = "%.2f" % avg_feedback_rating
    context['amt_feedback_received'] = amt_feedback_received

    return render_to_response('bookworm_app/profile/myfeedback.html', context, context_instance=RequestContext(request))


def get_response_post(request):
    context = {}
    # No post action passed? Error
    if(not 'action' in request.POST):
        return HttpResponseRedirect(reverse('profile_myfeedback'))

    if(request.POST['action'] == 'send_feedback'):
        return get_send_feedback_response(request)


def get_send_feedback_response(request):

    loan_id = int(request.POST['loan_id'])
    rating = int(request.POST['rating'])
    notes = request.POST['notes']

    #TODO: Verify that feedback has not already been given

    # Get user_id feedback is for.
    c = connection.cursor()
    query = """
            SELECT from_user_id, to_user_id FROM loan WHERE id = %s
            """
    c.execute(query, [loan_id])
    rows = c.fetchall()
    row = rows[0]

    if(int(row[0] == request.user.id)):
        to_user_id = row[1]
    elif(int(row[1]) == request.user.id):
        to_user_id = row[0]
    else:
        # Invalid loan_id
        return HttpResponseRedirect(reverse('profile_myfeedback'))


    # Create the feedback
    query = """
            INSERT INTO feedback (loan_id, user_id_from, user_id_to, rating, notes)
            VALUES (%s, %s, %s, %s, %s)
            """
    c.execute(query, [loan_id, request.user.id, to_user_id, rating, notes])

    return HttpResponseRedirect(reverse('profile_myfeedback'))


def get_pending_loaned_from_feedback_list(request):
    """
    Return a list of people that feedback is pending for for books user borrowed.
    :param request:
    :return: List
    """
    c = connection.cursor()

    query = """
            SELECT loan.id as loan_id, loan.status, auth_user.username, media.name FROM loan
            LEFT JOIN
            (
                SELECT * FROM feedback
                WHERE user_id_from = %s
            ) t1
            ON loan.id = t1.loan_id
            LEFT JOIN auth_user
            ON auth_user.id = loan.to_user_id
            LEFT JOIN user_owns_media
            ON user_owns_media.id = loan.unique_media_id
            LEFT JOIN media
            ON user_owns_media.media_id = media.id
            WHERE t1.id is NULL AND from_user_id = %s AND loan.status != 'Pending' AND loan.status != 'Canceled'
            """
    c.execute(query, [request.user.id, request.user.id])
    rows = c.fetchall()

    ret_list = []
    for row in rows:
        data = {'loan_id':row[0], 'status':row[1], 'username':row[2], 'book_name':row[3]}
        ret_list.append(data)

    return ret_list


def get_pending_loaned_to_feedback_list(request):
    """
    Return a list of people that feedback is pending for for books user borrowed.
    :param request:
    :return: List
    """
    c = connection.cursor()

    query = """
            SELECT loan.id as loan_id, loan.status, auth_user.username, media.name FROM loan
            LEFT JOIN
            (
                SELECT * FROM feedback
                WHERE user_id_from = %s
            ) t1
            ON loan.id = t1.loan_id
            LEFT JOIN auth_user
            ON auth_user.id = loan.from_user_id
            LEFT JOIN user_owns_media
            ON user_owns_media.id = loan.unique_media_id
            LEFT JOIN media
            ON user_owns_media.media_id = media.id
            WHERE t1.id is NULL AND to_user_id = %s AND loan.status != 'Pending' AND loan.status != 'Canceled'
            """
    c.execute(query, [request.user.id, request.user.id])
    rows = c.fetchall()

    ret_list = []
    for row in rows:
        data = {'loan_id':row[0], 'status':row[1], 'username':row[2], 'book_name':row[3]}
        ret_list.append(data)

    return ret_list


def get_last_10_feedback_list_rcvd(request):
    """Returns a list of the last 10 feedback lines user recieved"""
    c = connection.cursor()

    query = """
            SELECT loan_id, auth_user.username, rating, notes FROM feedback
            LEFT JOIN auth_user
            ON auth_user.id = feedback.user_id_from
            WHERE user_id_to = %s
            ORDER BY feedback.id DESC
            LIMIT 10
            """
    c.execute(query, [request.user.id])

    rows = c.fetchall()

    ret_list = []
    for row in rows:
        data = {'loan_id':row[0], 'username':row[1], 'rating':row[2], 'notes':row[3]}
        ret_list.append(data)

    return ret_list


def get_last_10_feedback_list_sent(request):
    """Returns a list of the last 10 feedback lines user recieved"""
    c = connection.cursor()

    query = """
            SELECT loan_id, auth_user.username, rating, notes FROM feedback
            LEFT JOIN auth_user
            ON auth_user.id = feedback.user_id_to
            WHERE user_id_from = %s
            ORDER BY feedback.id DESC
            LIMIT 10
            """
    c.execute(query, [request.user.id])

    rows = c.fetchall()

    ret_list = []
    for row in rows:
        data = {'loan_id':row[0], 'username':row[1], 'rating':row[2], 'notes':row[3]}
        ret_list.append(data)

    return ret_list


def get_avg_feedback_rating(user_id):
    """Returns the average feedback rating out of 5 for a user"""
    c = connection.cursor()
    query = """
            SELECT rating FROM feedback
            WHERE feedback.user_id_to = %s
            """
    c.execute(query, [user_id])

    rows = c.fetchall()

    rating_total = 0
    rating_count = 0

    for row in rows:
        rating_count += 1
        rating_total += int(row[0])

    if(rating_count == 0):
        avg_rating = 0.0
    else:
        avg_rating = float(rating_total) / rating_count

    return avg_rating


def get_feedback_count(user_id):
    """Returns the about of feedback a user has received"""
    c = connection.cursor()
    query = """
            SELECT COUNT(*) as count FROM feedback
            WHERE feedback.user_id_to = %s
            """
    c.execute(query, [user_id])
    rows = c.fetchall()

    count = rows[0][0]

    return count