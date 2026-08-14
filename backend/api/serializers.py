from rest_framework import serializers

class KeyPressSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=1)