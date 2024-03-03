from django.urls import path
from .views import ProductAccessAPIView, LessonListView, ProductListView, GroupListAPIView

urlpatterns = [
    path('product/<str:name>/', ProductAccessAPIView.as_view()),
    path('products-list/', ProductListView.as_view()),
    path('lessons/<str:name>/', LessonListView.as_view()),
    path('groups/', GroupListAPIView.as_view())
]
