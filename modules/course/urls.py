from django.urls import path

from .views import (
    ArticleListView, ArticleDetailView, ArticleByCategoryListView, ArticleUpdateView,
    ArticleDeleteView, CommentCreateView, ArticleByTagListView, ArticleSearchResultView,
    ArticleBySignedUser, CartAddView, CartView, CartCheckView, CartRemoveView
)

urlpatterns = [
    path('', ArticleListView.as_view(), name='home'),
    path('cart/', CartAddView.as_view(), name='cart'),
    path('cart/remove/<int:article_id>/', CartRemoveView.as_view(), name='cart_remove'),
    path('cart/check/<int:article_id>/', CartCheckView.as_view(), name='cart_check'),
    path('category/<str:slug>/', ArticleByCategoryListView.as_view(), name="articles_by_category"),
    path('cart_detail/', CartView.as_view(), name='cart_detail'),
    path('articles/<str:slug>/update/', ArticleUpdateView.as_view(), name='articles_update'),
    path('articles/<str:slug>/delete/', ArticleDeleteView.as_view(), name='articles_delete'),
    path('articles/<str:slug>/', ArticleDetailView.as_view(), name='articles_detail'),
    path('articles/signed/', ArticleBySignedUser.as_view(), name='articles_by_signed_user'),
    path('articles/<int:pk>/comments/create/', CommentCreateView.as_view(), name='comment_create_view'),
    path('articles/tags/<str:tag>/', ArticleByTagListView.as_view(), name='articles_by_tags'),
    path('search/', ArticleSearchResultView.as_view(), name='search'),

]

