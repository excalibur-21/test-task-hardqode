from rest_framework import serializers
from .models import Product, Lesson, Group


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    purchase_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'start_date', 'cost', 'min_users', 'max_users', 'lesson_count', 'student_count',
                  'purchase_percentage']

    def get_lesson_count(self, obj):
        return obj.lesson_set.count()

    def get_student_count(self, obj):
        return obj.total_students

    def get_purchase_percentage(self, obj):
        total_users_on_platform = self.context.get('total_users_on_platform')
        if total_users_on_platform == 0:
            return 0
        return round((obj.total_students / total_users_on_platform) * 100)


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    filled_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = '__all__'

    def get_filled_percentage(self, obj):
        members_count = obj.members.count()
        max_users = obj.product.max_users
        if max_users == 0:
            return 0
        return round((members_count / max_users) * 100)