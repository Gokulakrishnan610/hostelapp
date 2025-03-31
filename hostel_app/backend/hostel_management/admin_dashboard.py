from django.contrib.admin.apps import AdminConfig
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

class CustomAdminDashboard(admin.ModelAdmin):
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        
        # Add custom app ordering
        app_ordering = {
            'accounts': 1,
            'rooms': 2,
            'payments': 3,
        }
        
        app_list.sort(key=lambda x: app_ordering.get(x['app_label'], 10))
        return app_list

class CustomAdminConfig(AdminConfig):
    default_site = 'hostel_management.admin.HostelAdminSite' 