from django import forms

from .models import BulkInvitation


class BulkInvitationForm(forms.ModelForm):

    class Meta:
        model = BulkInvitation
        fields = ('emails',)
        exclude = ('invited_by', 'content_type', 'object_id')

    def save(self, user, content_type, object_id):
        instance = super(OrganizationForm, self).save(commit=False)
        instance.invited_by = user
        instance.content_type = content_type
        instance.object_id = object_id
        instance.save()
        return instance
