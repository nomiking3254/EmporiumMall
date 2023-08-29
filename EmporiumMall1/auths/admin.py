from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from auths.models import User

# Register your models here.
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # filter_horizontal = ('refer_parent',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<image style="height:30px;border-radius:30px" src="{}" />'.format(obj.image.url))
        else:
            return None
        
    list_display = [
                    'phone_number',
                    'email',
                    'image_preview',
                    'username', 
                    'is_active', 
                    'is_superuser',
                    'refer_parent',
                    'id',
                    ]
    list_filter = ['is_active', 'is_superuser']
    readonly_fields = ['image_preview', 'refer_code']
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'forget_password')}),
        (_('Personal info'), {'fields': (
                                         'first_name', 
                                         'last_name',
                                         'phone_number',
                                         'refer_parent',                                         
                                         'refer_code',
                                         'image',
                                         )
                            }
        ),
        (_('Permissions'), {'fields': (
                                       'is_active', 
                                       'is_staff', 
                                       'is_superuser', 
                                        ),
                            }
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
