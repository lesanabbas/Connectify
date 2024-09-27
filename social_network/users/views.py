
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsAdmin, IsReadOnly, IsWriter
from .serializers import (
    UserSerializer, 
    LoginSerializer, 
    UserSearchSerializer, 
    FriendRequestSerializer, 
    ActivitySerializer, 
    NotificationSerializer,
)
from django_ratelimit.decorators import ratelimit
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import (
    FriendRequest, 
    CustomUser, 
    UserBlock, 
    Activity, 
    Notification,
)
from .utils import create_notification
from django.core.cache import cache
from django.db.models import Q
from rest_framework.throttling import UserRateThrottle


User = get_user_model()

class SignupView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=True))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data['email'].lower(),
            password=serializer.validated_data['password'],
        )
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]
    
    @method_decorator(ratelimit(key='ip', rate='10/m', method='GET', block=True))
    @method_decorator(cache_page(60 * 10))
    def get(self, request):
        query = request.query_params.get('query', '').strip()
        
        if query:
            if '@' in query:
                users = CustomUser.objects.filter(email__iexact=query)
            else:
                users = CustomUser.objects.filter(
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query) |
                    Q(username__icontains=query)
                )
        else:
            users = CustomUser.objects.none()

        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(users, request)
        serializer = UserSearchSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    

class FriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=True))
    @transaction.atomic
    def post(self, request):
        to_user_id = request.data.get('to_user_id')
        to_user = User.objects.filter(id=to_user_id).first()

        if not to_user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if already friends
        if FriendRequest.objects.filter(from_user=request.user, to_user=to_user, is_accepted=True).exists():
            return Response({"detail": "You are already friends."}, status=status.HTTP_400_BAD_REQUEST)

        # Check for pending or rejected requests
        existing_request = FriendRequest.objects.filter(from_user=request.user, to_user=to_user).last()
        if existing_request and not existing_request.can_send_another_request():
            return Response({"detail": "You cannot send another friend request now."}, status=status.HTTP_400_BAD_REQUEST)

        # Create new friend request
        friend_request = FriendRequest.objects.create(from_user=request.user, to_user=to_user)

        # Create send request activity
        Activity.objects.create(user=request.user, action="sent friend request", target_user=to_user)
        
        # Create notification for send friend request
        create_notification(user=to_user, message=f"{request.user.username} has sent you a friend request.")

        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

    @method_decorator(ratelimit(key='ip', rate='5/m', method='PUT', block=True))
    def put(self, request, pk):
        # Accept or reject a friend request
        friend_request = FriendRequest.objects.filter(id=pk).first()
        
        if not friend_request:
            return Response({"detail": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != friend_request.to_user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        accept = request.data.get('accept', False)
        with transaction.atomic():
            if accept:
                friend_request.is_accepted = True
                friend_request.save()
                # Create accept request activity        
                Activity.objects.create(user=request.user, action="accepted friend request", target_user=request.user)
                # Create notification for accept friend request
                create_notification(user=request.user, message=f"{request.user.username} has accepted your friend request.")
            else:
                friend_request.delete()
                # Create accept request activity
                Activity.objects.create(user=request.user, action="rejected friend request", target_user=request.user)
                # Create notification for send friend request
                create_notification(user=request.user, message=f"{request.user.username} has rejected friend request.")

        return Response({"status": "success"}, status=status.HTTP_200_OK)
    

class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    @transaction.atomic
    def post(self, request):
        """
        Block a user
        """
        to_block_id = request.data.get('to_block_id')
        to_block = User.objects.filter(id=to_block_id).first()

        if not to_block:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is already blocked
        if UserBlock.objects.filter(blocker=request.user, blocked=to_block).exists():
            return Response({"detail": "User is already blocked."}, status=status.HTTP_400_BAD_REQUEST)

        # Block the user
        UserBlock.objects.create(blocker=request.user, blocked=to_block)
        return Response({"status": "User blocked successfully."}, status=status.HTTP_201_CREATED)

    @method_decorator(ratelimit(key='ip', rate='5/m', method='DELETE', block=True))
    @transaction.atomic
    def delete(self, request):
        """
        Unblock a user
        """
        to_unblock_id = request.data.get('to_unblock_id')
        to_unblock = User.objects.filter(id=to_unblock_id).first()

        if not to_unblock:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is blocked
        block_relation = UserBlock.objects.filter(blocker=request.user, blocked=to_unblock).first()
        if not block_relation:
            return Response({"detail": "User is not blocked."}, status=status.HTTP_400_BAD_REQUEST)

        # Unblock the user
        block_relation.delete()
        return Response({"status": "User unblocked successfully."}, status=status.HTTP_200_OK)
    
    
class FriendsListView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='10/m', method='GET', block=True))
    @method_decorator(cache_page(60 * 10))
    def get(self, request):
        friends_list = FriendRequest.objects.filter(
            (Q(from_user=request.user) | Q(to_user=request.user)),
            is_accepted=True
        ).select_related('from_user', 'to_user')

        friends_users = [
            friend_request.to_user if friend_request.from_user == request.user else friend_request.from_user
            for friend_request in friends_list
        ]

        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(friends_users, request)
        serializer = UserSearchSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PendingFriendRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    @method_decorator(cache_page(60 * 10))
    def get(self, request):
        pending_requests = FriendRequest.objects.filter(to_user=request.user, is_accepted=False).order_by('-created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(pending_requests, request)
        serializer = FriendRequestSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ActivityView(APIView):
    permission_classes = [IsAuthenticated]
    
    @method_decorator(ratelimit(key='ip', rate='10/m', method='GET', block=True))
    @method_decorator(cache_page(60 * 10))
    def get(self, request):
        activities = Activity.objects.filter(user=request.user).order_by('-created_at')
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)
    

class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def put(self, request):
        # Mark notifications as read
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all notifications marked as read'})