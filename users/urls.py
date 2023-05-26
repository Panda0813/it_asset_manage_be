from django.conf.urls import url, include
from users import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^login$', views.JwtLoginView.as_view()),
    url(r'^logout$', views.LogoutView.as_view()),
    url(r'^register$', views.UserRegisterView.as_view()),
    url(r'^roles$', views.RoleListGeneric.as_view()),
    url(r'^roles/(?P<pk>[0-9]+)', views.RoleDetailGeneric.as_view()),
    url(r'^sections$', views.SectionListGeneric.as_view()),
    url(r'^sections/(?P<pk>[0-9]+)', views.SectionDetailGeneric.as_view()),
    url(r'^users$', views.UserListGeneric.as_view()),
    url(r'^users/(?P<pk>[0-9]+)', views.UserDetailGeneric.as_view()),
    url(r'^change-password$', views.ChangePassword.as_view()),
    url(r'^operation-log$', views.OperationLogGeneric.as_view()),
    url(r'^get-oa-users$', views.query_oa_user_list),
    url(r'^get-oa-sections$', views.query_oa_sections),
    url(r'^forget-pwd$', views.forget_pwd),
    url(r'^get-oa-user-sections$', views.query_user_sections),
    url(r'^get-sections-tree$', views.query_sections_tree),
]
