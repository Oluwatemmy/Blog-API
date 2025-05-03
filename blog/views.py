
from .serializers import PostSerializer
from .models import Post
from account.models import CustomUser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    DestroyAPIView,
    UpdateAPIView
)

# Create your views here.
class CreatepostView(CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        author = request.user
        if serializer.is_valid(raise_exception=True):
            # Check if the user is authenticated
            if not author.is_authenticated:
                return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Save the post with the author
            serializer.save(user=author)
            # return the created post data
            return Response({
                "post": serializer.data,
                "message": f"Post created successfully by {author.first_name} {author.last_name}",
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        
class ListPostView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the user from the request
        user = CustomUser.objects.get(id=request.user.id)
        # Get all posts by the user
        posts = Post.objects.filter(user=user)
        # Return the posts in the response
        serializer = self.serializer_class(posts, many=True)
        return Response(
            {
                "posts": serializer.data,
                "message": f"Posts retrieved successfully for {user.first_name}",
            },
            status=status.HTTP_200_OK,
        )
    

class ViewAPostView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
            serializer = self.serializer_class(post)
            return Response(
                {
                    "post": serializer.data,
                    "message": f"Post retrieved successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )


    


