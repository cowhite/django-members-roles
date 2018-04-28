from django import forms
from django.contrib.auth.models import Permission

from .models import BulkInvitation, Role, RolePermission


class BulkInvitationForm(forms.ModelForm):

    class Meta:
        model = BulkInvitation
        fields = ('emails',)
        exclude = ('invited_by', 'content_type', 'object_id')

    def save(self, user, content_type, object_id):
        instance = super(BulkInvitationForm, self).save(commit=False)
        instance.invited_by = user
        instance.content_type = content_type
        instance.object_id = object_id
        instance.save()
        return instance


class RoleForm(forms.ModelForm):

    class Meta:
        model = Role
        fields = ('name', 'description', 'permissions')

    def __init__(self, *args, **kwargs):
        content_type_id = kwargs.pop("content_type_id")
        super(RoleForm, self).__init__(*args, **kwargs)
        try:
            role_permission = RolePermission.objects.get(
                content_type_id=content_type_id).permissions
            permissions_list = list(
                role_permission.values_list("id", flat=True))
        except RolePermission.DoesNotExist:
            permissions_list = []
        self.fields['permissions'].queryset = self.fields[
            'permissions'].queryset.filter(id__in=permissions_list)

    def save(self, content_type, object_id):
        instance = super(RoleForm, self).save(commit=False)
        instance.content_type = content_type
        instance.object_id = object_id
        instance.save()
        return instance
