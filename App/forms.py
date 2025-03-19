from django import forms
from .models import SportProvider
from django.contrib.auth.models import User

class SportProviderForm(forms.ModelForm):
    class Meta:
        model = SportProvider
        fields = ['company_name', 'company_email', 'company_phone', 'company_address', 'user']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name',
            }),
            'company_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company email',
            }),
            'company_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company phone',
            }),
            'company_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company address',
                'rows': 3,  # Adjust the number of rows for the textarea
            }),
            'user': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


from django import forms
from .models import SportPartner
from django.contrib.auth.models import User

class SportPartnerForm(forms.ModelForm):
    class Meta:
        model = SportPartner
        fields = ['company_name', 'company_email', 'company_phone', 'company_address', 'user']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name',
            }),
            'company_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company email',
            }),
            'company_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company phone',
            }),
            'company_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company address',
                'rows': 3,  # Adjust the number of rows for the textarea
            }),
            'user': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


from django import forms
from .models import SportActivity

class SportActivityForm(forms.ModelForm):
    class Meta:
        model = SportActivity
        fields = ['activity_name']
        widgets = {
            'activity_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter activity name',
            }),
        }


from django import forms
from .models import Contract, SportPartner

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['sport_partner', 'start_date', 'end_date']
        widgets = {
            'sport_partner': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }



from django import forms
from .models import SportWorker

class SportWorkerForm(forms.ModelForm):
    class Meta:
        model = SportWorker
        fields = ['first_name', 'last_name', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
            }),
        }



from django import forms
from .models import Contract, SportProvider, SportPartner
from django.core.exceptions import ValidationError

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['sport_provider', 'sport_partner', 'start_date', 'end_date']
        widgets = {
            'sport_provider': forms.Select(attrs={
                'class': 'form-control',
            }),
            'sport_partner': forms.Select(attrs={
                'class': 'form-control',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',  # Use HTML5 date input
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',  # Use HTML5 date input
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Validate that the start date is before the end date
        if start_date and end_date and start_date >= end_date:
            raise ValidationError("Start date must be before end date.")

        return cleaned_data
    



from django import forms
from .models import AllowedActivity, Contract, SportActivity

class AllowedActivityForm(forms.ModelForm):
    class Meta:
        model = AllowedActivity
        fields = ['contract', 'sport_activity', 'allowed']
        widgets = {
            'contract': forms.Select(attrs={
                'class': 'form-control',
            }),
            'sport_activity': forms.Select(attrs={
                'class': 'form-control',
            }),
            'allowed': forms.CheckboxInput(attrs={
                'class': 'form-check-input,ml-3',
                'style': 'width: 25px; height: 25px;',  # Increase checkbox size
            }),
        }

from django import forms
from .models import SportProvider, SportPartner

class AttendanceReportForm(forms.Form):
    sport_provider = forms.ModelChoiceField(
        queryset=SportProvider.objects.all(), 
        required=False, 
        label="Sport Provider",
        widget=forms.Select(attrs={
            'class': 'form-control',  # Bootstrap class for form control
            'placeholder': 'Select Sport Provider',
        })
    )
    sport_partner = forms.ModelChoiceField(
        queryset=SportPartner.objects.all(), 
        required=False, 
        label="Sport Partner",
        widget=forms.Select(attrs={
            'class': 'form-control',  # Bootstrap class for form control
            'placeholder': 'Select Sport Partner',
        })
    )
    from_date = forms.DateField(
        required=False, 
        label="From Date",
        widget=forms.DateInput(attrs={
            'class': 'form-control',  # Bootstrap class for form control
            'type': 'date',  # HTML5 date input
        })
    )
    to_date = forms.DateField(
        required=False, 
        label="To Date",
        widget=forms.DateInput(attrs={
            'class': 'form-control',  # Bootstrap class for form control
            'type': 'date',  # HTML5 date input
        })
    )