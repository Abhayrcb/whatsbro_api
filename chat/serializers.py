
from rest_framework import serializers
from .models import User, Connection, Message
import re


class SignUpSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(min_length=8, max_length=128, write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'email',
            'phone',
            'username',
            'first_name',
            'last_name',
            'password',
            'confirm_password'
        ]
        extra_kwargs = {
            'password': {
                # Ensures that when serializing, this field will be excluded
                'write_only': True
            }
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise serializers.ValidationError("Invalid email format.")
        return value
    
    def validate(self, data):
        pass1 = data.get('password')
        pass2 = data.get('confirm_password')
        if pass1 != pass2:
            raise serializers.ValidationError("Passwords do not match.")
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', pass1):
            raise serializers.ValidationError("Password must be at least 8 characters long and contain both letters and numbers.")
        return data

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        if not re.match(r"[6-9][0-9]{9}", value):
            raise serializers.ValidationError("Invalid phone number format.")
        return value

    def create(self, validated_data):
        # Clean all values, set as lowercase
        email = validated_data['email'].lower()
        phone = validated_data['phone'].lower()
        username = validated_data['username'].lower()
        if validated_data['first_name']:
            first_name = validated_data['first_name'].lower()
        else:
            first_name = ''
        if validated_data['last_name']:
            last_name = validated_data['last_name'].lower()
        else:
            last_name = ''
        # Create new user
        user = User.objects.create(
            email=email,
            phone=phone,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        password = validated_data['password']
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
	name = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = [
			'username',
			'name',
			'thumbnail'
		]

	def get_name(self, obj):
		fname = obj.first_name.capitalize()
		lname = obj.last_name.capitalize()
		return fname + ' ' + lname


class SearchSerializer(UserSerializer):
	status = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = [
            'phone',
            'email',
			'username',
			'name',
			'thumbnail',
			'status'
		]
	
	def get_status(self, obj):
		if obj.pending_them:
			return 'pending-them'
		elif obj.pending_me:
			return 'pending-me'
		elif obj.connected:
			return 'connected'
		return 'no-connection'


class RequestSerializer(serializers.ModelSerializer):
	sender = UserSerializer()
	receiver = UserSerializer()

	class Meta:
		model = Connection
		fields = [
			'id',
			'sender',
			'receiver',
			'created'
		]


class FriendSerializer(serializers.ModelSerializer):
	friend = serializers.SerializerMethodField()
	preview = serializers.SerializerMethodField()
	updated = serializers.SerializerMethodField()
	
	class Meta:
		model = Connection
		fields = [
			'id',
			'friend',
			'preview',
			'updated'
		]

	def get_friend(self, obj):
		# If Im the sender
		if self.context['user'] == obj.sender:
			return UserSerializer(obj.receiver).data
		# If Im the receiver
		elif self.context['user'] == obj.receiver:
			return UserSerializer(obj.sender).data
		else:
			print('Error: No user found in friendserializer')

	def get_preview(self, obj):
		default = 'New connection'
		if not hasattr(obj, 'latest_text'):
			return default
		return obj.latest_text or default

	def get_updated(self, obj):
		if not hasattr(obj, 'latest_created'):
			date = obj.updated
		else:
			date = obj.latest_created or obj.updated
		return date.isoformat()




class MessageSerializer(serializers.ModelSerializer):
	is_me = serializers.SerializerMethodField()

	class Meta:
		model = Message
		fields = [
			'id',
			'is_me',
			'text',
			'created'
		]

	def get_is_me(self, obj):
		return self.context['user'] == obj.user
