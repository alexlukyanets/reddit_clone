from django.shortcuts import render
from rest_framework import generics, permissions, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Post, Vote
from .serializers import *


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user)

class VoteCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        post = Post.objects.get(pk=self.kwargs['pk'])
        return Vote.objects.filter(voter=user, post=post)

    def perform_create(self, serializer):
        if self.get_queryset().exists():
            raise ValidationError('Вы уже голосовали за этот пост')
        serializer.save(voter=self.request.user, post=Post.objects.get(pk=self.kwargs['pk']))

    def delete(self, requests, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('Вы никогда не голосовали за этот пост ')
