from django.shortcuts import render, get_object_or_404
from issues.models import *
from issues import forms
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods

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

@require_http_methods(["GET", "POST"])
def detail(request, key=None):
    if request.user.has_perm('view_issues'):
        issue = get_object_or_404(Issue, pk=key)
        if request.method == "POST":
            form = forms.ResponseForm(request.POST)
            if form.is_valid():
                issue.send_response(str(request.user),form.cleaned_data['body'])
        form = forms.ResponseForm()
        messages = issue.message_set.all()
        return render(request, 'issues/detail.html', {'issue': issue, 'messages': messages, 'form': form})
    else:
        raise PermissionDenied
