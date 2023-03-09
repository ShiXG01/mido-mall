from django.shortcuts import render
from django.views import View


# Create your views here.

class RegisterViews(View):

    def get(self, request):
        """提供用户注册界面"""
        return render(request, 'register.html')

    def post(self, request):
        """实现用户注册业务"""
        pass
