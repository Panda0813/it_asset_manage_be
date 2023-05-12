from django.contrib import admin
from django.conf.urls import url, include
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

schema_view = get_schema_view(title='Asset System API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])

urlpatterns = [
   url(r'^admin/', admin.site.urls),
   url(r'^', include('users.urls')),
   url(r'^it-asset/', include('it_assets.urls')),
   url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
   url(r'^docs/$', schema_view, name='docs'),
]
