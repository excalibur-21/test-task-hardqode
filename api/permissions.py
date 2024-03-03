from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404
from .models import Product, Group


class HasAccessToProduct(BasePermission):
    '''
    Пользователю разрешен доступ, если он аутентифицирован и
    - является создателем продукта
    - является участником группы, связанной с продуктом
    '''
    message = "У вас нет доступа к этому продукту"

    def has_permission(self, request, view):
        user = request.user
        product_name = view.kwargs.get('name')
        product = get_object_or_404(Product, name=product_name)

        if not user.is_authenticated:
            return False

        if product.creator == user:
            return True

        return Group.objects.filter(product=product, members=user).exists()