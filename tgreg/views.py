from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from tgreg.models import User
from django.core.exceptions import ObjectDoesNotExist
import requests, re
from project1.settings import MEDIA_ROOT
from django.contrib.auth.views import *
from django.shortcuts import render

def root(request):
   return render(request, 'tgreg/root.html')

def main(request):
   return render(request, 'tgreg/main.html')

class MySerializer(ModelSerializer):
   class Meta:
      model = User
      fields = ['pk', 'username']

@api_view(['POST'])
def new_user(request):
   get_unique = r"(?<=-)[\w]+"
   get_userpic = requests.get(request.POST.get('userpic'), stream=True)
   u1 = User.objects.create_user(username=request.POST.get('username'), password=request.POST.get('password'))
   get_name = re.findall(get_unique, request.POST.get('userpic'))[0]
   img_path = f"{MEDIA_ROOT}/userpics/{get_name}_{u1.pk}.jpg"
   with open(img_path, 'wb') as img:
      img.write(get_userpic.content)
   u1.userpic = img_path
   u1.save()
   serialized = MySerializer(u1)
   return Response(serialized.data)


@api_view(['POST'])
def check_username(request):
   try:
      u1 = User.objects.get(username=request.POST.get('username'))
      return Response("taken")
   except ObjectDoesNotExist:
      return Response("available")

class UserLoginView(LoginView):
   model = User
   template_name = "tgreg/login.html"

class UserLogoutView(LogoutView):
   model = User
   template_name = "tgreg/logout.html"

