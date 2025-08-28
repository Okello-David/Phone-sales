from .forms import AssignmentForm, AssignedPhoneFormSet, ReassignPhoneForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.shortcuts import render, redirect
from .models import SalesAgent, Stock, Sale, Phone
from django import forms
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .forms import AssignmentForm
from .models import Assignment, AssignedPhone
from django.utils import timezone
from django.db.models import Max

#form to edite assigned phone
class AssignedPhoneForm(forms.ModelForm):
    class Meta:
        model = AssignedPhone
        fields = ['phone', 'quantity_given']

def edit_assigned_phone(request, pk):
    assigned_phone = get_object_or_404(AssignedPhone, pk=pk)

    if request.method == "POST":
        form = AssignedPhoneForm(request.POST, instance=assigned_phone)
        if form.is_valid():
            form.save()
            return redirect('assignments')
    else:
        form = AssignedPhoneForm(instance=assigned_phone)

    return render(request, 'core/edit_assigned_phone.html', {'form': form, 'assigned_phone': assigned_phone})

#delete function:
def delete_assigned_phone(request, assigned_phone_id):
    assigned_phone = get_object_or_404(AssignedPhone, pk=assigned_phone_id)
    assigned_phone.delete()
    return redirect('assignments')


def assignments_view(request):
    grouped = defaultdict(list)

    all_assignments = Assignment.objects.select_related('agent', 'previous_assignment__agent').prefetch_related('phones__phone')

    for assignment in all_assignments:
        grouped[assignment.agent].append(assignment)

    return render(request, 'core/assignment_list.html', {
        'grouped_assignments': grouped
    })




def reassign_phone(request, assignment_id):
    source_assignment = get_object_or_404(Assignment, id=assignment_id)
    source_items = source_assignment.phones.all()

    # Prepare form list for each phone in the source assignment
    phone_forms = []
    if request.method == 'POST':
        assignment_form = AssignmentForm(request.POST)
        if assignment_form.is_valid():
            new_assignment = assignment_form.save(commit=False)
            new_assignment.date_assigned = timezone.now()
            new_assignment.previous_assignment = source_assignment
            new_assignment.save()

            moved = False
            for item in source_items:
                form = ReassignPhoneForm(request.POST, prefix=f"phone_{item.id}")
                if form.is_valid() and form.cleaned_data.get('move'):
                    qty_to_move = form.cleaned_data.get('quantity_to_move', 0)
                    if qty_to_move > 0 and qty_to_move <= item.quantity_given:
                        AssignedPhone.objects.create(
                            assignment=new_assignment,
                            phone=item.phone,
                            quantity_given=qty_to_move
                        )
                        # Reduce quantity in source assignment
                        item.quantity_given -= qty_to_move
                        if item.quantity_given == 0:
                            item.delete()
                        else:
                            item.save()
                        moved = True
            if moved:
                return redirect('assignments')
    else:
        assignment_form = AssignmentForm(initial={'previous_assignment': source_assignment})
        for item in source_items:
            phone_forms.append(ReassignPhoneForm(
                prefix=f"phone_{item.id}",
                initial={
                    'phone_id': item.id,
                    'phone_name': item.phone.name,
                    'quantity_available': item.quantity_given,
                }
            ))

    return render(request, 'core/reassign_assignment.html', {
        'assignment_form': assignment_form,
        'phone_forms': phone_forms,
        'source_assignment': source_assignment
    })

def create_assignment(request):
    agent_id = request.GET.get('agent_id')
    initial_data = {'agent': agent_id} if agent_id else {}

    assignment_form = AssignmentForm(request.POST or None, initial=initial_data)
    phone_formset = AssignedPhoneFormSet(request.POST or None)


#the logic
    if request.method == 'POST':
        assignment_form = AssignmentForm(request.POST)
        phone_formset = AssignedPhoneFormSet(request.POST)
        if assignment_form.is_valid() and phone_formset.is_valid():
            assignment = assignment_form.save()
            phones = phone_formset.save(commit=False)
            for phone in phones:
                phone.assignment = assignment
                phone.save()

            if 'save_add' in request.POST:
                # 👇 Show success message
                messages.success(request, f"Phones assigned to {assignment.agent.full_name}. Add more if needed.")

                # 👇 Keep the same agent and other fields
                assignment_form = AssignmentForm(initial={
                    'agent': assignment.agent,
                    'remarks': assignment.remarks,
                    'previous_assignment': assignment.previous_assignment
                })
                phone_formset = AssignedPhoneFormSet()

                return render(request, 'core/create_assignment.html', {
                    'assignment_form': assignment_form,
                    'phone_formset': phone_formset,
                })

            else:
                messages.success(request, "Phone assignment created successfully.")
                return redirect('assignments')
    else:
        assignment_form = AssignmentForm()
        phone_formset = AssignedPhoneFormSet()

    return render(request, 'core/create_assignment.html', {
        'assignment_form': assignment_form,
        'phone_formset': phone_formset,
    })


def assignment_list(request):
    # Get all agents who have at least one assignment
    agents = SalesAgent.objects.filter(assignment__isnull=False).distinct()

    # Build a dictionary: agent -> list of assignments
    agent_assignments = {}
    for agent in agents:
        assignments = Assignment.objects.filter(agent=agent).prefetch_related('phones__phone')
        agent_assignments[agent] = assignments

    return render(request, 'core/assignment_list.html', {
        'agent_assignments': agent_assignments
    })

#end of forms
class StaffLoginView(LoginView):
    template_name = 'core/login.html'

    def form_valid(self, form):
        if not form.get_user().is_staff:
            messages.error(self.request, "Access denied: not a staff member.")
            return self.form_invalid(form)
        return super().form_valid(form)

def home(request):
    return render(request, 'core/home.html')

def agent_list(request):
    agents = SalesAgent.objects.all()
    return render(request, 'core/agent_list.html', {'agents': agents})

def stock_summary(request):
    stock = Stock.objects.all().order_by('-date')
    return render(request, 'core/stock_summary.html', {'stock': stock})

# Form to add sale
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['agent', 'phone', 'quantity_sold']

@login_required
def add_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SaleForm()
    return render(request, 'core/add_sale.html', {'form': form})

