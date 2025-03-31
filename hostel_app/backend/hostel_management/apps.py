from django.contrib.admin.apps import AdminConfig

class HostelAdminConfig(AdminConfig):
    default_site = 'hostel_management.admin.HostelAdminSite' 