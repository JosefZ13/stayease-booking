from django.contrib import admin
from .models import Room, Booking, Customer
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

admin.site.register(Room)
admin.site.register(Customer)

class CompletedBookingFilter(admin.SimpleListFilter):
    title = _('Slutförda bokningar')
    parameter_name = 'is_completed'

    def lookups(self, request, model_admin):
        return (
            ('True', _('Slutförda')),
            ('False', _('Ej slutförda')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(is_completed=True)
        if self.value() == 'False':
            return queryset.filter(is_completed=False)
        return queryset

class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'customer', 'room', 'check_in_date', 'check_out_date',
        'total_price', 'guests_count', 'is_completed', 'edit_link'
    )
    search_fields = ('customer__name', 'room__room_number', 'check_in_date', 'check_out_date')
    list_filter = ('check_in_date', 'room', CompletedBookingFilter)
    actions = ['mark_as_completed', 'delete_selected']

    def guests_count(self, obj):
        return obj.guests
    guests_count.short_description = 'Antal gäster'

    def mark_as_completed(self, request, queryset):
        queryset.update(is_completed=True)
    mark_as_completed.short_description = "Markera som slutförd"

    def is_completed(self, obj):
        return obj.is_completed
    is_completed.boolean = True
    is_completed.short_description = 'Slutförd'

    def edit_link(self, obj):
        return format_html('<a href="/admin/booking/booking/{}/change/">Redigera</a>', obj.id)
    edit_link.short_description = 'Redigera'

admin.site.register(Booking, BookingAdmin)
