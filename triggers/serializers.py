from rest_framework import serializers
from .models import BaseTrigger, ScheduledTrigger, APITrigger, EventLog


class BaseTriggerSerializer(serializers.ModelSerializer):
    """
    Base serializer for all triggers.
    """
    class Meta:
        model = BaseTrigger
        fields = ['id', 'name', 'created_at', 'updated_at']


class ScheduledTriggerSerializer(serializers.ModelSerializer):
    """
    Serializer for ScheduledTrigger.
    """
    class Meta:
        model = ScheduledTrigger
        fields = ['id', 'name', 'schedule_time', 'is_recurring', 'interval', 'end_time', 'created_at', 'updated_at']


class APITriggerSerializer(serializers.ModelSerializer):
    """
    Serializer for APITrigger.
    """
    class Meta:
        model = APITrigger
        fields = ['id', 'name', 'payload', 'created_at', 'updated_at']


class TriggerSerializer(serializers.Serializer):
    """
    Dynamic serializer to handle both ScheduledTrigger and APITrigger.
    """
    TRIGGER_TYPE_CHOICES = {
        'scheduled': ScheduledTriggerSerializer,
        'api': APITriggerSerializer,
    }

    def to_representation(self, instance):
        """
        Dynamically serialize based on trigger type.
        """
        if isinstance(instance, ScheduledTrigger):
            serializer_class = self.TRIGGER_TYPE_CHOICES['scheduled']
        elif isinstance(instance, APITrigger):
            serializer_class = self.TRIGGER_TYPE_CHOICES['api']
        else:
            raise ValueError("Unknown trigger type")

        serializer = serializer_class(instance, context=self.context)
        return serializer.data

    def create(self, validated_data):
        """
        Dynamically create the appropriate trigger type.
        """
        trigger_type = self.context.get('trigger_type', '').lower()
        if trigger_type == 'scheduled':
            return ScheduledTrigger.objects.create(**validated_data)
        elif trigger_type == 'api':
            return APITrigger.objects.create(**validated_data)
        else:
            raise ValueError("Invalid trigger type specified for creation.")

    def update(self, instance, validated_data):
        """
        Dynamically update the appropriate trigger type.
        """
        if isinstance(instance, ScheduledTrigger):
            serializer_class = self.TRIGGER_TYPE_CHOICES['scheduled']
        elif isinstance(instance, APITrigger):
            serializer_class = self.TRIGGER_TYPE_CHOICES['api']
        else:
            raise ValueError("Unknown trigger type")

        serializer = serializer_class(instance, data=validated_data, partial=True, context=self.context)
        serializer.is_valid(raise_exception=True)
        return serializer.save()


class EventLogSerializer(serializers.ModelSerializer):
    """
    Serializer for event logs.
    """
    class Meta:
        model = EventLog
        fields = ['id', 'trigger_type', 'trigger_id', 'fired_at', 'payload', 'is_test', 'status']

