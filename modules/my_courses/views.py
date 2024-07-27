import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Enrollment
from modules.course.models import Article
from modules.course.models import Cart
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.models import User
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse


stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


@login_required
def create_payment(request):
    if request.method == 'POST':
        amounts_str = request.POST.getlist('amounts[]')
        descriptions = request.POST.getlist('descriptions[]')
        course_ids = request.POST.getlist('course_ids[]')

        logger.debug(f"Received amounts: {amounts_str}, descriptions: {descriptions}, course_ids: {course_ids}")

        if not amounts_str or not descriptions or not course_ids:
            return JsonResponse({'error': 'Total amount, descriptions, and course_ids are required'}, status=400)

        try:
            amounts = [int(float(amount.replace(',', '.')) * 100) for amount in amounts_str]
        except ValueError:
            return JsonResponse({'error': 'Invalid amount format'}, status=400)

        if len(descriptions) != len(course_ids) or len(amounts) != len(course_ids):
            return JsonResponse({'error': 'Mismatch between number of descriptions, amounts, and course_ids'},
                                status=400)

        line_items = []
        for description, amount, course_id in zip(descriptions, amounts, course_ids):
            try:
                course = Article.objects.get(id=course_id)
            except Article.DoesNotExist:
                return JsonResponse({'error': f'Course with ID {course_id} does not exist'}, status=400)

            line_items.append({
                'price_data': {
                    'currency': 'rub',
                    'product_data': {
                        'name': description,
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            })

        try:
            success_url = request.build_absolute_uri('/payment_success/?course_ids=' + ','.join(course_ids))
            cancel_url = request.build_absolute_uri('/payment_cancelled/')
            logger.debug(f"Success URL: {success_url}")

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'course_ids': ','.join(course_ids),
                    'user_id': request.user.id,
                }
            )
            return JsonResponse({'paymentUrl': checkout_session.url})
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def payment_success(request):
    logger.debug("Payment success endpoint called")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request GET parameters: {request.GET}")

    if request.method == 'GET':
        course_ids_str = request.GET.get('course_ids')
        logger.debug(f"Received course_ids (raw): {course_ids_str}")

        if not course_ids_str:
            messages.error(request, 'Course IDs are missing.')
            return redirect('my_courses')

        course_ids = course_ids_str.split(',')
        logger.debug(f"Parsed course_ids: {course_ids}")

        courses = Article.objects.filter(id__in=course_ids)
        logger.debug(f"Retrieved courses: {[course.id for course in courses]}")

        if not courses.exists():
            messages.error(request, 'One or more courses are invalid.')
            return redirect('my_courses')

        for course in courses:
            enrollment, created = Enrollment.objects.get_or_create(user=request.user, article=course)

            if created:
                messages.success(request, f'Вы успешно записаны на курс: {course.title}')
                logger.info(f"User {request.user.id} enrolled in course {course.id}")
            else:
                messages.info(request, f'Вы уже записаны на курс: {course.title}')
                logger.info(f"User {request.user.id} was already enrolled in course {course.id}")

            Cart.objects.filter(user=request.user, product_id=course.id).delete()

        return redirect('my_courses')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        course_ids = session['metadata']['course_ids'].split(',')
        user_id = session['metadata']['user_id']
        logger.debug(f"Webhook received for user_id: {user_id}, course_ids: {course_ids}")

        try:
            user = User.objects.get(id=user_id)
            courses = Article.objects.filter(id__in=course_ids)
            logger.debug(f"Retrieved courses from webhook: {[course.id for course in courses]}")

            for course in courses:
                enrollment, created = Enrollment.objects.get_or_create(user=user, article=course)

                if created:
                    logger.info(f'Enrollment created for user {user_id} in course {course.id}')
                else:
                    logger.info(f'User {user_id} is already enrolled in course {course.id}')

            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f'Error processing webhook event: {e}')
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'status': 'skipped'})


@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('article')

    # Логирование всех записей
    logger.debug(f"Enrollments for user {request.user.id}: {[enrollment.article.id for enrollment in enrollments]}")

    return render(request, 'my_courses/my_courses.html', {'enrollments': enrollments})


@method_decorator(login_required, name='dispatch')
class RemoveEnrollmentView(View):
    def post(self, request, enrollment_id):
        try:
            enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
            article_id = enrollment.article.id
            enrollment.delete()

            return JsonResponse({
                'status': 'success',
                'article_id': article_id
            })
        except Enrollment.DoesNotExist:
            return JsonResponse({'error': 'Enrollment does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

