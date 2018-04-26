from django import forms

from .models import Organization


class OrganizationForm(forms.ModelForm):

    class Meta:
        model = Organization
        fields = ('name', 'location',)
        exclude = ('created_by',)

    def save(self, user):
        instance = super(OrganizationForm, self).save(commit=False)
        instance.created_by = user
        instance.save()
        return instance
