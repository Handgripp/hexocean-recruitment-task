import pathlib

import jwt
from PIL import Image
from decouple import config
from django.contrib import admin, messages
from django import forms
from .models.user_model import Users
from .models.image_model import ImagesAdmin, LinksAdmin

admin.site.register(Users)


class ImageAdminForm(forms.ModelForm):
    height = forms.IntegerField(required=True, initial=1)
    width = forms.IntegerField(required=True, initial=1)

    class Meta:
        model = ImagesAdmin
        fields = ['path', 'height', 'width']


@admin.register(ImagesAdmin)
class ImageAdmin(admin.ModelAdmin):
    form = ImageAdminForm

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        height = request.POST.get('height')
        width = request.POST.get('width')
        image_file = form.cleaned_data.get('path')
        file_format_without_dot = pathlib.Path(image_file.name).suffix.replace(".", "")
        img = Image.open(image_file)

        img_resized = img.resize((int(width), int(height)))

        resized_image_name = 'resized_' + image_file.name.replace(' ', '_')
        resized_image_path = 'media/' + resized_image_name

        img_resized.save(resized_image_path, format=file_format_without_dot)

        obj.resized_path = resized_image_name
        obj.save()

    def message_user(self, request, message, level=messages.INFO, extra_tags='', fail_silently=False):
        if level == messages.SUCCESS:
            image_id = message.split('(')[-1].split(')')[0]

            image_original = ImagesAdmin.objects.get(id=image_id)
            new_image_path = 'media/resized_' + str(image_original.path)

            new_image = ImagesAdmin()
            new_image.path = new_image_path
            new_image.save()

            image_resized = ImagesAdmin.objects.get(path=new_image_path)

            api_base_url = config('API_BASE_URL')

            url = f"Link to uploaded image: {api_base_url}images-admin/{image_id}\n" \
                  f"Link to uploaded image: {api_base_url}images-admin/{image_resized.id}\n"

        super().message_user(request, url, level, extra_tags, fail_silently)


class LinkAdminForm(forms.ModelForm):
    image_id = forms.CharField(required=True)
    expiration_time = forms.IntegerField(required=True)
    class Meta:
        model = ImagesAdmin
        fields = ['image_id', 'expiration_time']


@admin.register(LinksAdmin)
class LinkAdmin(admin.ModelAdmin):
    form = LinkAdminForm

    def message_user(self, request, message, level=messages.INFO, extra_tags='', fail_silently=False):
        expiration_time = request.POST.get('expiration_time')
        image_id = request.POST.get('image_id')
        if image_id:
            api_base_url = config('API_BASE_URL')
            image = ImagesAdmin.objects.filter(id=image_id).first()

            if image:
                image_id_str = str(image.id)

                token = jwt.encode({"id": image_id_str, "exp": expiration_time}, config('SIGNING_KEY'),
                                   algorithm="HS256")

                link = f"Link: {api_base_url}/images-admin/{image_id_str}?expires_token={token}"

                super().message_user(request, link, level, extra_tags, fail_silently)
