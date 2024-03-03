from django.db.models import Count
from .models import Group


def add_user_to_fewest_group(product, user):
    '''
    Добавляет пользователя в первую группу с меньшим числом участников.
    Если такая группа не найдена создает и добавляет пользователя
    после чего перераспределяет пользователей
    '''
    groups = Group.objects.filter(product=product).annotate(num_users=Count('members'))
    suitable_groups = groups.filter(num_users__lt=product.max_users).order_by('num_users')

    if suitable_groups.exists():
        for group in suitable_groups:
            group.members.add(user)
            return group
    else:
        new_group = Group.objects.create(name=product.name, product=product)
        new_group.members.add(user)
        return balance_groups(groups)

    return None


def balance_groups(groups):
    '''
    Сортирует группы чтобы разница в количестве участников не превышала 1
    '''
    groups = groups.order_by('num_users')

    while groups.last().num_users - groups.first().num_users > 1:
        min_group = groups.first()
        max_group = groups.last()

        user_to_move = max_group.members.first()
        max_group.members.remove(user_to_move)
        min_group.members.add(user_to_move)

        groups = groups.order_by('num_users')

    return groups