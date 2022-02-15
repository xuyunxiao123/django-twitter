from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from accounts.api.serializers import (
    UserSerializer,
    LoginSerializer,
    SignupSerializer
)

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ViewSet):

    serializer_class = SignupSerializer
    @action(methods=['GET'],detail=False)
    def login_status(self,request):
        data = {'has_logged_in':request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user']=UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'],detail=False)
    def logout(self,request):
        """
        登出当前用户
        """
        django_logout(request)
        return Response({"success":True})

    @action(methods=['POST'],detail=False)
    def login(self,request):
        """
        实现用户的登陆功能
        """
        serializer = LoginSerializer(data= request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        if not User.objects.filter(username=username).exists():
            return Response({
                "success":False,
                "message":"user does not exist"
            })
        user = django_authenticate(username=username,password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "username and password does not match"

            },status=400)
        django_login(request,user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    @action(methods=['POST'],detail=False)
    def signup(self,request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)
        user = serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        })


