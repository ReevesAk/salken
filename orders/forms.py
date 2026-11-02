from django import forms
from .models import Order


# OrderForm handles the form data to collected for an order places from the store.
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'phone',
            'email',
            'address_line_1',
            'address_line_2',
            'country',
            'state',
            'city',
            'order_note',
        ]


# PaymentForm validates the JSON body the payment page posts to payments()
# after the payment provider approves a transaction.
class PaymentForm(forms.Form):
    orderID = forms.CharField(max_length=20)
    transID = forms.CharField(max_length=100)
    payment_method = forms.CharField(max_length=100)
    status = forms.CharField(max_length=100)
