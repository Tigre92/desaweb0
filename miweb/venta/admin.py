from django.contrib import admin

from .models import Cliente, Producto

# Agregar el modelo Cliente al Admin
admin.site.register(Cliente)
admin.site.register(Producto)