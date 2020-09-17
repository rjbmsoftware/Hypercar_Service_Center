from django.views import View
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from collections import deque

oil_change = deque()
diagnostic = deque()
tyre_inflate = deque()


class ProcessingDetails:
    def __init__(self):
        self.customer_number = 1
        self.serving = 'Waiting for the next client'

    def pop(self) -> int or str:
        if oil_change:
            next_ticket = oil_change.popleft()
        elif tyre_inflate:
            next_ticket = tyre_inflate.popleft()
        elif diagnostic:
            next_ticket = tyre_inflate.popleft()
        else:
            next_ticket = 'Waiting for the next client'
        self.serving = next_ticket
        return next_ticket

    def next_ticket_number(self):
        current = self.customer_number
        self.customer_number += 1
        return current

    def add_job_to_queue(self, job_type: str) -> ():
        """
        add items to queue prioritised by time and type in order of importance
        descending
        1 oil change
        2 inflate tyres
        3 diagnostic
        """
        number = self.next_ticket_number()
        if job_type == 'change_oil':
            oil_change.append(number)
            return len(oil_change), (len(oil_change) - 1) * 2
        elif job_type == 'inflate_tires':
            queue_position = len(oil_change) + len(tyre_inflate)
            tyre_inflate.append(number)
            return queue_position,  len(oil_change) * 2 + (len(tyre_inflate) - 1) * 5
        else:
            queue_position = len(oil_change) + len(tyre_inflate) + len(diagnostic)
            diagnostic.append(number)
            time_taken = len(oil_change) * 2
            time_taken += len(tyre_inflate) * 5
            time_taken += (len(diagnostic) - 1) * 30
            return queue_position, time_taken


processing_details = ProcessingDetails()


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/homepage.html')


class ProcessingTickets(View):
    def get(self, request, *args, **kwargs):
        context = {
            'oil_change_queue_length': len(oil_change),
            'diagnostic_queue_length': len(diagnostic),
            'tyre_inflate_queue_length': len(tyre_inflate),
        }
        return render(request, 'tickets/processing.html', context=context)

    def post(self, request, *args, **kwargs):
        processing_details.pop()
        return redirect('/next')


class ServingCustomer(TemplateView):
    template_name = 'tickets/serving_customer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if processing_details.serving != 'Waiting for the next client':
            text = f'Next ticket #{processing_details.serving}'
        else:
            text = processing_details.serving
        context['next_ticket'] = text
        return context


class CustomerTicket(TemplateView):
    template_name = 'tickets/ticket.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        place_in_queue, wait_time = processing_details.add_job_to_queue(kwargs['ticket_type'])
        context['place_in_queue'] = place_in_queue
        context['ticket_type'] = kwargs['ticket_type']
        context['waiting_time'] = wait_time
        return context
