from django.shortcuts import render, redirect

# Класс HttpResponse из пакета django.http, который позволяет отправить текстовое содержимое.
from django.http import HttpResponse, HttpResponseNotFound
# Конструктор принимает один обязательный аргумент – путь для перенаправления. Это может быть полный URL (например, 'https://www.yahoo.com/search/') или абсолютный путь без домена (например, '/search/').
from django.http import HttpResponseRedirect

from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from django.db.models import Max
from django.db.models import Q

from datetime import datetime, timedelta

# Отправка почты
from django.core.mail import send_mail

# Подключение моделей
from .models import Category, Catalog, ViewCatalog, Customer, Application, ViewApplication, Movement
# Подключение форм
from .forms import CategoryForm, CatalogForm, MovementForm, SignUpForm

from django.db.models import Sum

from django.db import models

import sys

import math

#from django.utils.translation import ugettext as _
from django.utils.translation import gettext_lazy as _

from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from django.contrib.auth import login as auth_login

from django.db.models.query import QuerySet

import csv
import xlwt
from io import BytesIO

# Create your views here.
# Групповые ограничения
def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups, login_url='403')

###################################################################################################

# Стартовая страница 
def index(request):
    try:
        catalog = ViewCatalog.objects.all().order_by('?')[0:4]
        return render(request, "index.html", {"catalog": catalog, })    
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)    

# Контакты
def contact(request):
    try:
        return render(request, "contact.html")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Отчет 1
