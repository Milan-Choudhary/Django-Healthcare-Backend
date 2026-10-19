from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Doctor, Patient, PatientDoctorMapping

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, max_length=150)
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password')
        read_only_fields = ('id',)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def create(self, validated_data):
        name = validated_data.pop('name').strip()
        email = validated_data.pop('email')
        return User.objects.create_user(username=email, email=email, password=validated_data.pop('password'), first_name=name)


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'name', 'date_of_birth', 'gender', 'email', 'phone', 'address', 'medical_history', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('id', 'name', 'specialization', 'email', 'phone', 'created_at')
        read_only_fields = ('id', 'created_at')


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDoctorMapping
        fields = ('id', 'patient', 'doctor', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_patient(self, patient):
        request = self.context['request']
        if patient.user_id != request.user.id:
            raise serializers.ValidationError('You can only assign doctors to your own patients.')
        return patient

