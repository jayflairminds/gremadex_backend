from rest_framework import serializers 
from .models import * 

class PaymentSerializer(serializers.ModelSerializer): 

    class Meta:
        model = Payments 
        fields = "__all__"

class SubscriptionPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscriptionPlan
        fields = "__all__"
