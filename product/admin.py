from django.contrib import admin

# Register your models here.
from .models import Category, Catalog, Customer, Application, Movement

# ���������� ������ �� ������� �������� ���������� ��������������
admin.site.register(Category)
admin.site.register(Catalog)
admin.site.register(Customer)
admin.site.register(Application)
admin.site.register(Movement)

