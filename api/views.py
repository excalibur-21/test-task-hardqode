from rest_framework import status, generics, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Count
from .models import Product, Group, Lesson
from .serializers import ProductSerializer, LessonSerializer, ProductListSerializer, GroupSerializer
from .services import add_user_to_fewest_group
from django.db.models import Subquery
from .permissions import HasAccessToProduct


class ProductAccessAPIView(generics.RetrieveAPIView):
    '''
    Предоставляет информацию о продукте если пользователь имеет доступ
    Доступ определяется нахождением в группе с продуктом
    Если пользователь не имеет доступ - добавляет в группу и сортирует их
    '''
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'name'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.handle_access(instance, serializer, request.user)

    def handle_access(self, instance, serializer, user):
        if not user.is_authenticated:
            return Response({"error": "Пользователь не аутентифицирован"}, status=status.HTTP_401_UNAUTHORIZED)

        if instance.creator == user or Group.objects.filter(product=instance, members=user).exists():
            return Response(serializer.data, status=status.HTTP_200_OK)

        if add_user_to_fewest_group(instance, user) is None:
            return Response({"message": "Группы переполнены"}, status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductListView(generics.ListAPIView):
    '''
    Предоставляет список продуктов с указанием процента от общего числа покупателей
    а также количество уроков и количество студентов
    '''
    queryset = Product.objects.prefetch_related('lesson_set', 'group_set').annotate(
        total_students=Count('group__members')).all()
    serializer_class = ProductListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['total_users_on_platform'] = User.objects.count()
        return context


class LessonListView(generics.ListAPIView):
    '''
    Возвращает уроки, относящиеся к определенному продукту
    Доступ к ним имеют только создатель и входящие в группу связанную с этим продуктом
    '''
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, HasAccessToProduct]

    def get_queryset(self):
        name = self.kwargs.get('name')
        product_ids = Product.objects.filter(name=name).values_list('id', flat=True)
        lessons = Lesson.objects.filter(product_id__in=Subquery(product_ids))
        return lessons

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class GroupListAPIView(generics.ListAPIView):
    '''
    Предоставляет список всех групп с указанием
    процента заполненности пользователями каждой из них
    '''
    queryset = Group.objects.all().prefetch_related('members').select_related('product')
    serializer_class = GroupSerializer