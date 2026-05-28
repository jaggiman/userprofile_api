from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, min_length = 8)
    college_name = serializers.CharField(required=True)
    register_no = serializers.CharField(required=True)
    class_section = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'college_name', 'register_no', 'class_section']

    def create(self, validated_data):
            password = validated_data.pop('password')
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            return user
        
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'college_name', 'register_no', 'class_section']

class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()

class CompleteProfileSerializer(serializers.ModelSerializer):
    college_email = serializers.EmailField(required=False)
    class Meta:
        model = User
        fields = ['name', 'college_name', 'register_no', 
                    'class_section', 'college_email']
    def validate_register_no(self, value):
        user = self.context['request'].user
        if User.objects.filter(register_no=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("This Register number is already in use!")
        return value

    def update(self, instance, validated_data):
        #update each field only if it was sent in the request
        instance.name = validated_data.get('name', instance.name)
        instance.college_name = validated_data.get('college_name', instance.college_name)
        instance.register_no = validated_data.get('register_no', instance.register_no)
        instance.class_section = validated_data.get('class_section', instance.class_section)
        instance.college_email = validated_data.get('college_email', instance.college_email)
        #check if all the required feilds are filled
        #if yes, we flip the profile_complete to true
        if all([instance.college_name, instance.register_no, instance.class_section]):
            instance.profile_complete = True
        instance.save()
        return instance

class SendOTPSerializer(serializers.Serializer):
    college_email = serializers.EmailField()
    def validate_college_email(self, value):
        user = self.context['request'].user
        if User.objects.filter(college_email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("This college Email id already exists.")
        return value
class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)