@login_required
@group_required("Managers")
def report_1(request):
    try:
        where = ""
        start_date = datetime(datetime.now().year, 1, 1, 0, 0).strftime('%Y-%m-%d') 
        finish_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0).strftime('%Y-%m-%d') 
        total = ViewApplication.objects.aggregate(Sum('price'))
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по дате
                start_date = request.POST.get("start_date")
                #print(start_date)
                finish_date = request.POST.get("finish_date")
                finish_date = str(datetime.strptime(finish_date, "%Y-%m-%d") + timedelta(days=1))
                total = ViewApplication.objects.filter(date_application__range=[start_date, finish_date]).aggregate(Sum('price'))
                #print(finish_date)
                if where != "":
                    where = where + " AND "
                where = "view_application.date_application>='" + start_date + "' AND view_application.date_application<='" + finish_date + "'"
                print(where)
                finish_date = request.POST.get("finish_date")
                # Добавить ключевое слово WHERE 
                if where != "":
                    where = " WHERE " + where + " "              
                print(where)
        report = Customer.objects.raw("""
SELECT 1 as id, date_application, final, telegram_id, phone_number, first_name, last_name, category, catalog_title, price
FROM view_application
""" 
+ where +
"""
ORDER BY date_application
""")
        return render(request, "report/report_1.html", {"report": report, "total": total, "start_date": start_date, "finish_date": finish_date, })
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Отчет 2
@login_required
@group_required("Managers")
def report_2(request):
    try:
        where = ""
        start_date = datetime(datetime.now().year, 1, 1, 0, 0).strftime('%Y-%m-%d') 
        finish_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0).strftime('%Y-%m-%d') 
        total = ViewApplication.objects.count()
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по дате
                start_date = request.POST.get("start_date")
                #print(start_date)
                finish_date = request.POST.get("finish_date")
                finish_date = str(datetime.strptime(finish_date, "%Y-%m-%d") + timedelta(days=1))
                total = ViewApplication.objects.filter(date_application__range=[start_date, finish_date]).count()
                #print(finish_date)
                if where != "":
                    where = where + " AND "
                where = "view_application.date_application>='" + start_date + "' AND view_application.date_application<='" + finish_date + "'"
                print(where)
                finish_date = request.POST.get("finish_date")
                # Добавить ключевое слово WHERE 
                if where != "":
                    where = " WHERE " + where + " "              
                print(where)
        report = Customer.objects.raw("""
SELECT 1 as id, category, catalog_title, COUNT(*) AS kolichestvo, SUM(price) AS summa
FROM view_application
""" 
+ where +
"""
GROUP BY category, catalog_title
""")
        return render(request, "report/report_2.html", {"report": report, "total": total, "start_date": start_date, "finish_date": finish_date, })
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def category_index(request):
    try:
        category = Category.objects.all().order_by('category_title')
        return render(request, "category/index.html", {"category": category,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def category_create(request):
    try:
        if request.method == "POST":
            category = Category()
            category.category_title = request.POST.get("category_title")
            categoryform = CategoryForm(request.POST)
            if categoryform.is_valid():
                category.save()
                return HttpResponseRedirect(reverse('category_index'))
            else:
                return render(request, "category/create.html", {"form": categoryform})
        else:        
            categoryform = CategoryForm()
            return render(request, "category/create.html", {"form": categoryform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@group_required("Managers")
def category_edit(request, id):
    try:
        category = Category.objects.get(id=id)
        if request.method == "POST":
            category.category_title = request.POST.get("category_title")
            categoryform = CategoryForm(request.POST)
            if categoryform.is_valid():
                category.save()
                return HttpResponseRedirect(reverse('category_index'))
            else:
                return render(request, "category/edit.html", {"form": categoryform})
        else:
            # Загрузка начальных данных
            categoryform = CategoryForm(initial={'category_title': category.category_title, })
            return render(request, "category/edit.html", {"form": categoryform})
    except Category.DoesNotExist:
        return HttpResponseNotFound("<h2>Category not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def category_delete(request, id):
    try:
        category = Category.objects.get(id=id)
        category.delete()
        return HttpResponseRedirect(reverse('category_index'))
    except Category.DoesNotExist:
        return HttpResponseNotFound("<h2>Category not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@group_required("Managers")
def category_read(request, id):
    try:
        category = Category.objects.get(id=id) 
        return render(request, "category/read.html", {"category": category})
    except Category.DoesNotExist:
        return HttpResponseNotFound("<h2>Category not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

####################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def catalog_index(request):
    catalog = Catalog.objects.all().order_by('catalog_title')
    return render(request, "catalog/index.html", {"catalog": catalog})
    
# Список для просмотра и отправки в корзину
#@login_required
#@group_required("Managers")
#@login_required
def catalog_list(request):
    try:
        # Каталог доступных товаров
        catalog = ViewCatalog.objects.all().order_by('category').order_by('catalog_title')
        # Категории и подкатегория товара (для поиска)
        category = Category.objects.all().order_by('category_title')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по категории товара
                selected_item_category = request.POST.get('item_category')
                #print(selected_item_category)
                if selected_item_category != '-----':
                    category_query = Category.objects.filter(category_title = selected_item_category).only('id').all()
                    catalog = catalog.filter(category_id__in = category_query).all()
                # Поиск по названию товара
                catalog_search = request.POST.get("catalog_search")
                #print(catalog_search)                
                if catalog_search != '':
                    catalog = catalog.filter(catalog_title__contains = catalog_search).all()
                # Сортировка
                sort = request.POST.get('radio_sort')
                #print(sort)
                direction = request.POST.get('checkbox_sort_desc')
                #print(direction)
                if sort=='title':                    
                    if direction=='ok':
                        catalog = catalog.order_by('-catalog_title')
                    else:
                        catalog = catalog.order_by('catalog_title')
                elif sort=='price':                    
                    if direction=='ok':
                        catalog = catalog.order_by('-price')
                    else:
                        catalog = catalog.order_by('price')
                elif sort=='category':                    
                    if direction=='ok':
                        catalog = catalog.order_by('-category')
                    else:
                        catalog = catalog.order_by('category')
                return render(request, "catalog/list.html", {"catalog": catalog, "category": category, "selected_item_category": selected_item_category, "catalog_search": catalog_search, "sort": sort, "direction": direction,})    
            else:          
                return render(request, "catalog/list.html", {"catalog": catalog, "category": category,})    
        else:
            return render(request, "catalog/list.html", {"catalog": catalog, "category": category, })            
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def catalog_create(request):
    try:
        if request.method == "POST":
            catalog = Catalog()
            catalog.category = Category.objects.filter(id=request.POST.get("category")).first()
            catalog.catalog_title = request.POST.get("catalog_title")
            catalog.details = request.POST.get("details")        
            catalog.price = request.POST.get("price")
            if "photo" in request.FILES:                
                catalog.photo = request.FILES["photo"]
            catalogform = CatalogForm(request.POST)
            if catalogform.is_valid():
                catalog.save()
                return HttpResponseRedirect(reverse('catalog_index'))
            else:
                return render(request, "catalog/create.html", {"form": catalogform})
        else:        
            catalogform = CatalogForm()
            return render(request, "catalog/create.html", {"form": catalogform, })
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
# Функция в качестве параметра принимает идентификатор объекта в базе данных.
@login_required
@group_required("Managers")
def catalog_edit(request, id):
    try:
        catalog = Catalog.objects.get(id=id) 
        if request.method == "POST":
            catalog.category = Category.objects.filter(id=request.POST.get("category")).first()
            catalog.catalog_title = request.POST.get("catalog_title")
            catalog.details = request.POST.get("details")        
            catalog.price = request.POST.get("price")
            if "photo" in request.FILES:                
                catalog.photo = request.FILES["photo"]
            catalogform = CatalogForm(request.POST)
            if catalogform.is_valid():
                catalog.save()
                return HttpResponseRedirect(reverse('catalog_index'))
            else:
                return render(request, "catalog/edit.html", {"form": catalogform})            
        else:
            # Загрузка начальных данных
            catalogform = CatalogForm(initial={'category': catalog.category, 'catalog_title': catalog.catalog_title, 'details': catalog.details, 'price': catalog.price, 'photo': catalog.photo })
            #print('->',catalog.photo )
            return render(request, "catalog/edit.html", {"form": catalogform})
    except Catalog.DoesNotExist:
        return HttpResponseNotFound("<h2>Catalog not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def catalog_delete(request, id):
    try:
        catalog = Catalog.objects.get(id=id)
        catalog.delete()
        return HttpResponseRedirect(reverse('catalog_index'))
    except Catalog.DoesNotExist:
        return HttpResponseNotFound("<h2>Catalog not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы с информацией о товаре для менеджера.
@login_required
@group_required("Managers")
def catalog_read(request, id):
    try:
        catalog = ViewCatalog.objects.get(id=id) 
        return render(request, "catalog/read.html", {"catalog": catalog})
    except Catalog.DoesNotExist:
        return HttpResponseNotFound("<h2>Catalog not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы с информацией о товаре для клиента
#@login_required
def catalog_details(request, id):
    try:
        # Товар с каталога
        catalog = ViewCatalog.objects.get(id=id)
        return render(request, "catalog/details.html", {"catalog": catalog, })
    except Catalog.DoesNotExist:
        return HttpResponseNotFound("<h2>Catalog not found</h2>")

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def customer_index(request):
    try:
        customer = Customer.objects.all().order_by('date_joined')
        return render(request, "customer/index.html", {"customer": customer,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@group_required("Managers")
def customer_read(request, id):
    try:
        customer = Customer.objects.get(id=id) 
        return render(request, "customer/read.html", {"customer": customer})
    except Customer.DoesNotExist:
        return HttpResponseNotFound("<h2>Customer not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def application_index(request):
    try:
        application = ViewApplication.objects.all().order_by('date_application')
        return render(request, "application/index.html", {"application": application,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def application_delete(request, id):
    try:
        application = Application.objects.get(id=id)
        application.delete()
        return HttpResponseRedirect(reverse('application_index'))
    except Application.DoesNotExist:
        return HttpResponseNotFound("<h2>Application not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@group_required("Managers")
def application_read(request, id):
    try:
        application = ViewApplication.objects.get(id=id) 
        return render(request, "application/read.html", {"application": application})
    except Application.DoesNotExist:
        return HttpResponseNotFound("<h2>Application not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def movement_index(request, application_id):
    try:
        movement = Movement.objects.filter(application_id=application_id).order_by('-datem')
        app = Application.objects.get(id=application_id)
        print(app.id)
        #movement = Movement.objects.all().order_by('-orders', '-datem')
        return render(request, "movement/index.html", {"movement": movement, "application_id": application_id, "app": app})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def movement_create(request, application_id):
    try:
        app = Application.objects.get(id=application_id)
        if request.method == "POST":
            movement = Movement()
            movement.application_id = application_id
            movement.datem = datetime.now()
            movement.status = request.POST.get("status")
            movement.details = request.POST.get("details")
            movementform = MovementForm(request.POST)
            if movementform.is_valid():
                movement.save()
                return HttpResponseRedirect(reverse('movement_index', args=(application_id,)))
            else:
                return render(request, "application/create.html", {"form": movementform})
        else:
            movementform = MovementForm(initial={ 'datem': datetime.now().strftime('%Y-%m-%d')})
            return render(request, "movement/create.html", {"form": movementform, "application_id": application_id, "app": app})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@group_required("Managers")
def movement_edit(request, id, application_id):
    app = Application.objects.get(id=application_id)
    try:
        movement = Movement.objects.get(id=id) 
        if request.method == "POST":
            #movement.datem = datetime.now()
            movement.status = request.POST.get("status")
            movement.details = request.POST.get("details")
            movementform = MovementForm(request.POST)
            if movementform.is_valid():
                movement.save()
                return HttpResponseRedirect(reverse('movement_index', args=(application_id,)))
            else:
                return render(request, "application/edit.html", {"form": movementform})
        else:
            # Загрузка начальных данных
            movementform = MovementForm(initial={'application': movement.application, 'datem': movement.datem.strftime('%Y-%m-%d'), 'status': movement.status, 'details': movement.details,  })
            return render(request, "movement/edit.html", {"form": movementform, "application_id": application_id, "app": app})
    except Movement.DoesNotExist:
        return HttpResponseNotFound("<h2>Movement not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def movement_delete(request, id, application_id):
    try:
        movement = Movement.objects.get(id=id)
        movement.delete()
        return HttpResponseRedirect(reverse('movement_index', args=(application_id,)))
    except Movement.DoesNotExist:
        return HttpResponseNotFound("<h2>Movement not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
def movement_read(request, id, application_id):
    try:
        movement = Movement.objects.get(id=id) 
        return render(request, "movement/read.html", {"movement": movement, "application_id": application_id})
    except Movement.DoesNotExist:
        return HttpResponseNotFound("<h2>Movement not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)


###################################################################################################

# Регистрационная форма 
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')
            #return render(request, 'registration/register_done.html', {'new_user': user})
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# Изменение данных пользователя
@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email',)
    template_name = 'registration/my_account.html'
    success_url = reverse_lazy('index')
    #success_url = reverse_lazy('my_account')
    def get_object(self):
        return self.request.user

# Выход
from django.contrib.auth import logout
def logoutUser(request):
    logout(request)
    return render(request, "index.html")

