from django.urls import path
from .views import my_courses, create_payment, payment_success, stripe_webhook, RemoveEnrollmentView

urlpatterns = [
    path('my_courses/', my_courses, name='my_courses'),
    path('create_payment/', create_payment, name='create_payment'),
    path('payment_success/', payment_success, name='payment_success'),
    path('stripe_webhook/', stripe_webhook, name='stripe_webhook'),
    path('remove_enrollment/<int:enrollment_id>/', RemoveEnrollmentView.as_view(), name='remove_enrollment'),
    # другие URL
]
