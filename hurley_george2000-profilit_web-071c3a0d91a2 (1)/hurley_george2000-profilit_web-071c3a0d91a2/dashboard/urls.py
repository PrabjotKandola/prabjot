from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from dashboard.backend.dashboard import simpleexample, exploration_dashboard, check_rules, rules_dashboard_attribute,\
    rules_dashboard_trend, dropdown_test, rules_dashboard_overall, matching


urlpatterns = [
    path('exploration/dashboard', views.exploration_dashboard, name='dashboard-exploration'),
    path('rules/dashboard', views.rules_dashboard_overall, name='dashboard-rules-overall'),
    path('check_rules/dashboard', views.check_rules, name='check-rules'),
    path('rules/dashboard/attribute', views.rules_dashboard_attribute, name='dashboard-rules-attribute'),
    path('rules/dashboard/trend', views.rules_dashboard_trend, name='dashboard-rules-trend'),
    path('matching/dashboard', views.matching_dashboard, name='dashboard_match')
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)