from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login, logout
from .serializers import RegisterSerializer, APIKeySerializer
from .models import UserAPIKey
from django.contrib.auth.models import User


from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, password=password)
        token = Token.objects.create(user=user)
        return Response({'token': token.key}, status=201)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=400)

class LogoutView(APIView):
    def post(self, request):
        request.auth.delete()  # Delete token
        return Response({'message': 'Logged out'})


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_user_keys(request):
    youtube_key = request.data.get('youtube_api_key')
    openai_key = request.data.get('openai_api_key')  # Optional

    if not youtube_key:
        return Response({'error': 'YouTube API key is required'}, status=400)

    obj, created = UserAPIKey.objects.get_or_create(user=request.user)
    obj.youtube_api_key = youtube_key
    if openai_key:
        obj.openai_api_key = openai_key
    obj.save()

    return Response({'message': 'API keys saved successfully'})



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserAPIKey
from .utils import (
    fetch_youtube_titles,
    generate_description_with_openai,
    generate_tags_with_openai,
    generate_basic_description,
    generate_basic_tags,
)

class GenerateContentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        keyword = request.data.get('keyword')
        if not keyword:
            return Response({'error': 'Keyword is required'}, status=400)

        try:
            api_keys = UserAPIKey.objects.get(user=request.user)
            youtube_key = api_keys.youtube_api_key
            openai_key = api_keys.openai_api_key
        except UserAPIKey.DoesNotExist:
            return Response({'error': 'API keys not found for this user'}, status=400)

        # Fetch titles from YouTube API
        titles = fetch_youtube_titles(youtube_key, keyword)

        openai_error = None
        try:
            if openai_key:
                description = generate_description_with_openai(openai_key, titles, keyword)
                tags = generate_tags_with_openai(openai_key, titles)

                if not description or not tags:
                    raise Exception("OpenAI response incomplete")
            else:
                raise Exception("OpenAI key missing")
        except Exception as e:
            openai_error = str(e)
            description = generate_basic_description(titles, keyword)
            tags = generate_basic_tags(titles)

        return Response({
            "titles": titles,
            "description": description,
            "tags": tags,
            "openai_error": openai_error
        })



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_user_keys(request):
    youtube_key = request.data.get('youtube_api_key')
    openai_key = request.data.get('openai_api_key')

    if not youtube_key:
        return Response({'error': 'YouTube API key is required'}, status=400)

    obj, created = UserAPIKey.objects.get_or_create(user=request.user)
    obj.youtube_api_key = youtube_key
    if openai_key:
        obj.openai_api_key = openai_key
    obj.save()

    return Response({'message': 'API keys saved successfully'})