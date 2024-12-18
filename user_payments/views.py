from rest_framework.views import APIView,View
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import stripe
from django.conf import settings
from rest_framework import status
import os

import stripe.error
from core import *
from .serializers import *
from django.utils import timezone
import datetime
from users.permissions import subscription
# from user_payments.helper_functions import payment_status

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        input_json = request.data
        tier = input_json.get('tier')
        price_id = input_json.get('price_id')
        promo_code = input_json.get('promo_code')
        price_dict = stripe.Price.retrieve(price_id)
        product_id = price_dict.get('product')
        product_dict = stripe.Product.retrieve(product_id)
        tier = product_dict.get('name')
        #localhost = http://localhost:5173
        #localhost = https://glasdex.com
        # Creating Stripe Checkout session
        try:
            subscription_data = {}            
            # Customize for Trial tier
            if tier == 'Trial':
                subscription_data={
                    "trial_settings": {"end_behavior": {"missing_payment_method": "cancel"}},
                    "trial_period_days": 30,
                }
            if promo_code is not None and promo_code != '':
                try:                
                    valid_promo_code = stripe.Coupon.retrieve(promo_code).valid
                except Exception as e:
                    return Response({'response':'No such coupon available'},status=status.HTTP_404_NOT_FOUND)

                if promo_code is not None and valid_promo_code :
                    discount = [{
                        'coupon': promo_code,  # Replace with your coupon ID
                    }]
            else:
                discount = []
            print(discount)
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                discounts=discount,
                mode='subscription',
                subscription_data = subscription_data,
                payment_method_collection="if_required" if tier in  ('Trial','Gremadex Trial') else "always",
                success_url=f"{os.getenv('FRONTEND_URL')}/success?" + 'sessionid={CHECKOUT_SESSION_ID}',
                cancel_url=f"{os.getenv('FRONTEND_URL')}/cancel?" + 'sessionid={CHECKOUT_SESSION_ID}'
            )
            return Response({'sessionId': session.id,'status':'session_created',"session":session})
        except stripe.error.StripeError as e:
            return Response({"error",str(e)})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
