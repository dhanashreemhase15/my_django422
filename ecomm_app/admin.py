from django.contrib import admin
from .models import Product

# Register your models here.
class Productadmin(admin.ModelAdmin):
    list_display=['id','name','price','pdetails','cat','is_active']
    list_filter=['price','is_active']


admin.site.register(Product,Productadmin)