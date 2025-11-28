from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Course)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(Order_Item)
admin.site.register(Payment)
admin.site.register(Enrollment)
admin.site.register(ProductImage)
admin.site.register(Categury)
admin.site.register(Tag)