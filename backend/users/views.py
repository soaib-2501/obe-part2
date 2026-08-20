from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import MyTokenObtainPairSerializer, UserSerializer
from .permissions import IsAdminRole


class MyTokenObtainPairView(TokenObtainPairView):
    """POST username + password -> access & refresh tokens (+ role, name)."""
    serializer_class = MyTokenObtainPairSerializer


class MeView(APIView):
    """GET the currently logged-in user's profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserViewSet(viewsets.ModelViewSet):
    """
    Admin-only: Add / update / delete faculty members (SRS 2.3 User Management).
    GET (list/retrieve) is open to any authenticated user so faculty names show up
    in dropdowns; write actions are Admin-only.
    """
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return [IsAdminRole()]
        return [IsAuthenticated()]
