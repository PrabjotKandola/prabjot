from django.shortcuts import render
from profilit.models import ExplorationFiles, MatchFiles
from django.contrib.auth.decorators import login_required
from dashboard.models import RuleTemplateErrors, RulesBasedProfileFiles
from django.contrib import messages


@login_required
def exploration_dashboard(request):
    files = ExplorationFiles.objects.filter(person=request.user.id).order_by('-date_created')
    context = {'files': files}
    print('hello')
    print(str(files))
    return render(request, 'dashboard/exploration-dashboard.html', context)


@login_required
def check_rules(request):
    files = RuleTemplateErrors.objects.filter(person=request.user.id)
    context = {'files': files}
    messages.warning(request, 'There are errors in your rules - these are shown below.', extra_tags='danger')
    return render(request, 'dashboard/check_rules.html', context)

@login_required
def matching_dashboard(request):
    files = MatchFiles.objects.filter(person=request.user.id)
    context = {'files': files}
    return render(request, 'dashboard/match_venn.html', context)


@login_required
def rules_dashboard_overall(request):
    files = RulesBasedProfileFiles.objects.filter(person=request.user.id).order_by('-date_created')
    context = {'files': files}
    return render(request, 'dashboard/rules-dashbaord-overall.html', context)

@login_required
def rules_dashboard_attribute(request):
    files = RulesBasedProfileFiles.objects.filter(person=request.user.id).order_by('-date_created')
    context = {'files': files}
    return render(request, 'dashboard/rules-dashboard-attribute.html', context)


@login_required
def rules_dashboard_trend(request):
    files = RulesBasedProfileFiles.objects.filter(person=request.user.id).order_by('-date_created')
    context = {'files': files}
    return render(request, 'dashboard/rules-dashboard-trend.html', context)
