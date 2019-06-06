from django.urls import path
from .views import *

urlpatterns = [
    # ----- posts ----------------
    path('group/<str:slug>/post/create/', PostCreate.as_view(), name='post_create'),
    path('group/<str:slug>/post/<str:postslug>/', PostView.as_view(), name='post_detail'),
    # ----- groups --------------
    path('group/list/', GroupList.as_view(), name='group_list'),
    path('group/create/', GroupCreate.as_view(), name='group_create'),
    path('group/<str:slug>/join/', group_join, name='group_join'),
    path('group/<str:slug>/left/', group_left, name='group_left'),
    path('group/<str:slug>/delete/', GroupDelete.as_view(), name='group_delete'),
    path('group/<str:slug>/update/', GroupUpdate.as_view(), name='group_update'),
    path('group/<str:slug>/', GroupView.as_view(), name='group_info'),
    # ------ profile --------
    path('profile/edit/', ProfileEdit.as_view(), name='profile_edit'),
    path('profile/', ProfileInfo.as_view(), name='myprofile'),
    path('profile/<int:pk>/', ProfileInfo.as_view(), name='profile'),
    path('reg/', SignUp.as_view(), name='reg'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', logoutview, name='logout'),
    # ---------------
    path('', MainView.as_view(), name='main'),
]