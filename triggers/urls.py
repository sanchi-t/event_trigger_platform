from django.urls import path
from .views import TriggerListCreateView, EventLogListView, TriggerTestView, TriggerDetailView, index

urlpatterns = [
    path('', index, name='index'),
    path('triggers/', TriggerListCreateView.as_view(), name='triggers'),
    path('events/', EventLogListView.as_view(), name='events'),
    path('triggers/<int:pk>/test/', TriggerTestView.as_view(), name='test_trigger'),
    path('triggers/<int:pk>/', TriggerDetailView.as_view(), name='trigger_detail'),
]

