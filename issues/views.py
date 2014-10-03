from django.shortcuts import render
from issues.models import *
from django.core.exceptions import PermissionDenied

# Create your views here.

def list(request):
    if request.user.has_perm('view_issues'):
        issues = Issue.objects.filter(active=True)
        my_issues = issues.filter(assigned_user=request.user)
        other_issues = issues.exclude(assigned_user__isnull=True).exclude(assigned_user=request.user)
        unassigned_issues = issues.filter(assigned_user__isnull=True)
        return render(request, 'issues/list.html', {'my_issues': my_issues, 'other_issues': other_issues,'unassigned_issues': unassigned_issues,})
    else:
        raise PermissionDenied

def detail(request, key=None):
    pass
