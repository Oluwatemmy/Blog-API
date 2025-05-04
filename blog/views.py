
from .serializers import PostSerializer, CommentSerializer
from .models import Post, Comment
from account.models import CustomUser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
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


class UpdatePostView(UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        # Check if the user is the author of the post
        if post.user != request.user:
            return Response(
                {"message": "You do not have permission to edit this post."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.serializer_class(post, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "post": serializer.data,
                    "message": "Post updated successfully",
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DeletePostView(DestroyAPIView):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        # Check if the user is the author of the post
        if post.user != request.user and not request.user.is_superuser:
            # If the user is not the author and not a superuser, deny permission
            return Response(
                {"message": "You do not have permission to delete this post."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            post.delete()
            return Response(
                {"message": "Post deleted successfully"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "An error occurred while deleting the post"},
                status=status.HTTP_400_BAD_REQUEST,
            )

class CreateCommentView(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = self.serializer_class(data=request.data)
        # Check if the post exists
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # Check if the post is published
        if not post.is_published:
            return Response(
                {"error": "Post is not published"}, status=status.HTTP_400_BAD_REQUEST
            )
        
        if serializer.is_valid(raise_exception=True):
            # Check if the user is authenticated
            if not request.user.is_authenticated:
                return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Save the comment with the author and post
            serializer.save(user=request.user, post=post)
            return Response({
                "comment": serializer.data,
                "message": f"Comment added successfully by {request.user.first_name} {request.user.last_name}",
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        

class ListCommentView(ListAPIView):
    serializer_class = CommentSerializer
    # permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        comments = Comment.objects.filter(post=post)
        serializer = self.serializer_class(comments, many=True)
        return Response(
            {
                "comments": serializer.data,
                "message": f"Comments retrieved successfully for {post.title}",
            },
            status=status.HTTP_200_OK,
        )
    
class UpdateCommentView(UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            comment = Comment.objects.get(id=pk)
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # Check if the user is the author of the comment
        if comment.user != request.user:
            return Response(
                {"message": "You do not have permission to edit this comment."},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Check if the post exists
        try:
            post = Post.objects.get(id=comment.post.id)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.serializer_class(comment, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Update the comment
        serializer.save()
        return Response({
            "comment": serializer.data,
            "message": "Comment updated successfully"
        }, status=status.HTTP_200_OK)
    

class DeleteCommentView(DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(id=pk)
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if comment.user != request.user and not request.user.is_staff and not request.user.is_superuser:
            # If the user is not the author and not a superuser, deny permission
            return Response(
                {"message": "You do not have permission to delete this comment."},
                status=status.HTTP_403_FORBIDDEN,
            )
        # delete the comment
        comment.delete()
        return Response(
            {"message": "Comment deleted successfully."},
            status=status.HTTP_200_OK
        )

