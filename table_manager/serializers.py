from rest_framework import serializers

from .constants import DYNAMIC_TYPES, VALID_TYPES
from .models import DynamicTable


class DynamicFieldValidator(serializers.Serializer):
    type = serializers.ChoiceField(choices=list(DYNAMIC_TYPES.keys()))
    options = serializers.DictField(required=False)

    def validate(self, attrs):
        field_class = DYNAMIC_TYPES[attrs['type']]
        self.validate_field_options(field_class, attrs)
        return attrs

    @staticmethod
    def validate_field_options(field_class, data):
        data_options = data.get('options')
        if not data_options:
            return

        options = [item for item in data_options.keys() if item != 'type']
        valid_options = dir(field_class())
        for option in options:
            if option not in valid_options:
                raise serializers.ValidationError({
                    'options': f'Invalid option provided for {data["type"]}: {option}'
                })

            if option in VALID_TYPES:
                expected_type = VALID_TYPES[option]
                if not isinstance(data_options[option], expected_type):
                    raise serializers.ValidationError({
                        'options': f'Invalid type {option}: {data["type"]}'
                    })


class DynamicTableSerializer(serializers.ModelSerializer):
    schema = serializers.DictField(child=DynamicFieldValidator())

    class Meta:
        model = DynamicTable
        exclude = ('uuid_hex',)


class DynamicTableRowSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
