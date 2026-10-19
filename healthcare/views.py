from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Doctor, Patient, PatientDoctorMapping
from .serializers import DoctorSerializer, PatientDoctorMappingSerializer, PatientSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer

    def get_queryset(self):
        return Patient.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer

    def get_queryset(self):
        return Patient.objects.filter(user=self.request.user)


class DoctorListCreateView(generics.ListCreateAPIView):
    serializer_class = DoctorSerializer

    def get_queryset(self):
        return Doctor.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IsDoctorOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.user_id == request.user.id


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsDoctorOwnerOrReadOnly]


class MappingListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientDoctorMappingSerializer

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(patient__user=self.request.user).select_related('patient', 'doctor')

    def perform_create(self, serializer):
        serializer.save()


class MappingDetailView(APIView):
    def get(self, request, pk):
        mappings = PatientDoctorMapping.objects.filter(patient_id=pk, patient__user=request.user).select_related('patient', 'doctor')
        return Response(PatientDoctorMappingSerializer(mappings, many=True).data)

    def delete(self, request, pk):
        try:
            mapping = PatientDoctorMapping.objects.get(pk=pk, patient__user=request.user)
        except PatientDoctorMapping.DoesNotExist:
            raise NotFound('Mapping not found.')
        mapping.delete()
        return Response(status=204)
