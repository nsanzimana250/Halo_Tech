from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import SportProvider, SportPartner, Contract, SportWorker, Attendance, SportActivity, AllowedActivity, SportCode
from django.utils import timezone
import random
import africastalking
from datetime import datetime
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from .models import SportProvider, SportActivity, Contract, SportPartner, AllowedActivity, SportWorker
from .forms import SportActivityForm, ContractForm
from django.contrib.auth.decorators import login_required

# Africa's Talking Credentials
africastalking.initialize(username='heloteck', api_key='atsk_c5c688c3b92798e5d6df618317734b7edd81cf547a8e70a3e33ebcfe19e61b0deb6ab53a')
sms = africastalking.SMS

# password = Tg8@rLz2


# _________________________________________________________________________________________
#____________________________user_login______________________________________
# __________________________________________________________________________________________

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Check user role
            is_sport_provider = SportProvider.objects.filter(user=user).exists()
            is_sport_partner = SportPartner.objects.filter(user=user).exists()

            if user.is_superuser:
                return redirect("halo_tech_dashboard")
            elif is_sport_provider:
                return redirect("sport_provider_dashboard")
            elif is_sport_partner:
                return redirect("sport_partner_dashboard")

            messages.error(request, "User role not assigned!")
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, "login.html")
# _________________________________________________________________________________________
#________________________________user_logout__________________________________
# __________________________________________________________________________________________
def user_logout(request):
    logout(request)
    return redirect('login')
# _________________________________________________________________________________________
#____________________________sport_provider_dashboard______________________________________
# __________________________________________________________________________________________

@login_required
def sport_provider_dashboard(request):
    user = request.user
    sport_provider = SportProvider.objects.filter(user=user).first() 
    if not sport_provider:
        return redirect('login')    

    myContract = Contract.objects.filter(sport_provider=sport_provider)

    if request.method == "POST":
        sport_partner_id = request.POST.get("sport_partner")
        if sport_partner_id:
            request.session["selected_sport_partner"] = sport_partner_id
            return redirect("check_customer")  # Redirect to Step Two
        
        

    context = {
        'company_name': sport_provider.company_name,
        'company_email': sport_provider.company_email,
        'company_phone': sport_provider.company_phone,
        'company_address': sport_provider.company_address,
        "sport_provider": sport_provider,
        "myContract": myContract,
    }
    return render(request, "sport_provider_dashboard/sport_provider_dashboard.html", context)

# _________________________________________________________________________________________
#____________________________check_customer________________________________________________
# __________________________________________________________________________________________
@login_required
def check_customer(request):
    user = request.user
    sport_provider = SportProvider.objects.filter(user=user).first()

    if not sport_provider:
        return redirect('login')

    sport_partner_id = request.GET.get("sport_partner")
    if not sport_partner_id:
        return redirect("sport_provider_dashboard")

    sport_partner = SportPartner.objects.filter(id=sport_partner_id).first()
    worker = None
    step_three_visible = False

    # Get allowed activities for this sport provider and partner
    contract = Contract.objects.filter(sport_provider=sport_provider, sport_partner=sport_partner).first()
    allowed_activities = AllowedActivity.objects.filter(contract=contract, allowed=True) if contract else []
    sport_activities = [aa.sport_activity for aa in allowed_activities]

    if request.method == "POST":
        if "phone_number" in request.POST:
            # Step One: Retrieve Worker
            phone_number = request.POST.get("phone_number")
            worker = SportWorker.objects.filter(sport_partner=sport_partner, phone_number=phone_number).first()
            if worker:
                step_three_visible = True
                messages.success(request, "Customer found successfully! Proceed to the next step.")
                request.session["worker_phone"] = phone_number  # Store worker in session
            else:
                messages.error(request, "No customer found with this phone number in the selected company.")

        elif "Activity" in request.POST:
            # Step Three: Generate Code, Send SMS, and Save Attendance
            activity_id = request.POST.get("Activity")
            phone_number = request.session.get("worker_phone")  # Retrieve worker from session
            worker = SportWorker.objects.filter(sport_partner=sport_partner, phone_number=phone_number).first()
            activity = SportActivity.objects.filter(id=activity_id).first()

            # Debugging
            if not worker:
                messages.error(request, "Worker not found! Check phone number.")
            if not activity:
                messages.error(request, f"Activity not found! ID: {activity_id}")

            if worker and activity:
                try:
                    # Generate a 6-digit random code
                    generated_code = str(random.randint(100000, 999999))

                    # Save Code to Database
                    SportCode.objects.create(code=generated_code, sport_worker=worker)
                    messages.success(request, f"Code {generated_code} generated and saved.")

                    # Send Code via Africa's Talking
                    sms.send(f"Your sport verification code: {generated_code}", [worker.phone_number])
                    messages.success(request, f"Verification code sent to {worker.phone_number}.")

                    # Save Attendance
                    Attendance.objects.create(
                        sport_provider=sport_provider,
                        sport_partner=sport_partner,
                        sport_work=worker,
                        sport_activity=activity
                    )
                    messages.success(request, "Attendance recorded successfully.")
                
                except Exception as e:
                    messages.error(request, f"Error: {str(e)}")

    context = {
        'company_name': sport_provider.company_name,
        'company_email': sport_provider.company_email,
        'company_phone': sport_provider.company_phone,
        'company_address': sport_provider.company_address,
        "sport_partner_id": sport_partner_id,
        "worker": worker,
        "sport_partner": sport_partner,
        "step_three_visible": step_three_visible,
        "sport_activities": sport_activities,  # Ensure activities are available in the template
    }
    return render(request, "sport_provider_dashboard/check_customer.html", context)




