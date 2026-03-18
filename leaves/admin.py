from django.contrib import admin
from .models import Leave, Employee


@admin.action(description="Approve selected leave requests")
def approve_leaves(modeladmin, request, queryset):
    updated_count = queryset.update(status="APPROVED")
    modeladmin.message_user(request, f"{updated_count} leave requests approved.")

@admin.action(description="Reject selected leave requests")
def reject_leaves(modeladmin, request, queryset):
    updated_count = queryset.update(status="REJECTED")
    modeladmin.message_user(request, f"{updated_count} leave requests rejected.")

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('leave_type','start_date', 'end_date', 'reason', 'status', 'employee')
    search_fields = ('leave_type','reason')
    list_filter = ('start_date', 'end_date', 'leave_type')
    actions = [approve_leaves, reject_leaves]

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'employee_department', 'employee_position', 'email', 'employee_role')
    search_fields = ('first_name', 'last_name', 'employee_department', 'employee_position', 'email', 'employee_role')
    list_filter = ('employee_department', 'employee_position', 'employee_role')
