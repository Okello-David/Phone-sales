# create your models

from django.db import models
from django.utils import timezone






class SalesAgent(models.Model):
    full_name = models.CharField(max_length=100)
    phone_contact = models.CharField(max_length=15)
    agent_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.full_name} ({self.agent_number})"


class Phone(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.brand} {self.name} ({self.model})"



class Stock(models.Model):
    date = models.DateField()
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE)
    stock_received = models.PositiveIntegerField(default=0)
    stock_out_to_teams = models.PositiveIntegerField(default=0)
    stock_at_office = models.PositiveIntegerField(default=0)
    sold_stock = models.PositiveIntegerField(default=0)
    balance = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.date} - {self.phone}"


class Sale(models.Model):
    agent = models.ForeignKey(SalesAgent, on_delete=models.CASCADE)
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    sale_date = models.DateTimeField(default=timezone.now)

class Assignment(models.Model):
    agent = models.ForeignKey(SalesAgent, on_delete=models.CASCADE)
    date_assigned = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    previous_assignment = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reassigned_to'
    )

    def __str__(self):
        return f"Assignment for {self.agent.full_name} on {self.date_assigned}"


class AssignedPhone(models.Model):
    assignment = models.ForeignKey(Assignment, related_name='phones', on_delete=models.CASCADE)
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE)
    quantity_given = models.PositiveIntegerField()
    

    def __str__(self):
        return f"{self.quantity_given} x {self.phone.name} to {self.assignment.agent.full_name}"
