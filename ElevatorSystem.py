import heapq

FLOOR_NONE = -1
WAITING_RATIO = 3


class Customer(object):
    def __init__(self, pickup_floor, destination, boarding_time):
        self.pickup_floor = pickup_floor
        self.destination = destination
        self.boarding_time = boarding_time


class Elevator(object):
    def __init__(self, id, capacity, initial_floor, controller):
        self.id = id
        # customers for all floors, stored as a map containing many lists
        self.customers = {}
        self.destination = FLOOR_NONE
        self.current_floor = initial_floor
        self.capacity = capacity
        self.customer_count = 0
        self.controller = controller

    ##
    # return whether the elevator participate pickup
    def participate_pickup(self, pickup_destination):
        return self.destination == FLOOR_NONE or (
            (pickup_destination - self.current_floor) * (
                pickup_destination - self.destination) <= 0 and self.customer_count < self.capacity)

    def is_empty(self):
        return self.customer_count == 0

    def add_customer(self, customer):
        print "[%d] pickup customer at floor %d his destination %d " % (self.id, self.current_floor, customer.destination)
        destination = customer.destination
        if destination in self.customers:
            self.customers[destination].append(customer)
        else:
            self.customers[destination] = [customer]
        self.customer_count += 1

    # drop customers at that floor
    def release_customers(self):
        if self.current_floor in self.customers:
            released_count = len(self.customers[self.current_floor])
            if released_count > 0:
                self.customer_count -= released_count
                self.customers[self.current_floor] = []
                print "[%d] release customer at floor %d " % (self.id, self.current_floor)
        # if empty, set the state to idle
        if self.customer_count <= 0 and self.current_floor == self.destination:
            self.destination = FLOOR_NONE
        self.controller.update(self.id, self.current_floor, self.destination, self.customer_count)

    def move_step(self):
        if self.destination == FLOOR_NONE:
            return
        if self.destination > self.current_floor:
            self.current_floor += 1
        else:
            self.current_floor -= 1
        self.controller.update(self.id, self.current_floor, self.destination, self.customer_count)

    def find_next_destination(self):
        # the major logic is rank all destinations according to the formula:
        # val = distance_to_destination + ratio / waiting_time
        def func_compare(customer):
            val = abs(self.current_floor - customer.destination) + WAITING_RATIO / (
                self.controller.time_counter - customer.boarding_time + 1)
            return -val

        h = []
        for key, value in self.customers.iteritems():
            if value is not None and len(value) > 0:
                for customer in value:
                    heapq.heappush(h, (func_compare(customer), customer))
        if len(h) > 0:
            customer = heapq.heappop(h)[1]
            self.destination = customer.destination
            self.controller.update(self.id, self.current_floor, self.destination, self.customer_count)


class ElevatorController(object):
    def __init__(self, num_elevator, capacity):
        # these passengers who are waiting
        # stored as a map containing many lists
        self.waiting_passenger = {}
        # all elevators
        self.elevators = []
        self.status = []
        self.time_counter = 0
        self.waiting_count = 0
        self.active_elevator = 0
        for x in range(0, num_elevator):
            # set the initial floor to 0, which matches real case
            elevator = Elevator(x, capacity, 0, self)
            self.elevators.append(elevator)
            self.status.append((x, elevator.current_floor, elevator.destination, elevator.customer_count))

    ##
    # return the status of all elevators,
    # it contains status of all elevator as an array,
    # for each element in that array, it's a 3-length array,
    # containing [elevator_id, current_floor, destination_floor]
    def query_status(self):
        return self.status

    def update(self, elevator_id, current_floor, destination, customer_count):
        self.status[elevator_id] = (elevator_id, current_floor, destination, customer_count)

    def pickup(self, floor, destination):
        customer = Customer(floor, destination, self.time_counter)

        self.append_to_waiting(customer)

    def step(self):
        self.time_counter += 1
        active_count = 0
        for elevator in self.elevators:
            if elevator.current_floor == elevator.destination:
                # two kinds of elevators execute this
                # 1. occupied elevator going to release a customer
                # 2. empty elevator going to pickup a customer;

                # release all possible customers heading towards that floor
                elevator.release_customers()

                # elevators that reach the destination
                # pickup possible customers on that floor
                waiting_customers = self.get_waiting_customers_by_floor(elevator.current_floor)

                while elevator.customer_count < elevator.capacity and len(waiting_customers) > 0:
                    customer = waiting_customers.pop()
                    self.waiting_count -= 1
                    elevator.add_customer(customer)

                # if there is still customers inside, decide the next destination
                if not elevator.is_empty():
                    elevator.find_next_destination()
                    elevator.move_step()

            elif elevator.destination != FLOOR_NONE:
                # ongoing elevators
                # it has three missions
                # 1. heading towards the destination
                # 2. release customer on that floor if possible
                # 3. pickup customers on that floor if necessary

                # release possible customers
                elevator.release_customers()

                # pickup possible customers
                waiting_customers = self.get_waiting_customers_by_floor(elevator.current_floor)

                while len(elevator.customers) < elevator.capacity and len(waiting_customers) > 0:
                    customer = waiting_customers.pop()
                    self.waiting_count -= 1
                    elevator.add_customer(customer)

                # move towards the destination
                elevator.move_step()
            else:
                # for empty elevator, if there is unsettled customer, go to pick it up
                if self.waiting_count > 0:
                    for key, value in self.waiting_passenger.iteritems():
                        if len(value) > 0:
                            # heading towards the unsettled
                            elevator.destination = value[0].pickup_floor
                            self.update(elevator.id, elevator.current_floor, elevator.destination,
                                        elevator.customer_count)
                            break
                    elevator.move_step()

            if elevator.destination != FLOOR_NONE:
                active_count += 1
        self.active_elevator = active_count

    def append_to_waiting(self, customer):
        floor = customer.pickup_floor
        if floor in self.waiting_passenger:
            self.waiting_passenger[floor].append(customer)
        else:
            self.waiting_passenger[floor] = [customer]
        self.waiting_count += 1

    def get_waiting_customers_by_floor(self, floor):
        if floor in self.waiting_passenger:
            return self.waiting_passenger[floor]
        else:
            return []

