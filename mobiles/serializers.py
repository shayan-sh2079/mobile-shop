from rest_framework import serializers

from .models import Mobile, MobileImage


class MobileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileImage
        fields = "__all__"


class MobileSerializer(serializers.ModelSerializer):
    images = MobileImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=400, allow_empty_file=False),
        write_only=True,
        required=False,
    )
    added_image = serializers.ImageField(
        max_length=400, allow_empty_file=False, write_only=True, required=False
    )

    def delete_images(self, instance):
        instance.images.all().delete()

    def update(self, instance, validated_data):
        uploaded_images = (
            validated_data.pop("uploaded_images")
            if "uploaded_images" in validated_data
            else None
        )
        added_image = (
            validated_data.pop("added_image")
            if "added_image" in validated_data
            else None
        )

        if (uploaded_images is not None) and (added_image is not None):
            raise serializers.ValidationError(
                "You should only provide one of the keys 'added_image' or "
                "'uploaded_images'"
            )

        if uploaded_images is not None:
            self.delete_images(instance)
            for img in uploaded_images:
                MobileImage.objects.create(mobile=instance, img=img)

        if added_image is not None:
            MobileImage.objects.create(mobile=instance, img=added_image)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance

    def create(self, validated_data):
        uploaded_images = (
            validated_data.pop("uploaded_images")
            if "uploaded_images" in validated_data
            else None
        )
        added_image = (
            validated_data.pop("added_image")
            if "added_image" in validated_data
            else None
        )

        if (uploaded_images is not None) and (added_image is not None):
            raise serializers.ValidationError(
                "You should only provide one of the keys 'added_image' or "
                "'uploaded_images'"
            )

        mobile = Mobile.objects.create(**validated_data)
        if uploaded_images is not None:
            self.delete_images(mobile)
            for img in uploaded_images:
                MobileImage.objects.create(mobile=mobile, img=img)

        if added_image is not None:
            MobileImage.objects.create(mobile=mobile, img=added_image)

        return mobile

    class Meta:
        model = Mobile
        fields = "__all__"
        extra_kwargs = {"seller": {"read_only": True}}