@login_required
def Contract_list(request):
    user = request.user
    sport_provider = SportProvider.objects.filter(user=user).first()
    
    if not sport_provider:
        return redirect('login')
    
    contracts = Contract.objects.filter(sport_provider=sport_provider)
    total_contracts = contracts.count() 
    
    context = {
                'company_name': sport_provider.company_name,
        'company_email': sport_provider.company_email,
        'company_phone': sport_provider.company_phone,
        'company_address': sport_provider.company_address,
        'sport_provider': sport_provider,
        'contract_records': contracts,
          'total_contracts': total_contracts,  # Make sure this matches the template variable
    }
    return render(request, 'sport_provider_dashboard/Contract.html', context)


@login_required
def daily_report(request):
    user = request.user
    sport_provider = SportProvider.objects.filter(user=user).first()

    if not sport_provider:
        return redirect('login')

    selected_date = request.POST.get('day')  # Get the date from the form

    # If a date is selected, filter attendance records for that date
    if selected_date:
        attendance_records = Attendance.objects.filter(
            sport_provider=sport_provider,
            activity_date=selected_date
        )
    else:
        attendance_records = []

    context = {
                'company_name': sport_provider.company_name,
        'company_email': sport_provider.company_email,
        'company_phone': sport_provider.company_phone,
        'company_address': sport_provider.company_address,
        'sport_provider': sport_provider,
        'attendance_records': attendance_records,
        'selected_date': selected_date,  # Pass the selected date to the template
    }
    return render(request, 'sport_provider_dashboard/daily_report.html', context)


@login_required
def monthly_report(request):
    user = request.user
    sport_provider = SportProvider.objects.filter(user=user).first()
    
    if not sport_provider:
        return redirect('login')

    attendances = Attendance.objects.filter(sport_provider=sport_provider)
    
    # Handle form submission
    if request.method == 'POST':
        from_date = request.POST.get('from')
        to_date = request.POST.get('to')
        
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            attendances = attendances.filter(activity_date__gte=from_date)
        
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            attendances = attendances.filter(activity_date__lte=to_date)

        context = {
            'sport_provider': sport_provider,
            'attendance_records': attendances,
            'from_date': from_date,
            'to_date': to_date,
        }
    else:
        context = {
                'company_name': sport_provider.company_name,
        'company_email': sport_provider.company_email,
        'company_phone': sport_provider.company_phone,
        'company_address': sport_provider.company_address,
            'sport_provider': sport_provider,
            'attendance_records': None,
        }
    
    return render(request, 'sport_provider_dashboard/month_report.html', context)


