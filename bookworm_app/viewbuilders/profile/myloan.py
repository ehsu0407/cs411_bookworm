__author__ = 'Eddie'

from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import connection

def get_response(request):
    # Check if its a POST request, if so, perform appropiate actions
    if(request.method == 'POST'):
        return get_response_post(request)

    context = {}

    # Default page
    # Get active loans
    c = connection.cursor()
    query = """
            SELECT user_owns_media.id, media.name, auth_user.username, loan.status, loan.id FROM loan
            LEFT JOIN user_owns_media
            ON user_owns_media.id = loan.unique_media_id
            LEFT JOIN media
            ON media.id = user_owns_media.media_id
            LEFT JOIN auth_user
            ON auth_user.id = loan.from_user_id
            WHERE loan.to_user_id = {0} AND loan.is_complete != 1
            """.format(request.user.id)
    c.execute(query)
    rows = c.fetchall()
    active_list = [{'uid':row[0], 'title':row[1], 'owner':row[2], 'status':row[3], 'loan_id':row[4]} for row in rows]

    # Get Loan Requests
    query = """SELECT user_owns_media.id, media.name, auth_user.username, loan.status, loan.id FROM loan
            LEFT JOIN user_owns_media
            ON user_owns_media.id = loan.unique_media_id
            LEFT JOIN media
            ON media.id = user_owns_media.media_id
            LEFT JOIN auth_user
            ON auth_user.id = loan.to_user_id
            WHERE loan.from_user_id = {0} AND loan.is_complete != 1
             """.format(request.user.id)

    c.execute(query)
    rows = c.fetchall()
    loan_requests_list = [{'uid':row[0], 'title':row[1], 'requester':row[2], 'status':row[3], 'loan_id':row[4]} for row in rows]

    # Get Complete Requests
    query = """SELECT user_owns_media.id, media.name, u1.username, u2.username, loan.status, loan.id FROM loan
            LEFT JOIN user_owns_media
            ON user_owns_media.id = loan.unique_media_id
            LEFT JOIN media
            ON media.id = user_owns_media.media_id
            LEFT JOIN auth_user as u1
            ON u1.id = loan.from_user_id
            LEFT JOIN auth_user as u2
            ON u2.id = loan.to_user_id
            WHERE (loan.from_user_id = {0} OR loan.to_user_id = {0}) AND loan.is_complete = 1
             """.format(request.user.id)

    c.execute(query)
    rows = c.fetchall()
    complete_requests_list = [{'uid':row[0], 'title':row[1], 'user_from':row[2], 'user_to':row[3], 'status':row[4], 'loan_id':row[5]} for row in rows]
    complete_requests_list = sorted(complete_requests_list, key=lambda x:x['uid'], reverse=True)

    context['active_list'] = active_list
    context['loan_requests_list'] = loan_requests_list
    context['complete_requests_list'] = complete_requests_list

    return render_to_response('bookworm_app/profile/myloan.html', context, context_instance=RequestContext(request))


def get_response_post(request):
    context = {}
    # No post action passed? Error
    if(not 'action' in request.POST):
        context['error'] = "No post action."
        return render_to_response('bookworm_app/profile/myloan.html', context, context_instance=RequestContext(request))

    if(request.POST['action'] == 'approveloanrequest'):
        loan_id = int(request.POST['loan_id'])

        c = connection.cursor()
        if(request.POST['confirm'] == 'True'):
            # Loan approved
            query = """
                    UPDATE loan SET status = 'Approved' WHERE id = {0}
                    """.format(loan_id)
            c.execute(query)

            # Set the media as checked out
            query = "SELECT unique_media_id FROM loan WHERE id = {0}".format(loan_id)
            c.execute(query)
            rows = c.fetchall()
            row = rows[0]

            uid = int(row[0])

            query = "UPDATE user_owns_media SET status = 'Checked Out' WHERE id = {0}".format(uid)
            c.execute(query)

        else:
            # Loan rejected
            query = """
                    UPDATE loan SET status = 'Rejected', is_complete = 1 WHERE id = {0}
                    """.format(loan_id)
            c.execute(query)

    if(request.POST['action'] == 'updateloan_received'):
        loan_id = int(request.POST['loan_id'])

        c = connection.cursor()
        query = """
                UPDATE loan SET status = 'Received' WHERE id = {0}
                """.format(loan_id)
        c.execute(query)

    if(request.POST['action'] == 'loanrequest_returned'):
        loan_id = int(request.POST['loan_id'])

        c = connection.cursor()
        query = """
                UPDATE loan SET status = 'Returned', is_complete = 1 WHERE id = {0}
                """.format(loan_id)
        c.execute(query)

        # Set the media as available
        query = "SELECT unique_media_id FROM loan WHERE id = {0}".format(loan_id)
        c.execute(query)
        rows = c.fetchall()
        row = rows[0]

        uid = int(row[0])

        query = "UPDATE user_owns_media SET status = 'Available' WHERE id = {0}".format(uid)
        c.execute(query)

    return HttpResponseRedirect("/profile/myloan")