class StripeWebhook(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.WEBHOOK_SIGNING_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return Response({'error': str(e)}, status=400)
        event_type = event['type']
        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            print('Payment succeeded!')            
        elif event_type == 'customer.subscription.trial_will_end':
            print('Subscription trial will end')
        elif event_type == 'customer.subscription.created':
            print('Subscription created %s', event.id)
        elif event_type == 'customer.subscription.updated':
            print('Subscription created %s', event.id)
        elif event_type == 'customer.subscription.deleted':
            print('Subscription canceled: %s', event.id)
        return Response({'status': 'success'}, status=200)

class CreatePaymentIntent(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        try:
            input_json = request.data
            payment_method_id = input_json.get('payment_method_id')
            session_id = input_json.get('session_id')
            session = stripe.checkout.Session.retrieve(session_id)
            amount = session.amount_total
            currency = session.currency
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                payment_method=payment_method_id,
                # payment_method='pm_card_visa',
                # confirmation_method='manual',
                confirm=True,
                automatic_payment_methods={
                    'enabled': True,
                    'allow_redirects': 'never'  # This will disable redirects
                }
            )
            return Response(payment_intent)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
class ProductList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        product_list = stripe.Product.list()
        price_list = stripe.Price.list()
        print(request.user, list(Payments.objects.values_list('user_id',flat=True)))
        if request.user.id in list(Payments.objects.values_list('user_id',flat=True)) :
            for product in product_list:
                for price in price_list:
                    if price['id'] == product['default_price']:
                        product["unit_amount"] = float(price['unit_amount'])/100 if price['unit_amount'] != 0 else 0
                        product['currency'] = price['currency'].upper()
                        product['type'] = product['type'].capitalize()
            updated_product_list = [i for i in product_list['data'] if i.name not in ('Trial','Gremadex Trial')]
            product_list['data'] = updated_product_list
            return Response(product_list,status=status.HTTP_200_OK)
        
        else:
            for product in product_list:
                for price in price_list:
                    if price['id'] == product['default_price']:
                        product["unit_amount"] = int(price['unit_amount'])/100 if price['unit_amount'] != 0 else 0
                        product['currency'] = price['currency'].upper()
                        product['type'] = product['type'].capitalize()
            # product_list = sorted(product_list, key=lambda price: price['unit_amount'])
            return Response(product_list,status=status.HTTP_200_OK)

class PricesList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        input_params = request.query_params
        limit = input_params.get('limit')
        product = input_params.get('product')
        response = stripe.Price.list(limit=limit,product=product)
        return Response(response,status=status.HTTP_200_OK) 
    
class SavePaymentDetails(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self,request):

        data = request.data
        data["stripe_session_id"] = data.get('session_id')
        
        try:
            # Retrieve the checkout session using the session ID
            stripe_session = stripe.checkout.Session.retrieve(data['stripe_session_id']) 

            # Retrieve the subscription ID from the checkout session
            subscription_id = stripe_session.get('subscription') 

             # Now retrieve the subscription details
            subscription = stripe.Subscription.retrieve(subscription_id)

            # Retrieve the product details to get the tier (product name)
            product_id = subscription.plan.product
            product = stripe.Product.retrieve(product_id) 
            # Extract the tier name (product name)
            tier = product.name 

            # Prepare the data to store in the database
            payment_data = {
                'stripe_session_id': data['stripe_session_id'],
                'stripe_subscription_id': subscription.id,  # Subscription ID
                'subscription_status': subscription.status,  # Status (active, canceled, etc.)
                'tier': tier,
                'account_creation_date': datetime.datetime.fromtimestamp(subscription.created),  # Account creation date (timestamp)
                'renew_date': datetime.datetime.fromtimestamp(subscription.current_period_end),  # Renewal date (timestamp)
                'transaction_fee': subscription.application_fee_percent if subscription.application_fee_percent else 0,  # Transaction fee (if applicable)
                'description': subscription.description if subscription.description else '',  # Subscription description
                'currency': stripe_session.currency,  # Currency
                'amount': stripe_session.amount_total,  # Total amount
                'payment_status': stripe_session.payment_status,  # Payment status,
                'user': request.user.id,
                'current_date':timezone.now()
            }
  
            serializer = PaymentSerializer(data=payment_data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Payment data saved successfully","Payment":serializer.data},status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except stripe.error.StripeError as e:
             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# Currently this API is not in use -- As this would require more parameters and clarity on product creation.    
class CreateDeleteProduct(APIView):

    permission_classes = [IsAuthenticated] 

    def post(self,request):
        
      
        name = request.data.get('name')
        description = request.data.get('description', None)
        price = request.data.get('price')
        currency = request.data.get('currency')
    
        if not name or not price:
            return Response({"error": "Name and price are required fields"}, status=400)
        
        # # Convert price to cents
        # price_in_cents = int(float(price) * 100) 

        try:
             # Create the product in Stripe
            product = stripe.Product.create(
                name=name,
                active=True,
                shippable=False,
                unit_label="subscription",
                images = [],
                metadata= {},
                url = None,
                
            )

             # Create the price for the product
            price_obj = stripe.Price.create(
                product=product.id,
                unit_amount=price,  # price in cents
                currency='usd',
                recurring={"interval": "month"},  # for monthly subscription

            ) 

            return Response({
                "message": "Product created successfully",
                "product_id": product.id,
                "price_id": price_obj.id,
                "product_name": product.name,
                "default_price":price_obj.id,
                "price_amount": price_obj.unit_amount,  # Convert back to dollars
            }, status=201)
        
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=400)

    # Product cannot be deleted as stripe doesn't allow it,products can only be archived as prices are associated with it.
    def delete(self,request,product_id):

        # try:
            print(f"Attempting to delete product with ID: {product_id}")
            print(stripe.Product.retrieve(product_id))
                    # Deactivate the product
            stripe.Product.modify(product_id, active=False)
            stripe.Product.delete(product_id)
        
            return Response({"message": f"Product {product_id} deactivated successfully"}, status=200)
           

class InsertDeleteRetrieveUpdateSubscription(APIView):

    permission_classes = [IsAuthenticated] 

    def post(self,request):

        data = request.data
        data['created_at'] = timezone.now()
        data['updated_at'] = timezone.now()
        serializer = SubscriptionPlanSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,id):

        if not id:
            return Response({"message":"id is required"},status=status.HTTP_400_BAD_REQUEST)
        
        my_instance = SubscriptionPlan.objects.get(id=id)
        my_instance.delete()
        return Response({"message": f"record {id} deleted successfully"}, status=200) 
    
    def get(self,request):

        input_params = request.query_params
        tier = input_params.get('tier') 
        

        if tier:
             if SubscriptionPlan.objects.filter(tier=tier).exists():
                my_instance = SubscriptionPlan.objects.get(tier=tier)
                serializer = SubscriptionPlanSerializer(my_instance)
             else:
                 return Response({"error": f"No subscription plan found for tier: {tier}"},status=status.HTTP_404_NOT_FOUND)
        else:
            my_instance = SubscriptionPlan.objects.all()
            serializer = SubscriptionPlanSerializer(my_instance,many=True)

        return Response(serializer.data,status=201) 
    
    def put(self,request,id):

        try:
            my_instance = SubscriptionPlan.objects.get(pk=id) 
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Subscription plan not found"}, status=status.HTTP_404_NOT_FOUND) 
        
        data = request.data 
        data['updated_at'] = timezone.now() 
        serializer = SubscriptionPlanSerializer(my_instance,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PromoCode(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        input_json = request.data

        coupon_id = input_json.get("coupon_id")  # The ID of the coupon you want to create
        applies_to = input_json.get("applies_to")
        percent_off = input_json.get("percent_off")

        try:
            # Check if the coupon already exists
            existing_coupon = stripe.Coupon.retrieve(coupon_id)
            return Response({'error': 'Coupon with that ID already exists', 'coupon': existing_coupon}, status=status.HTTP_409_CONFLICT)
        except stripe.error.InvalidRequestError:
            # Coupon does not exist, create a new one
            coupon = stripe.Coupon.create(
                duration="forever",
                id=coupon_id,
                percent_off=percent_off,
                applies_to={'products': applies_to}
            )
            return Response({'response': 'Coupon created', 'coupon': coupon}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        try:
            coupon_delete = stripe.Coupon.delete(id)
            return Response({'response': 'Coupon deleted', 'coupon': coupon_delete}, status=status.HTTP_200_OK)
        except stripe.error.InvalidRequestError as e:
            # Handle the case where the coupon does not exist
            if 'No such coupon' in str(e):
                return Response({'error': 'Coupon does not exist'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 
    
class UpgradeSubscriptionView(APIView):
    permission_classes = [IsAuthenticated, subscription]

    def post(self, request):
        # Get the subscription and new price ID from the request data
        subscription_id = request.data.get('subscription_id')
        new_price_id = request.data.get('new_price_id')

        # Validate the input
        if not subscription_id or not new_price_id:
            return Response({"error": "Subscription ID and new price ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the current subscription
            subscription = stripe.Subscription.retrieve(subscription_id)

            # Upgrade the subscription and apply prorated credit
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription['items']['data'][0].id,
                    "price": new_price_id,  # Set new plan price ID here
                }],
                proration_behavior="create_prorations",  # Apply remaining balance
            )
             # Retrieve the updated subscription to verify
            subscription_after_update = stripe.Subscription.retrieve(subscription_id)

            # Check the new price_id to confirm it's now set to Premium
            current_price_id = subscription_after_update['items']['data'][0]['price']['id']
            print('current_price_id',current_price_id)

            # Retrieve the latest invoice, which should reflect the prorated amount
            latest_invoice_id = updated_subscription['latest_invoice']
            print("latest_invoice_id",latest_invoice_id)
            latest_invoice = stripe.Invoice.retrieve(latest_invoice_id) if latest_invoice_id else None
            print(latest_invoice.amount_due,latest_invoice.amount_paid)
            print(latest_invoice['lines']['data'][0]['price']['id'])
            # Check if there's a remaining balance in the latest invoice
            if latest_invoice and latest_invoice['amount_due'] > 0:
                # Create a checkout session to collect the remaining payment
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price': latest_invoice['lines']['data'][0]['price']['id'],  # The price ID from the invoice
                        'quantity': 1,
                    }],
                    mode='subscription',
                    success_url=f"{os.getenv('FRONTEND_URL')}/success?" + 'sessionid={CHECKOUT_SESSION_ID}',
                    cancel_url=f"{os.getenv('FRONTEND_URL')}/cancel?" + 'sessionid={CHECKOUT_SESSION_ID}'
                )
                # Return session ID to the client so they can pay the remaining amount
                return Response({"session":session}, status=status.HTTP_200_OK)

            # If no remaining balance, simply return the updated subscription
            return Response({
                "updated_subscription": updated_subscription,
                "latest_invoice": latest_invoice
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            # Handle Stripe error
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        

def get_subscription_details(subscription_id):
    return stripe.Subscription.retrieve(subscription_id)

class ValidatePromoCode(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        input_json = request.data
        promo_code = input_json.get('promo_code')
        try:                
            valid_promo_code = stripe.Coupon.retrieve(promo_code)
            return Response({"response":valid_promo_code})
        except Exception as e:
            return Response({'response':'No such coupon available'},status=status.HTTP_404_NOT_FOUND)
