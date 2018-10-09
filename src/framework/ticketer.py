
from defs import *  # noqa

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class Ticketer():

    def __init__(self):
        self.tickets = {}

        self.scheduler = js_global.kernel.scheduler

        self.validate_memory()

    def add_ticket(self, type, requester, data=None):
        tid = self.gen_tid()

        ticket = {
            'type': type,
            'tick': Game.time,
            'requester': requester,
            'priority': self.scheduler.get_priority_of(requester),
            'tid': tid,
            'data': data,
            'completed': False,
            'result': {}
        }

        self.tickets[tid] = ticket

        return tid

    def get_ticket(self, tid):
        return self.tickets[tid]

    def get_highest_priority(self, type, city=None):
        highest_priority = 99
        highest_ticket = None
        for tid in Object.keys(self.tickets):
            ticket = self.tickets[tid]

            if ticket['type'] == type and ticket['priority'] < highest_priority \
                    and not ticket['completed'] and \
                    (city is None or ticket['data']['city'] == city):
                highest_ticket = ticket
                highest_priority = ticket['priority']

        return highest_ticket

    def get_tickets_by_type(self, type, city=None):
        tickets = []

        for tid in Object.keys(self.tickets):
            ticket = self.tickets[tid]
            if ticket['type'] == type and (city is None or ticket['data']['city'] == city):
                tickets.append(ticket)

        return tickets

    def clear_all_tickets(self):
        self.tickets = {}

    def delete_ticket(self, tid):
        del self.tickets[tid]

    def save_tickets(self):
        Memory.os.ticketer.tickets = self.tickets

    def load_tickets(self):
        self.tickets = Object.assign({}, Memory.os.ticketer.tickets)

    def gen_tid(self):
        self.memory.tid += 1
        return self.memory.tid

    def validate_memory(self):
        if _.isUndefined(Memory.os.ticketer):
            Memory.os.ticketer = {}

        if _.isUndefined(Memory.os.ticketer.tickets):
            Memory.os.ticketer.tickets = {}

        if _.isUndefined(Memory.os.ticketer.tid):
            Memory.os.ticketer.tid = 0

        self.memory = Memory.os.ticketer
