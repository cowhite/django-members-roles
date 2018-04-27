from django import forms

from .models import BulkInvitation, Role


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
        fields = ('name', 'description')

    def save(self, content_type, object_id):
        instance = super(RoleForm, self).save(commit=False)
        instance.content_type = content_type
        instance.object_id = object_id
        instance.save()
        return instance
