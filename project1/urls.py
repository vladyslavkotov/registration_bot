from django.contrib import admin
from django.urls import path, include
from tgreg.views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root, name="root"),
    path('main/', main, name="main"),
    #----------------------------API---------------------------
    path('new_user/', new_user, name="new_user"),
    path('check_username/', check_username, name="check_username"),
#--------------------------------USER--------------------------
    path('login/', UserLoginView.as_view(),name='login'),
    path('logout/', UserLogoutView.as_view(),name='logout')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)