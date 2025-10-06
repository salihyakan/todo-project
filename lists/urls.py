from django.urls import path
from . import views

app_name = 'lists'

urlpatterns = [
    path('', views.ListListView.as_view(), name='list_list'),
    path('create/', views.ListCreateView.as_view(), name='list_create'),
    path('<int:pk>/', views.ListDetailView.as_view(), name='list_detail'),
    path('<int:pk>/edit/', views.ListUpdateView.as_view(), name='list_edit'),
    path('<int:pk>/delete/', views.ListDeleteView.as_view(), name='list_delete'),
    
    # AJAX endpoints
    path('item/<int:item_id>/toggle/', views.toggle_item_status, name='toggle_item'),
    path('item/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('<int:list_id>/add-item/', views.add_item, name='add_item'),
]