@login_required
def custom_reports(request):
    user = request.user
    sport_provider = SportProvider.objects.filter(user=user).first()

    if not sport_provider:
        return redirect('login')

    # Get all contracts for this provider
    contracts = Contract.objects.filter(sport_provider=sport_provider)

    if request.method == 'POST':
        # Get the selected contract, from date, and to date
        contract_id = request.POST.get('contract')
        from_date = request.POST.get('from')
        to_date = request.POST.get('to')

        # If a contract is selected, filter attendance by contract and date range
        if contract_id and from_date and to_date:
            contract = Contract.objects.get(id=contract_id)
            attendances = Attendance.objects.filter(
                sport_provider=sport_provider,
                sport_partner=contract.sport_partner,
                activity_date__range=[from_date, to_date]
            )
        else:
            attendances = None
            error = "Please select a contract and date range."

        context = {
            'company_name': sport_provider.company_name,
            'company_email': sport_provider.company_email,
            'company_phone': sport_provider.company_phone,
            'company_address': sport_provider.company_address,
            'role': "Sport Partner",
            'contracts': contracts,
            'attendances': attendances,
            'from_date': from_date,
            'to_date': to_date,
            'error': error if 'error' in locals() else None,
        }

        return render(request, "sport_provider_dashboard/Custom_Report.html", context)

    context = {
        'company_name': sport_provider.company_name,
        'company_email': sport_provider.company_email,
        'company_phone': sport_provider.company_phone,
        'company_address': sport_provider.company_address,
        'role': "Sport Partner",
        'contracts': contracts,
    }

    return render(request, "sport_provider_dashboard/Custom_Report.html", context)



@login_required
def AllsportWorker(request):
    user = request.user
    sport_provider = SportProvider.objects.filter(user=user).first()
    
    if not sport_provider:
        return redirect('login')
    
    # Get the sport_partner from the form (if needed)
    sport_partner = request.GET.get('sport_partner')  # Example of getting from GET request
    
    # Filter attendances based on the sport_provider and optionally sport_partner
    attendances = Attendance.objects.filter(sport_provider=sport_provider)
    
    if sport_partner:
        attendances = attendances.filter(sport_partner_id=sport_partner)  # Optional filter by sport_partner

    context = {
        'company_name': sport_provider.company_name,
        'company_email': sport_provider.company_email,
        'company_phone': sport_provider.company_phone,
        'company_address': sport_provider.company_address,
        'role': "Sport Partner",
        'sport_provider': sport_provider,
        'attendance_records': attendances,
    }
    return render(request, 'sport_provider_dashboard/AllsportWorker.html', context)





# ***********************************************************************************************************************************
# ***********************************************************************************************************************************
# *******************************************sport_partner_dashboard*****************************************************************
# ***********************************************************************************************************************************
# ***********************************************************************************************************************************
@login_required
def sport_partner_dashboard(request):
    user = request.user
    sport_partner = SportPartner.objects.filter(user=user).first()

    if not sport_partner:
        return redirect('login') 
    
    sport_workers = SportWorker.objects.filter(sport_partner=sport_partner)
    total_employees = sport_workers.count()  # Count total employees

    context = {
        'company_name': sport_partner.company_name,
        'company_email': sport_partner.company_email,
        'company_phone': sport_partner.company_phone,
        'company_address': sport_partner.company_address,
        'role': "Sport Partner",
        'sport_workers': sport_workers,
        'total_employees': total_employees,  # Pass employee count to template
    }
    return render(request, "sport_pertner_dashboard/sport_partner_dashboard.html", context)


@login_required
def day_report(request):
    user = request.user
    sport_partner = SportPartner.objects.filter(user=user).first()
    if not sport_partner:
        return redirect('login') 

    if request.method == "POST":
        selected_date = request.POST.get("day")  # Get the selected date from the form
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

        # Fetch the attendance data for the selected date
        attendances = Attendance.objects.filter(sport_partner=sport_partner, activity_date=selected_date)

        if not attendances.exists():  # Check if there are no records for that day
            message = f"No records found for {selected_date}."
            return render(request, "sport_pertner_dashboard/day_report.html", {"message": message})
        else:
            return render(request, "sport_pertner_dashboard/day_report.html", {"attendances": attendances, "selected_date": selected_date})
    context = {
        'company_name': sport_partner.company_name,
        'company_email': sport_partner.company_email,
        'company_phone': sport_partner.company_phone,
        'company_address': sport_partner.company_address,
        'role': "Sport Partner"
    }


    return render(request, "sport_pertner_dashboard/day_report.html",context)


