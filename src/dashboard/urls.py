"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

# from django.conf.urls import url, include
from django.urls import re_path

# from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# from django.views.i18n import javascript_catalog
from django.views.i18n import JavaScriptCatalog
from .views import (
    Index,
    About,
    # DailyReport,
    # ProductSelector,
    # ProductSelectorUI,
    # JarvisMenu,
    # ChartTabs,
    # ChartContents,
    # IntegrationTable,
    BrowserNotSupport,
    # Tableau1,
    # Tableau2,  # 已停用
    Tableau3,
    Tableau4,
    Tableau5,
    Tableau6,
    Tableau_base,
    # Tableau7,  # 已停用
    # Tableau8,  # 已停用
    # Tableautest,
    # Tableautrusted,
    # WebPublicIP,
    # GetTableauServerTicket,
)

urlpatterns = [
    # local apps
    # url(r'^accounts/', include('apps.accounts.urls', namespace='accounts')),
    # url(r'^posts/', include('apps.posts.urls', namespace='posts')),
    # url(r'^comments/', include('apps.comments.urls', namespace='comments')),
    # url(r'^events/', include('apps.events.urls', namespace='events')),
    # url(r'^dailytrans/', include('apps.dailytrans.urls', namespace='dailytrans')),
    # i18n
    # re_path(r'^jsi18n/$', javascript_catalog, name='parse_javascript'),
    re_path(r"^jsi18n/$", JavaScriptCatalog.as_view(), name="parse_javascript"),
    # url(r'^set-user-language/(?P<lang>[-\w]+)/$',
    # Index.as_view(), name='set_user_language'),
    # third part
    # url(r'^tracking/', include('tracking.urls')),
    # watchlist
    # url(r'^set-user-watchlist/(?P<wi>\d+)/$',
    # Index.as_view(), name='set_user_watchlist'),
    # re_path(r"^tableau1/$", Tableau1.as_view(), name="Tableau1"),  # 已停用
    # re_path(r"^tableau2/$", Tableau2.as_view(), name="Tableau2"),  # 已停用
    re_path(r"^tableau3/$", Tableau3.as_view(), name="Tableau3"),
    re_path(r"^tableau4/$", Tableau4.as_view(), name="Tableau4"),
    re_path(r"^tableau5/$", Tableau5.as_view(), name="Tableau5"),
    re_path(r"^tableau6/$", Tableau6.as_view(), name="Tableau6"),
    # re_path(r"^tableau7/$", Tableau7.as_view(), name="Tableau7"),  # 已停用
    # re_path(r"^tableau8/$", Tableau8.as_view(), name="Tableau8"),  # 已停用

    # url(r'^tableau_reloadjson/$', Tableau_base.reload_json, name='tableau_reloadjson'),
    re_path(
        r"^tableau_reloadjson/(?P<refresh>\d)/$",
        Tableau_base.reload_json,
        name="tableau_reloadjson",
    ),
    # url(r'^tableautest/$', Tableautest.as_view(), name='Tableautest'),
    # url(r'^tableautrusted/$', Tableautrusted.as_view(), name='Tableautrusted'),
    # url(r'^webpublicip/$', WebPublicIP.as_view(), name='WebPublicIP'),
    # url(r'^gettableauserverticket/$', GetTableauServerTicket.as_view(), name='GetTableauServerTicket'),
]

urlpatterns += i18n_patterns(
    # admin
    # url(r'^{}/'.format(settings.DJANGO_ADMIN_PATH), admin.site.urls),
    # pages
    re_path(r"^$", Index.as_view(), name="index"),
    re_path(r"^about/", About.as_view(), name="about"),
    re_path(
        r"^browser-not-support/",
        BrowserNotSupport.as_view(),
        name="browser_not_support",
    ),
    # jarvis menu ajax
    # url(r'^jarvismenu/(?P<wi>\d+)/(?P<ct>\w+)/(?P<oi>\d+)/$',
    # JarvisMenu.as_view(), name='jarvismenu'),
    # url(r'^jarvismenu/(?P<wi>\d+)/(?P<ct>\w+)/(?P<oi>\d+)/(?P<lct>\w+)/(?P<loi>\d+)/$',
    # JarvisMenu.as_view(), name='jarvismenu'),
    # chart tab ajax
    # url(r'^chart-tab/chart/$', ChartTabs.as_view(), name='chart_tab'),
    # url(r'^chart-tab/watchlist/(?P<wi>\d+)/resource/(?P<ct>\w+)-(?P<oi>\d+)/$',
    # ChartTabs.as_view(watchlist_base=True), name='chart_tab'),
    # url(r'^chart-tab/watchlist/(?P<wi>\d+)/resource/(?P<ct>\w+)-(?P<oi>\d+)/sub-resource/(?P<lct>\w+)-(?P<loi>\d+)/$',
    # ChartTabs.as_view(watchlist_base=True), name='chart_tab'),
    # chart content ajax
    # url(r'^chart-content/chart/(?P<ci>\d+)/type/(?P<type>\d+)/products/(?P<products>\w+)/$',
    # ChartContents.as_view(product_selector_base=True), name='chart_content'),
    # url(r'^chart-content/chart/(?P<ci>\d+)/watchlist/(?P<wi>\d+)/resource/(?P<ct>\w+)/(?P<oi>\d+)/$',
    # ChartContents.as_view(watchlist_base=True), name='chart_content'),
    # url(r'^chart-content/chart/(?P<ci>\d+)/watchlist/(?P<wi>\d+)/resource/(?P<ct>\w+)-(?P<oi>\d+)/sub-resource/(?P<lct>\w+)-(?P<loi>\d+)/$',
    # ChartContents.as_view(watchlist_base=True), name='chart_content'),
    # chart content ajax
    # url(r'^integration-table/chart/(?P<ci>\d+)/type/(?P<type>\d+)/products/(?P<products>\w+)/$',
    # IntegrationTable.as_view(product_selector_base=True), name='integration_table'),
    # url(r'^integration-table/chart/(?P<ci>\d+)/watchlist/(?P<wi>\d+)/resource/(?P<ct>\w+)-(?P<oi>\d+)/$',
    # IntegrationTable.as_view(watchlist_base=True), name='integration_table'),
    # url(r'^integration-table/chart/(?P<ci>\d+)/watchlist/(?P<wi>\d+)/resource/(?P<ct>\w+)-(?P<oi>\d+)/sub-resource/(?P<lct>\w+)-(?P<loi>\d+)/$',
    # IntegrationTable.as_view(watchlist_base=True), name='integration_table'),
    # daily report ajax
    # url(r'^daily-report/', DailyReport.as_view(), name='daily_report'),
    # product selector
    # url(r'^product-selector/$', ProductSelector.as_view(), name='product_selector'),
    # url(r'^product-selector-ui/step/(?P<step>\d+)/$',
    # ProductSelectorUI.as_view(), name='product_selector_ui'),
)

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.SERVE_MEDIA_FILES:
    urlpatterns += patterns(
        "",
        re_path(
            r"^%s(?P<path>.*)$" % settings.MEDIA_URL.lstrip("/"),
            "django.views.static.serve",
            {"document_root": settings.MEDIA_ROOT},
        ),
    )
