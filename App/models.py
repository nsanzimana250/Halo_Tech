from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class SportProvider(models.Model):
    company_name = models.CharField(max_length=255)
    company_email = models.EmailField(unique=True)
    company_phone = models.CharField(max_length=20)
    company_address = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sport_providers")

    def __str__(self):
        return self.company_name


class SportPartner(models.Model):
    company_name = models.CharField(max_length=255)
    company_email = models.EmailField(unique=True)
    company_phone = models.CharField(max_length=20)
    company_address = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sport_partners")

    def __str__(self):
        return self.company_name

class SportWorker(models.Model):
    sport_partner = models.ForeignKey(SportPartner, on_delete=models.CASCADE, related_name='sport_works')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    from django.db import models

class SportCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    sport_worker = models.ForeignKey(
        'SportWorker', on_delete=models.CASCADE, related_name='sport_codes'
    )
    
    def __str__(self):
        return self.code


class SportActivity(models.Model):
    sport_provider = models.ForeignKey(SportProvider, on_delete=models.CASCADE, related_name='sport_activities')
    activity_name = models.CharField(max_length=255)
    def __str__(self):
        return self.activity_name

class Contract(models.Model):
    sport_provider = models.ForeignKey(SportProvider, on_delete=models.CASCADE, related_name="contracts")
    sport_partner = models.ForeignKey(SportPartner, on_delete=models.CASCADE, related_name="contracts")
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ('sport_provider', 'sport_partner', 'start_date')

    def __str__(self):
        return f"Contract: {self.sport_provider.company_name} & {self.sport_partner.company_name}"

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("Start date must be before end date.")
        

class Attendance(models.Model):
    sport_provider = models.ForeignKey(SportProvider, on_delete=models.CASCADE, related_name="attendances")
    sport_partner = models.ForeignKey(SportPartner, on_delete=models.CASCADE, related_name="attendances")
    sport_work = models.ForeignKey(SportWorker, on_delete=models.CASCADE, related_name="attendances")
    sport_activity = models.ForeignKey(SportActivity, on_delete=models.CASCADE, related_name="attendances")
    activity_date = models.DateField(auto_now_add=True)
    activity_time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sport_work.first_name} {self.sport_work.last_name} - {self.sport_activity.activity_name} on {self.activity_date} at {self.activity_time}"


class AllowedActivity(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="allowed_activities")
    sport_activity = models.ForeignKey(SportActivity, on_delete=models.CASCADE, related_name="allowed_for_contracts")
    allowed = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.sport_activity.activity_name} for {self.contract.sport_partner.company_name}"