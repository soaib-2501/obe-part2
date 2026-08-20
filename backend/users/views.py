from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (
    MyTokenObtainPairSerializer,
    UserSerializer,
    SignupSerializer,
    effective_role,
    admin_account_exists,
)
from .permissions import IsAdminRole


class MyTokenObtainPairView(TokenObtainPairView):
    """POST username + password -> access & refresh tokens (+ role, name)."""
    permission_classes = [AllowAny]
    serializer_class = MyTokenObtainPairSerializer


class SignupView(APIView):
    """Public registration for Faculty, and for the first Administrator."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'admin_signup_open': not admin_account_exists(),
        })

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = MyTokenObtainPairSerializer.get_token(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'role': effective_role(user),
            'name': user.get_full_name() or user.username,
            'user_id': user.id,
        }, status=status.HTTP_201_CREATED)


class MeView(APIView):
    """GET the currently logged-in user's profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = UserSerializer(request.user).data
        data['role'] = effective_role(request.user)
        return Response(data)


class UserViewSet(viewsets.ModelViewSet):
    """
    Admin-only: Add / update / delete faculty members (SRS 2.3 User Management).
    GET (list/retrieve) is open to any authenticated user so faculty names show up
    in dropdowns; write actions are Admin-only.
    """
    serializer_class = UserSerializer
    pagination_class = None

    def get_queryset(self):
        qs = User.objects.all().order_by('username')
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)
        return qs

    def get_permissions(self):
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return [IsAdminRole()]
        return [IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        if int(kwargs.get('pk')) == request.user.id:
            return Response({'detail': 'You cannot delete your own account.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)
