from django.db import models
#from django.utils.translation import ugettext as _
from django.utils.translation import gettext_lazy as _
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django import forms

from django.contrib.auth.models import User

# Модели отображают информацию о данных, с которыми вы работаете.
# Они содержат поля и поведение ваших данных.
# Обычно одна модель представляет одну таблицу в базе данных.
# Каждая модель это класс унаследованный от django.db.models.Model.
# Атрибут модели представляет поле в базе данных.
# Django предоставляет автоматически созданное API для доступа к данным

# choices (список выбора). Итератор (например, список или кортеж) 2-х элементных кортежей,
# определяющих варианты значений для поля.
# При определении, виджет формы использует select вместо стандартного текстового поля
# и ограничит значение поля указанными значениями.

# Читабельное имя поля (метка, label). Каждое поле, кроме ForeignKey, ManyToManyField и OneToOneField,
# первым аргументом принимает необязательное читабельное название.
# Если оно не указано, Django самостоятельно создаст его, используя название поля, заменяя подчеркивание на пробел.
# null - Если True, Django сохранит пустое значение как NULL в базе данных. По умолчанию - False.
# blank - Если True, поле не обязательно и может быть пустым. По умолчанию - False.
# Это не то же что и null. null относится к базе данных, blank - к проверке данных.
# Если поле содержит blank=True, форма позволит передать пустое значение.
# При blank=False - поле обязательно.

# Категория товара (услуги)
class Category(models.Model):
    category_title = models.CharField(_('category_title'), max_length=128, unique=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'category'
    def __str__(self):
        # Вывод названияв тег SELECT 
        return "{}".format(self.category_title)

# Каталог товаров (услуг)
class Catalog(models.Model):
    category = models.ForeignKey(Category, related_name='catalog_category', on_delete=models.CASCADE)
    catalog_title = models.CharField(_('catalog_title'), max_length=255)
    details = models.TextField(_('catalog_details'), blank=True, null=True)
    price = models.DecimalField(_('catalog_price'), max_digits=9, decimal_places=2)
    photo = models.ImageField(_('catalog_photo'), upload_to='images/', blank=True, null=True)    
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'catalog'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['catalog_title']),
        ]
        # Сортировка по умолчанию
        ordering = ['catalog_title']
    def __str__(self):
        # Вывод в тег SELECT 
        return "{} {} {}".format(self.category, self.catalog_title, self.price)

# Представление базы данных Каталог товаров (со средней оценкой)
class ViewCatalog(models.Model):
    category_id = models.IntegerField(_('category_id'))
    category = models.CharField(_('category_title'), max_length=128)
    catalog_title = models.CharField(_('catalog_title'), max_length=255)
    details = models.TextField(_('catalog_details'), blank=True, null=True)
    price = models.DecimalField(_('catalog_price'), max_digits=9, decimal_places=2)
    photo = models.ImageField(_('photo'), upload_to='images/', blank=True, null=True)
    #avg_rating = models.DecimalField(_('avg_rating'), max_digits=6, decimal_places=2)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'view_catalog'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['catalog_title']),
        ]
        # Сортировка по умолчанию
        ordering = ['category', 'catalog_title']
        # Таблицу не надо не добавлять не удалять
        managed = False

# Пользователи Telegram
class Customer(models.Model):
    telegram_id = models.IntegerField(_('telegram_id'), unique=True)
    phone_number = models.CharField(_('phone_number'), max_length=20, blank=True, null=True)    
    first_name = models.CharField(_('first_name'), max_length=64, blank=True, null=True)    
    last_name = models.CharField(_('last_name'), max_length=64, blank=True, null=True)   
    date_joined = models.DateTimeField(_('date_joined'))
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'customer'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['telegram_id']),
        ]
        # Сортировка по умолчанию
        ordering = ['first_name', 'last_name']
    def __str__(self):
        # Вывод 
        return "{} {}: {}".format(self.first_name, self.last_name, self.phone_number)

# Заявки 
class Application(models.Model):
    date_application = models.DateTimeField(_('date_application'), auto_now_add=True)
    telegram_id = models.IntegerField(_('telegram_id'))
    catalog = models.ForeignKey(Catalog, related_name='application_catalog', on_delete=models.CASCADE, default=0)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'application'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['date_application', 'telegram_id']),
        ]
        # Сортировка по умолчанию
        ordering = ['date_application']
    def __str__(self):
        # Вывод 
        return "{}: {}".format(self.date_application, self.telegram_id)

# Представление Заявки
class ViewApplication(models.Model):
    date_application = models.DateTimeField(_('date_application'))
    telegram_id = models.IntegerField(_('telegram_id'))
    phone_number = models.CharField(_('phone_number'), max_length=20, blank=True, null=True)    
    first_name = models.CharField(_('first_name'), max_length=64, blank=True, null=True)    
    last_name = models.CharField(_('last_name'), max_length=64, blank=True, null=True)   
    date_joined = models.DateTimeField(_('date_joined'))
    catalog_id = models.IntegerField(_('catalog_id'))
    category_id = models.IntegerField(_('category_id'))
    category = models.CharField(_('category_title'), max_length=128)
    catalog_title = models.CharField(_('catalog_title'), max_length=255)
    details = models.TextField(_('catalog_details'), blank=True, null=True)
    price = models.DecimalField(_('catalog_price'), max_digits=9, decimal_places=2)
    photo = models.ImageField(_('photo'), upload_to='images/', blank=True, null=True)
    final = models.TextField(_('final'), blank=True, null=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'view_application'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['date_application']),
        ]
        # Сортировка по умолчанию
        ordering = ['date_application']
        # Таблицу не надо не добавлять не удалять
        managed = False

# Рассмотрение заявки клиента
class Movement(models.Model):
    application = models.ForeignKey(Application, related_name='movement_application', on_delete=models.CASCADE)
    datem = models.DateTimeField(_('datem'))
    status = models.CharField(_('movement_status'), max_length=128)
    details = models.TextField(_('movement_details'), blank=True, null=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'movement'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['application']),
            models.Index(fields=['datem']),
        ]
        # Сортировка по умолчанию
        ordering = ['datem']        
    def __str__(self):
        # Вывод в тег Select
        return "{} ({}): {}".format(self.datem.strftime('%d.%m.%Y'), self.application, self.status)

