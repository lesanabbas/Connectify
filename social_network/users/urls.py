from django.urls import path
from .views import (
    SignupView, 
    LoginView, 
    UserSearchView, 
    FriendRequestView, 
    BlockUserView, 
    FriendsListView, 
    PendingFriendRequestsView,
    ActivityView,
    NotificationView,
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='user_search'),
    path('friend-requests/', FriendRequestView.as_view(), name='friend_requests'),
    path('friend-requests/<int:pk>/', FriendRequestView.as_view(), name='friend_request_update'),
    path('block/', BlockUserView.as_view(), name='block-user'),
    path('unblock/', BlockUserView.as_view(), name='unblock-user'),
    path('friends/', FriendsListView.as_view(), name='friends_list'),
    path('pending-requests/', PendingFriendRequestsView.as_view(), name='pending_requests'),
    path('activities/', ActivityView.as_view(), name='user_activities'),
    path('notifications/', NotificationView.as_view(), name='user_notifications'),
]
