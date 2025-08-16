#register your models here
from django.contrib import admin
from .models import SalesAgent, Phone, Assignment, Stock, Sale, AssignedPhone

@admin.register(SalesAgent)
class SalesAgentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_contact', 'agent_number')
    search_fields = ('full_name', 'agent_number')
    list_per_page = 20

@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'model')
    search_fields = ('name', 'model', 'brand')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('sale_date', 'agent', 'phone', 'quantity_sold')
    list_filter = ('sale_date', 'agent')
    search_fields = ('agent__full_name', 'phone__name')

#assigned phone
class AssignedPhoneInline(admin.TabularInline):
    model = AssignedPhone
    extra = 1

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('agent', 'date_assigned', 'previous_assignment')
    list_filter = ('date_assigned',)
    search_fields = ('agent__full_name',)
    inlines = [AssignedPhoneInline]

