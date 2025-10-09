from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from services.models import RealEstate
import decimal

class Command(BaseCommand):
    help = 'Создает тестовые данные объектов недвижимости'

    def handle(self, *args, **options):
        # Создаем объекты недвижимости
        real_estates = [
            {
                'name': 'Современная квартира в центре',
                'description': 'Просторная светлая квартира с современным ремонтом в центре города. '
                            'Высокие потолки, большие окна, встроенная кухня. '
                            'Рядом парк, магазины, школы и детские сады. '
                            'Отличная транспортная доступность.',
                'price': decimal.Decimal('8500000'),
                'area': decimal.Decimal('65.5'),
                'address': 'г. Москва, ул. Тверская, д. 15, кв. 42',
                'rooms': 2,
                'floor': 5,
                'total_floors': 12,
                'property_type': 'apartment',
                'image_key': 'apartment1.jpg',
                'is_active': True
            },
            {
                'name': 'Уютный загородный дом',
                'description': 'Двухэтажный загородный дом из экологически чистых материалов. '
                            'Участок 15 соток с ландшафтным дизайном, беседкой и барбекю. '
                            'В доме 4 спальни, 2 санузла, просторная гостиная с камином. '
                            'Центральные коммуникации, газовое отопление.',
                'price': decimal.Decimal('15000000'),
                'area': decimal.Decimal('180'),
                'address': 'Московская область, Одинцовский район, пос. Лесной, ул. Сосновая, д. 7',
                'rooms': 6,
                'floor': 2,
                'total_floors': 2,
                'property_type': 'house',
                'image_key': 'house1.jpg',
                'is_active': True
            },
            {
                'name': 'Коммерческое помещение в бизнес-центре',
                'description': 'Офисное помещение в современном бизнес-центре класса B+. '
                            'Качественная отделка, панорамные окна, система кондиционирования. '
                            'Удобная планировка: open space + 2 кабинета. '
                            'Охрана, видеонаблюдение, парковка для сотрудников и клиентов.',
                'price': decimal.Decimal('12000000'),
                'area': decimal.Decimal('120'),
                'address': 'г. Москва, Пресненская наб., д. 10, офис 505',
                'rooms': 3,
                'floor': 5,
                'total_floors': 25,
                'property_type': 'commercial',
                'image_key': 'commercial1.jpg',
                'is_active': True
            },
            {
                'name': 'Земельный участок под строительство',
                'description': 'Ровный земельный участок правильной формы в коттеджном поселке. '
                            'Электричество по границе участка, газ в перспективе. '
                            'Хорошая транспортная доступность, круглогодичный подъезд. '
                            'Красивые виды, лес в шаговой доступности.',
                'price': decimal.Decimal('3500000'),
                'area': decimal.Decimal('1200'),
                'address': 'Московская область, Истринский район, д. Лужки, уч. 42',
                'rooms': 0,
                'floor': None,
                'total_floors': None,
                'property_type': 'land',
                'image_key': 'land1.jpg',
                'is_active': True
            },
            {
                'name': 'Студия с видом на реку',
                'description': 'Компактная студия с современным ремонтом и панорамным видом на реку. '
                            'Функциональная планировка, встроенная кухня, гардеробная. '
                            'Дом новый, с подземным паркингом и охраной. '
                            'Развитая инфраструктура района.',
                'price': decimal.Decimal('5200000'),
                'area': decimal.Decimal('28'),
                'address': 'г. Москва, Пресненская наб., д. 8, кв. 315',
                'rooms': 1,
                'floor': 15,
                'total_floors': 30,
                'property_type': 'apartment',
                'image_key': 'apartment2.jpg',
                'is_active': True
            },
            {
                'name': 'Таунхаус в коттеджном поселке',
                'description': 'Современный таунхаус в охраняемом коттеджном поселке. '
                            'Три уровня, качественная отделка, встроенная техника. '
                            'Участок 2 сотки, парковка на 2 автомобиля. '
                            'Рядом лес, озеро, детская площадка.',
                'price': decimal.Decimal('9800000'),
                'area': decimal.Decimal('150'),
                'address': 'Московская область, Красногорский район, пос. Отрадное, ул. Лесная, д. 12',
                'rooms': 4,
                'floor': 3,
                'total_floors': 3,
                'property_type': 'house',
                'image_key': 'house2.jpg',
                'is_active': True
            },
        ]
        
        # Создаем объекты недвижимости
        for data in real_estates:
            RealEstate.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            
        self.stdout.write(self.style.SUCCESS(f'Создано {len(real_estates)} объектов недвижимости'))
        
        # Создаем суперпользователя, если его нет
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Создан суперпользователь admin с паролем admin'))
            
        # Создаем обычного пользователя, если его нет
        if not User.objects.filter(username='user').exists():
            user = User.objects.create_user('user', 'user@example.com', 'user')
            self.stdout.write(self.style.SUCCESS('Создан пользователь user с паролем user'))
            
        # Создаем пользователя-модератора, если его нет
        if not User.objects.filter(username='moderator').exists():
            moderator = User.objects.create_user('moderator', 'moderator@example.com', 'moderator')
            moderator.is_staff = True
            moderator.save()
            self.stdout.write(self.style.SUCCESS('Создан модератор moderator с паролем moderator'))