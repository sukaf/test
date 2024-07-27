from django.views.generic import ListView,\
    DetailView, CreateView, UpdateView,\
    DeleteView, RedirectView
from django.shortcuts import render,\
    redirect, get_object_or_404
from .models import Article, Category, Comment, Cart, ArticleVariation
from .forms import ArticleCreateForm, ArticleUpdateForm,\
    CommentCreateForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from ..services.mixins import AuthorRequiredMixin
from django.http import JsonResponse
from django.db.models import Sum, Q, Prefetch, F, Case, When, IntegerField
from django.core.paginator import Paginator
from taggit.models import Tag

from .models import Rating
from ..services.utils import get_client_ip
from django.views.generic import View
import json
import random
from django.db.models import Count
import traceback
from django.contrib.postgres.search import SearchVector,\
    SearchQuery, SearchRank
from django.core.serializers.json import DjangoJSONEncoder
from modules.teacher.models import Teacher
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.core.serializers import serialize
from modules.my_courses.models import Enrollment


class ArticleListView(ListView):
    model = Article
    template_name = 'course/articles_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('teacher').prefetch_related(
            Prefetch('variations')
        )
        teacher_id = self.request.GET.get('teacher')
        if teacher_id and teacher_id != 'all':
            queryset = queryset.filter(teacher__id=teacher_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        context['teachers'] = Teacher.objects.all()

        cart_items, total_quantity = self.get_cart_items_and_total_quantity()
        context['cart_article_ids'] = list(cart_items.values_list('product_id', flat=True))
        context['total_quantity'] = total_quantity

        # Retrieve purchased article IDs
        purchased_article_ids = self.get_purchased_article_ids()
        context['purchased_article_ids'] = purchased_article_ids

        article_variations = {
            article.id: [
                {
                    'id': variation.id,
                    'name': variation.name,
                    'price': str(variation.price),
                    'image_url': variation.image.url if variation.image else ''
                }
                for variation in article.variations.all()
            ]
            for article in context['articles']
        }
        context['article_variations'] = json.dumps(article_variations, cls=DjangoJSONEncoder)

        return context

    def get_cart_items_and_total_quantity(self):
        if self.request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
            cart_items = Cart.objects.filter(session_key=self.request.session.session_key)

        total_quantity = cart_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
        return cart_items, total_quantity

    def get_purchased_article_ids(self):
        if self.request.user.is_authenticated:
            return list(Enrollment.objects.filter(user=self.request.user).values_list('article_id', flat=True))
        return []


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'course/articles_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Article.objects.prefetch_related('tags', 'variations')

    def get_similar_articles(self, obj):
        article_tags_ids = obj.tags.values_list('id', flat=True)
        similar_articles = Article.objects.filter(tags__in=article_tags_ids).exclude(id=obj.id)
        similar_articles = similar_articles.annotate(related_tags=Count('tags')).order_by('-related_tags')
        similar_articles_list = list(similar_articles)
        random.shuffle(similar_articles_list)
        return similar_articles_list[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        context['title'] = article.title
        context['form'] = CommentCreateForm()
        context['similar_articles'] = self.get_similar_articles(article)

        cart_items, total_quantity = self.get_cart_items_and_total_quantity()
        context['total_quantity'] = total_quantity
        context['cart_article_ids'] = list(cart_items.values_list('product_id', flat=True))

        article_variations = {
            article.id: [
                {
                    'id': variation.id,
                    'name': variation.name,
                    'price': str(variation.price),
                    'image_url': variation.image.url if variation.image else None
                }
                for variation in article.variations.all()
            ]
        }
        context['article_variations'] = json.dumps(article_variations, cls=DjangoJSONEncoder)

        return context

    def get_cart_items_and_total_quantity(self):
        if self.request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
            cart_items = Cart.objects.filter(session_key=self.request.session.session_key)

        total_quantity = cart_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
        return cart_items, total_quantity


class ArticleByCategoryListView(ListView):
    model = Article
    template_name = 'course/articles_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        queryset = Article.objects.filter(category__slug=self.category.slug).prefetch_related('variations')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Статьи из категории: {self.category.title}'

        cart_items, total_quantity = self.get_cart_items_and_total_quantity()
        context['total_quantity'] = total_quantity

        article_variations = {
            article.id: [
                {
                    'id': variation.id,
                    'name': variation.name,
                    'price': str(variation.price),
                    'image_url': variation.image.url if variation.image else None
                }
                for variation in article.variations.all()
            ]
            for article in context['articles']
        }
        context['article_variations'] = json.dumps(article_variations, cls=DjangoJSONEncoder)

        return context

    def get_cart_items_and_total_quantity(self):
        if self.request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
            cart_items = Cart.objects.filter(session_key=self.request.session.session_key)

        total_quantity = cart_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
        return cart_items, total_quantity


class ArticleUpdateView(AuthorRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Представление: обновления материала на сайте
    """
    model = Article
    template_name = 'course/articles_update.html'
    context_object_name = 'article'
    form_class = ArticleUpdateForm
    login_url = 'home'
    success_message = 'Материал был успешно обновлен'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Обновление статьи: {self.object.title}'
        return context

    def form_valid(self, form):
        form.instance.updater = self.request.user
        form.save()
        return super().form_valid(form)


class ArticleDeleteView(AuthorRequiredMixin, DeleteView):
    """
    Представление: удаления материала
    """
    model = Article
    success_url = reverse_lazy('home')
    context_object_name = 'article'
    template_name = 'course/articles_delete.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление статьи: {self.object.title}'
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentCreateForm

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_invalid(self, form):
        if self.is_ajax():
            return JsonResponse({'error': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.article_id = self.kwargs.get('pk')
        comment.author = self.request.user
        comment.parent_id = form.cleaned_data.get('parent')
        comment.save()

        if self.is_ajax():
            return JsonResponse({
                'is_child': comment.is_child_node(),
                'id': comment.id,
                'author': comment.author.username,
                'parent_id': comment.parent_id,
                'time_create': comment.time_create.strftime('%Y-%b-%d %H:%M:%S'),
                'avatar': comment.author.profile.avatar.url,
                'content': comment.content,
                'get_absolute_url': comment.author.profile.get_absolute_url()
            }, status=200)

        return redirect(comment.article.get_absolute_url())

    def handle_no_permission(self):
        return JsonResponse({'error': 'Необходимо авторизоваться для добавления комментариев'}, status=400)


class ArticleByTagListView(ListView):
    model = Article
    template_name = 'course/articles_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    tag = None

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs['tag'])
        queryset = Article.objects.filter(tags__slug=self.tag.slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Статьи по тегу: {self.tag.name}'

        # Получаем идентификаторы статей, которые находятся в корзине
        if self.request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=self.request.user)
            total_quantity = Cart.objects.filter(user=self.request.user).aggregate(Sum('quantity'))['quantity__sum'] or 0
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.save()
                session_key = self.request.session.session_key
            cart_items = Cart.objects.filter(session_key=session_key)
            total_quantity = Cart.objects.filter(session_key=session_key).aggregate(Sum('quantity'))['quantity__sum'] or 0

        context['total_quantity'] = total_quantity

        cart_article_ids = [item.product.id for item in cart_items]
        context['cart_article_ids'] = cart_article_ids

        # Сериализуем вариации статей для передачи в JavaScript
        article_variations = {}
        for article in context['articles']:
            variations = list(article.variations.all())
            article_variations[article.id] = [
                {
                    'id': variation.id,
                    'name': variation.name,
                    'price': variation.price,
                    'image_url': variation.image.url if variation.image else None
                }
                for variation in variations
            ]
        # Используем DjangoJSONEncoder для правильной сериализации
        context['article_variations'] = json.dumps(article_variations, cls=DjangoJSONEncoder)

        return context


class ArticleSearchResultView(ListView):
    model = Article
    context_object_name = 'articles'
    paginate_by = 10
    allow_empty = True
    template_name = 'course/articles_list.html'

    def get_queryset(self):
        query = self.request.GET.get('do')
        queryset = self.model.objects.filter(
            Q(title__icontains=query) | Q(full_description__icontains=query)
        ).annotate(
            relevance=(
                (Case(When(title__icontains=query, then=1), default=0, output_field=IntegerField()) +
                 Case(When(full_description__icontains=query, then=1), default=0, output_field=IntegerField()))
            )
        ).order_by('-relevance')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Результаты поиска: {self.request.GET.get("do")}'

        cart_items, total_quantity = self.get_cart_items_and_total_quantity()
        context['total_quantity'] = total_quantity
        context['cart_article_ids'] = list(cart_items.values_list('product_id', flat=True))

        article_variations = {
            article.id: [
                {
                    'id': variation.id,
                    'name': variation.name,
                    'price': str(variation.price),
                    'image_url': variation.image.url if variation.image else ''
                }
                for variation in article.variations.all()
            ]
            for article in context['articles']
        }
        context['article_variations'] = json.dumps(article_variations, cls=DjangoJSONEncoder)

        return context

    def get_cart_items_and_total_quantity(self):
        if self.request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.save()
                session_key = self.request.session.session_key
            cart_items = Cart.objects.filter(session_key=session_key)

        total_quantity = cart_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
        return cart_items, total_quantity


# class RatingCreateView(View):
#     model = Rating
#
#     def post(self, request, *args, **kwargs):
#         article_id = request.POST.get('article_id')
#         value = int(request.POST.get('value'))
#         ip_address = get_client_ip(request)
#         user = request.user if request.user.is_authenticated else None
#
#         rating, created = self.model.objects.get_or_create(
#             article_id=article_id,
#             ip_address=ip_address,
#             defaults={'value': value, 'user': user},
#         )
#
#         if not created:
#             if rating.value == value:
#                 rating.delete()
#                 return JsonResponse({'status': 'deleted', 'rating_sum': rating.article.get_sum_rating()})
#             else:
#                 rating.value = value
#                 rating.user = user
#                 rating.save()
#                 return JsonResponse({'status': 'updated', 'rating_sum': rating.article.get_sum_rating()})
#         return JsonResponse({'status': 'created', 'rating_sum': rating.article.get_sum_rating()})


class ArticleBySignedUser(LoginRequiredMixin, ListView):
    """
    Представление, выводящее список статей авторов, на которые подписан текущий пользователь
    """
    model = Article
    template_name = 'course/articles_list.html'
    context_object_name = 'articles'
    login_url = 'login'
    paginate_by = 10

    def get_queryset(self):
        authors = self.request.user.profile.following.values_list('id', flat=True)
        queryset = self.model.objects.all().filter(author__id__in=authors)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Статьи авторов'
        return context


def get_cart_items(user=None, session_key=None):
    if user:
        cart_items = Cart.objects.filter(user=user).select_related('product', 'variation')
    else:
        cart_items = Cart.objects.filter(session_key=session_key).select_related('product', 'variation')

    total_quantity = sum(item.quantity for item in cart_items)
    total_price = sum(item.quantity * item.price for item in cart_items)

    articles_details = [
        {
            'article_id': item.product.id,
            'title': item.product.title,
            'thumbnail': item.product.thumbnail.url if item.product.thumbnail else None,
            'short_description': item.product.short_description,
            'status': item.product.status,
            'course_type': item.variation.name if item.variation else '',
            'start_course': item.product.start_course,
            'lessons': item.product.count,
            'len_course': item.product.len_course,
            'price_month': item.variation.price if item.variation else item.product.price,
            'price_total': (item.variation.price if item.variation else item.product.price) * item.product.len_course_time * item.quantity if item.product.len_course_time else 0,
            'tariff': item.variation.name if item.variation else '',
            'quantity': item.quantity,
            'total_price': item.price * item.quantity
        }
        for item in cart_items
    ]

    return articles_details, total_quantity, total_price


class CartAddView(View):
    def post(self, request):
        try:
            variation_id = request.POST.get('variation_id')
            article_id = request.POST.get('article_id')

            if variation_id:
                variation = get_object_or_404(ArticleVariation, id=variation_id)
                article = variation.article
            elif article_id:
                article = get_object_or_404(Article, id=article_id)
                variation = None
            else:
                return JsonResponse({'error': 'No article or variation specified'}, status=400)

            if request.user.is_authenticated:
                user = request.user
                cart_item, created = Cart.objects.get_or_create(
                    user=user, product=article,
                    defaults={'variation': variation, 'price': variation.price if variation else article.price}
                )
            else:
                session_key = request.session.session_key or request.session.create()
                cart_item, created = Cart.objects.get_or_create(
                    session_key=session_key, product=article,
                    defaults={'variation': variation, 'price': variation.price if variation else article.price}
                )

            if not created:
                cart_item.quantity += 1
                cart_item.save()

            cart_items, total_quantity, total_price = get_cart_items(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key if not request.user.is_authenticated else None
            )

            return JsonResponse({
                'status': 'added',
                'article_id': article.id,
                'total_quantity': total_quantity,
                'total_price': total_price,
                'cart_items': cart_items
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class CartView(View):
    def get(self, request):
        session_key = request.session.session_key or request.session.create()

        articles_details, total_quantity, total_price = get_cart_items(
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key if not request.user.is_authenticated else None
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'total_quantity': total_quantity,
                'total_price': total_price,
                'cart_items': articles_details
            })

        return render(request, 'course/cart.html', {
            'cart_items': articles_details,
            'total_quantity': total_quantity,
            'total_price': total_price
        })

    def post(self, request):
        pass  # Обработка POST-запроса (добавление или удаление товара из корзины)


class CartCheckView(View):
    def get(self, request, article_id):
        if request.user.is_authenticated:
            user = request.user
            in_cart = Cart.objects.filter(user=user, product_id=article_id).exists()
            already_purchased = Enrollment.objects.filter(user=user, article_id=article_id).exists()
        else:
            session_key = request.session.session_key or request.session.create()
            in_cart = Cart.objects.filter(session_key=session_key, product_id=article_id).exists()
            already_purchased = False  # Анонимные пользователи не могут иметь приобретённые курсы

        return JsonResponse({'in_cart': in_cart, 'already_purchased': already_purchased})


class CartRemoveView(View):
    def post(self, request, article_id):
        try:
            if request.user.is_authenticated:
                cart_item = get_object_or_404(Cart, user=request.user, product_id=article_id)
            else:
                session_key = request.session.session_key or request.session.create()
                cart_item = get_object_or_404(Cart, session_key=session_key, product_id=article_id)

            cart_item.delete()

            cart_items, total_quantity, total_price = get_cart_items(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key if not request.user.is_authenticated else None
            )

            return JsonResponse({
                'status': 'removed',
                'article_id': article_id,
                'total_quantity': total_quantity,
                'total_price': total_price,
                'cart_items': cart_items
            })

        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart item does not exist'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