@login_required
def Monthly_Report(request):
    user = request.user
    sport_partner = SportPartner.objects.filter(user=user).first()
    if not sport_partner:
        return redirect('login')

    context = {
        'company_name': sport_partner.company_name,
        'company_email': sport_partner.company_email,
        'company_phone': sport_partner.company_phone,
        'company_address': sport_partner.company_address,
        'role': "Sport Partner",
    }

    if request.method == "POST":
        # Get the starting and ending dates from the form
        from_date = request.POST.get("from")
        to_date = request.POST.get("to")

        if from_date and to_date:
            # Convert the dates to datetime objects
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

            # Filter the attendance records based on the selected date range
            attendances = Attendance.objects.filter(
                sport_partner=sport_partner,
                activity_date__range=[from_date, to_date]
            )

            if not attendances.exists():  # No records found
                message = f"No records found for the selected period ({from_date} to {to_date})."
                return render(request, "sport_pertner_dashboard/Monthly_Report.html", {
                    **context,
                    "message": message
                })
            else:
                # Pass the filtered attendances and the selected date range to the template
                return render(request, "sport_pertner_dashboard/Monthly_Report.html", {
                    **context,
                    "attendances": attendances,
                    "from_date": from_date,
                    "to_date": to_date,
                })

    return render(request, "sport_pertner_dashboard/Monthly_Report.html", context)

@login_required
def Custom_Report(request):
    user = request.user
    sport_partner = SportPartner.objects.filter(user=user).first()

    if not sport_partner:
        return redirect('login')

    # Initialize variables for filtering
    from_date = None
    to_date = None
    selected_contract = None

    # Handling form submission
    if request.method == "POST":
        # Get form data
        selected_contract = request.POST.get('contract')
        from_date = request.POST.get('from')
        to_date = request.POST.get('to')

        # Convert date strings to datetime objects
        from_date = timezone.datetime.strptime(from_date, '%Y-%m-%d') if from_date else None
        to_date = timezone.datetime.strptime(to_date, '%Y-%m-%d') if to_date else None

        # Filter attendance based on sport_provider and sport_partner
        attendances = Attendance.objects.filter(
            sport_partner=sport_partner
        )

        if selected_contract:
            contract = Contract.objects.get(id=selected_contract)
            attendances = attendances.filter(sport_provider=contract.sport_provider)

        if from_date:
            attendances = attendances.filter(activity_date__gte=from_date)

        if to_date:
            attendances = attendances.filter(activity_date__lte=to_date)

    else:
        attendances = []

    # Populate contracts available for the sport partner
    contracts = Contract.objects.filter(sport_partner=sport_partner)

    context = {
        'company_name': sport_partner.company_name,
        'company_email': sport_partner.company_email,
        'company_phone': sport_partner.company_phone,
        'company_address': sport_partner.company_address,
        'role': "Sport Partner",
        'contracts': contracts,  # Pass available contracts to the form
        'attendances': attendances,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, "sport_pertner_dashboard/Custom_Report.html", context)





def Contracts_SportPartner(request):
    user = request.user
    sport_partner = SportPartner.objects.filter(user=user).first()
    
    if not sport_partner:
        return redirect('login')

    contracts = Contract.objects.filter(sport_partner=sport_partner)
    total_contracts = contracts.count()  # Count total contracts

    context = {
        'company_name': sport_partner.company_name,
        'company_email': sport_partner.company_email,
        'company_phone': sport_partner.company_phone,
        'company_address': sport_partner.company_address,
        'role': "Sport Partner",
        'contracts': contracts,
        'total_contracts': total_contracts,  # Pass the count to the template
    }

    return render(request, "sport_pertner_dashboard/Contracts.html", context)




# import africastalking

# africastalking.initialize(username='heloteck', api_key='atsk_c5c688c3b92798e5d6df618317734b7edd81cf547a8e70a3e33ebcfe19e61b0deb6ab53a')
# sms = africastalking.SMS

# response = sms.send("Test message from Django", ["+250789865312"])
# print(response)

# from core.models import SportWorker

# # Get a worker by phone number
# worker = SportWorker.objects.filter(phone_number="+250789123456").first()
# print(worker)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import SportProvider, SportPartner, SportWorker, SportCode, SportActivity, Contract, Attendance, AllowedActivity

