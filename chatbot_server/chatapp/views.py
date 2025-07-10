# views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from django.contrib.auth.models import User
import openai

openai.api_key = 'your-openai-api-key'  # ✅ Replace with your OpenAI API key

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(sender=self.request.user) | ChatMessage.objects.filter(sender__username="bot")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_message = serializer.validated_data['message']
        serializer.save(sender=request.user)

        # Generate bot reply
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            bot_reply = response.choices[0].message['content']
        except Exception as e:
            print(f"OpenAI Error: {e}")
            bot_reply = "Sorry, I couldn't reply now."

        # Save bot reply
        bot_user = User.objects.get(username="bot")
        ChatMessage.objects.create(sender=bot_user, message=bot_reply)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
