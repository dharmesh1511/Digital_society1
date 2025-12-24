"""
URL configuration for society project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from enroll.views import signup_view, login_view, logout_view, home_view,profile_view, settings_view,complaint_add, complaint_list,contact_view
from django.conf import settings
from django.conf.urls.static import static
from enroll import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', signup_view, name="signup"),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout"),
    path('', home_view, name="home"),


    path('profile/', profile_view, name='profile'),  
    path('settings/', settings_view, name='settings'),  

    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),

    path('complaint/add/', complaint_add, name='complaint_add'),
    path('complaints/', complaint_list, name='complaint_list'),

    path('events/', views.events_view, name='events'),
    path('maintenance/', views.maintenance_view, name='maintenance'),

    path("send-notification/", views.send_notification, name="send_notification"),
    path("notifications/", views.notifications_view, name="notifications"),
    path("notification/read/<int:notification_id>/", views.mark_as_read, name="mark_as_read"),

    path("contact/send/", contact_view, name="contact_send"),

    path('payment/maintenance/<int:record_id>/',views.maintenance_payment,name='maintenance_payment'),
    path('events/payments/', views.event_payments, name='event_payments'),
    path('payment/event/<int:record_id>/', views.event_payment_pay, name='event_payment_pay'),
    path('payment/donation/', views.donation_payment, name='donation_payment'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)