@login_required
def halo_tech_dashboard(request):
    # Fetch all data
    sport_providers = SportProvider.objects.all()
    sport_partners = SportPartner.objects.all()
    sport_workers = SportWorker.objects.all()
    sport_codes = SportCode.objects.all()
    sport_activities = SportActivity.objects.all()
    contracts = Contract.objects.all()
    attendances = Attendance.objects.all()
    allowed_activities = AllowedActivity.objects.all()

    # Statistics
    total_providers = sport_providers.count()
    total_partners = sport_partners.count()
    total_workers = sport_workers.count()
    total_activities = sport_activities.count()
    total_contracts = contracts.count()
    total_attendances = attendances.count()

    # Pass data to the template
    context = {
        'sport_providers': sport_providers,
        'sport_partners': sport_partners,
        'sport_workers': sport_workers,
        'sport_codes': sport_codes,
        'sport_activities': sport_activities,
        'contracts': contracts,
        'attendances': attendances,
        'allowed_activities': allowed_activities,
        'total_providers': total_providers,
        'total_partners': total_partners,
        'total_workers': total_workers,
        'total_activities': total_activities,
        'total_contracts': total_contracts,
        'total_attendances': total_attendances,
    }
    return render(request, "halo_tech_dashboard/halo.html", context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages  # Import messages
from django.shortcuts import render, redirect
from .models import SportProvider
from .forms import SportProviderForm
from django.contrib.auth.decorators import login_required

@login_required
def users(request):
    all_users = User.objects.all()
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully!")  # Add success message
            return redirect('users')
        else:
            messages.error(request, "Error creating user. Please check the form.")  # Add error message

    return render(request, "halo_tech_dashboard/users.html", {
        'users': all_users,
        'form': form,
    })


@login_required
def SportProvidepage(request):
    sport_providers = SportProvider.objects.all()
    search_query = request.GET.get('search', '')
    if search_query:
        sport_providers = sport_providers.filter(company_name__icontains=search_query)
    if request.method == 'POST':
        form = SportProviderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('SportProvidepage') 
    else:
        form = SportProviderForm()
    return render(request, "halo_tech_dashboard/SportProvider.html", {
        'sport_providers': sport_providers,
        'form': form,
        'search_query': search_query,
    })


from django.shortcuts import render, redirect
from .models import SportPartner
from .forms import SportPartnerForm
from django.contrib.auth.decorators import login_required

@login_required
def SportPartnerpage(request):
    # Fetch all SportPartner objects from the database
    sport_partners = SportPartner.objects.all()

    # Handle search query
    search_query = request.GET.get('search', '')
    if search_query:
        sport_partners = sport_partners.filter(company_name__icontains=search_query)

    # Handle form submission for creating a new sport partner
    if request.method == 'POST':
        form = SportPartnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('SportPartnerpage')  # Redirect to the same page after saving
    else:
        form = SportPartnerForm()

    # Pass the form, sport partners, and search query to the template
    return render(request, "halo_tech_dashboard/SportPartner.html", {
        'sport_partners': sport_partners,
        'form': form,
        'search_query': search_query,
    })


@login_required
def SportProviderDetails(request, pk):
    # Fetch the specific SportProvider by primary key (pk)
    provider = get_object_or_404(SportProvider, pk=pk)
    
    # Fetch all SportActivity objects related to this SportProvider
    activities = SportActivity.objects.filter(sport_provider=provider)
    
    # Fetch all Contract objects related to this SportProvider
    contracts = Contract.objects.filter(sport_provider=provider)
    
    # Fetch AllowedActivity objects for each contract
    allowed_activities = {}
    for contract in contracts:
        allowed_activities[contract.id] = AllowedActivity.objects.filter(contract=contract)
    
    # Fix: Correctly count SportWorker instances associated with this SportProvider
    sport_workers_count = SportWorker.objects.filter( 
    sport_partner__in=SportPartner.objects.filter(
        id__in=Contract.objects.filter(sport_provider=provider).values_list("sport_partner", flat=True)
    )).count()

    
    # Handle form submission for creating a new SportActivity or Contract
    if request.method == 'POST':
        if 'activity_form' in request.POST:  # Check if the activity form is submitted
            activity_form = SportActivityForm(request.POST)
            if activity_form.is_valid():
                activity = activity_form.save(commit=False)
                activity.sport_provider = provider  # Associate the activity with the provider
                activity.save()
                return redirect('sport_provider_details', pk=provider.pk)
        elif 'contract_form' in request.POST:  # Check if the contract form is submitted
            contract_form = ContractForm(request.POST)
            if contract_form.is_valid():
                contract = contract_form.save(commit=False)
                contract.sport_provider = provider  # Associate the contract with the provider
                contract.save()
                return redirect('sport_provider_details', pk=provider.pk)
    else:
        activity_form = SportActivityForm()
        contract_form = ContractForm()
    
    # Pass the provider, activities, contracts, allowed_activities, sport_workers_count, and forms to the template
    return render(request, "halo_tech_dashboard/SportProvide_details.html", {
        'provider': provider,
        'activities': activities,
        'contracts': contracts,
        'allowed_activities': allowed_activities,
        'sport_workers_count': sport_workers_count,
        'activity_form': activity_form,
        'contract_form': contract_form,
    })
from django.shortcuts import render, get_object_or_404, redirect
from .models import SportPartner, SportWorker, Contract, AllowedActivity
from .forms import SportWorkerForm  # Import the SportWorkerForm

def SportPartner_details(request, pk):
    # Fetch the SportPartner object based on the provided pk
    partner = get_object_or_404(SportPartner, pk=pk)
    
    # Fetch all SportWorker objects related to this SportPartner
    workers = partner.sport_works.all()
    
    # Fetch all Contract objects related to this SportPartner
    contracts = partner.contracts.all()
    
    # Fetch allowed activities for each contract
    contracts_with_activities = []
    for contract in contracts:
        allowed_activities = contract.allowed_activities.all()  # Use the related_name
        contracts_with_activities.append({
            'contract': contract,
            'allowed_activities': allowed_activities,
        })
    
    # Handle form submissions
    if request.method == 'POST':
        if 'add_worker' in request.POST:  # Check if the worker form was submitted
            form = SportWorkerForm(request.POST)
            if form.is_valid():
                worker = form.save(commit=False)
                worker.sport_partner = partner  # Associate the worker with the current partner
                worker.save()
                return redirect('SportPartner_details', pk=partner.pk)
    else:
        form = SportWorkerForm()
    
    # Pass the partner, workers, contracts_with_activities, and form to the template
    return render(request, 'halo_tech_dashboard/SportPartner_details.html', {
        'partner': partner,
        'workers': workers,
        'contracts_with_activities': contracts_with_activities,
        'form': form,
    })




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Contract
from .forms import ContractForm

@login_required
def CreateContract(request):
    # Fetch all existing contracts
    contracts = Contract.objects.all()
    
    # Handle form submission
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new contract
            return redirect('CreateContract')  # Redirect to the same page after saving
    else:
        form = ContractForm()
    
    # Pass the form and contracts to the template
    return render(request, 'halo_tech_dashboard/CreateContract.html', {
        'form': form,
        'contracts': contracts,
    })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import AllowedActivity
from .forms import AllowedActivityForm

@login_required
def AllowedActivitys(request):
    # Fetch all existing allowed activities
    allowed_activities = AllowedActivity.objects.all()
    
    # Handle form submission
    if request.method == 'POST':
        form = AllowedActivityForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new allowed activity
            return redirect('AllowedActivitys')  # Redirect to the same page after saving
    else:
        form = AllowedActivityForm()
    
    # Pass the form and allowed activities to the template
    return render(request, 'halo_tech_dashboard/AllowedActivity.html', {
        'form': form,
        'allowed_activities': allowed_activities,
    })




from django.shortcuts import render
from .forms import AttendanceReportForm
from .models import Attendance

def attendance_report(request):
    """Render the report page with a form."""
    form = AttendanceReportForm(request.GET or None)
    return render(request, 'halo_tech_dashboard/Report.html', {'form': form})

def filtered_results(request):
    """Handle filtering logic and render the report page with details."""
    form = AttendanceReportForm(request.GET or None)
    attendances = Attendance.objects.all()  # Default: return all records

    # Extract filter values
    sport_provider = None
    sport_partner = None
    from_date = None
    to_date = None

    if form.is_valid():
        sport_provider = form.cleaned_data.get('sport_provider')
        sport_partner = form.cleaned_data.get('sport_partner')
        from_date = form.cleaned_data.get('from_date')
        to_date = form.cleaned_data.get('to_date')

        if sport_provider:
            attendances = attendances.filter(sport_provider=sport_provider)
        if sport_partner:
            attendances = attendances.filter(sport_partner=sport_partner)
        if from_date:
            attendances = attendances.filter(activity_date__gte=from_date)
        if to_date:
            attendances = attendances.filter(activity_date__lte=to_date)

    # Pass filter values and attendance data to the template
    return render(request, 'halo_tech_dashboard/FilteredResults.html', {
        'attendances': attendances,
        'sport_provider': sport_provider,
        'sport_partner': sport_partner,
        'from_date': from_date,
        'to_date': to_date
    })

