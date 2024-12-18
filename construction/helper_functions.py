from .models import *
from .serializers import *
from django.db.models import Max,Sum
import numpy as np

def disbursement_schedule(loan_id):
    loan_obj = Loan.objects.get(pk=loan_id)
    duration = int(loan_obj.duration)
    total_loan_budget = BudgetMaster.objects.filter(loan_id= loan_id).aggregate(total_loan_budget= Sum('loan_budget'))
    draws_obj_lis = DrawTracking.objects.filter(loan_id=loan_id).values('draw_request','total_released_amount')
    if len(draws_obj_lis) > duration:
        duration = len(draws_obj_lis)

    months = np.arange(0, duration) # Dividing total months into list of months
    normalized_months = (months - duration / 2) / (duration / 10)

    s_curve_values = sigmoid(normalized_months)
    
    scaled_s_curve_values = s_curve_values * total_loan_budget['total_loan_budget']
    total_sum_curve_value = np.sum(scaled_s_curve_values)
    draw_request_dict = {item['draw_request']: item['total_released_amount'] for item in draws_obj_lis}
    output_lis = create_disbursement_schedule_output_json(months, scaled_s_curve_values, draw_request_dict,total_loan_budget['total_loan_budget'])
    return output_lis

def sigmoid(amount):
    return 1 / (1 + np.exp(-amount))

def create_disbursement_schedule_output_json(months,scaled_s_curve_values,draw_request_dict,total_sum_curve_value):
    input_lis = list(zip(months, scaled_s_curve_values))
    
    output_lis = list()
    for i,j in input_lis: 

        output_dictionary = {
            "theoretical": (j/total_sum_curve_value)*100,
            "review_month":i
        }
         # If draw_request (from DrawTracking) matches the review_month
        if i in draw_request_dict:
            output_dictionary["actual"] = (draw_request_dict[i] /total_sum_curve_value)*100  # Add actual key with total_released
        else:
            output_dictionary["actual"] = None
        output_lis.append(output_dictionary)
    return output_lis


def construction_expenditure(loan_id):
    budget_master_lis = BudgetMaster.objects.filter(loan_id=loan_id).values_list('id','uses','loan_budget')
    budget_master_ids = [i[0] for i in budget_master_lis]
    draw_requests = DrawRequest.objects.filter(budget_master__in=budget_master_ids).values('budget_master_id').annotate(total_funded_amount=Sum('funded_amount')).order_by("budget_master_id")
    expenditure_lis =  list()
    for draw in draw_requests:
        for id,uses,loan_budget in budget_master_lis:
            if draw['budget_master_id'] == id:
                expenditure_dict = dict()
                expenditure_dict['released_amount'] = (float(draw['total_funded_amount'])/float(loan_budget))*100 if loan_budget != 0 else 0
                expenditure_dict['uses'] = uses
                expenditure_lis.append(expenditure_dict)
    return expenditure_lis

def contingency_status(loan_id):
    draw_request_obj_lis =  DrawRequest.objects.filter(budget_master_id__loan_id=loan_id,budget_master_id__uses_type='hard_cost').order_by('draw_request')
    total_hard_cost = BudgetMaster.objects.filter(loan_id=loan_id,uses_type='hard_cost').aggregate(Sum('loan_budget'))
    if total_hard_cost:
        total_hard_cost = total_hard_cost.get('loan_budget__sum')
    else:
        total_hard_cost = 0

    try:
        total_owner_contingency = BudgetMaster.objects.get(loan_id=loan_id,uses_type='hard_cost',uses='Owner Contingency')
        owner_contingency_loan_budget = float(total_owner_contingency.loan_budget)
    except BudgetMaster.DoesNotExist:
        owner_contingency_loan_budget = 0
    try:    
        owner_contingency = BudgetMaster.objects.get(loan_id=loan_id,uses='Owner Contingency')
        owner_contingency_id = owner_contingency.id
    except BudgetMaster.DoesNotExist:
        owner_contingency_id = None

    total_released_hard_cost_per_draw = DrawRequest.objects.filter(
        budget_master_id__loan_id=loan_id, 
        budget_master_id__uses_type='hard_cost'
    ).values('draw_request').annotate(total_released_amount=Sum('released_amount')).order_by('draw_request')
    output_lis = list()

    for draw in draw_request_obj_lis:
        response_dict = {}
        for total in total_released_hard_cost_per_draw:
            if draw.budget_master_id == owner_contingency_id:                
                if  total['draw_request'] == draw.draw_request:
                    response_dict['draw'] = int(draw.draw_request)
                    response_dict['contingency'] = owner_contingency_loan_budget  - float(draw.released_amount)
                    response_dict['contingency-percent'] =  ((owner_contingency_loan_budget - float(draw.released_amount))/total_hard_cost)*100
                    response_dict['total-released-direct-cost'] = total['total_released_amount'] 
                    response_dict['total-released-direct-cost-percent'] = (float(total['total_released_amount'])/total_hard_cost)*100
                    output_lis.append(response_dict)
    return output_lis