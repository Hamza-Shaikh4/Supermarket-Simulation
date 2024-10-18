import random
import threading
import time

# Lists to separate customers depending on number of items
customers_regular = []
customers_self_service = []

# Global variables
id_generator = 0

# list to store extra customers when lists are full
extra_customers = []

# Record the start time for the simulation
start_time = time.time()

class Customer:
    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.num_items = random.randint(1, 30) # Randomly generate the number of items the customer has
        self.lottery_ticket = self.num_items >= 10 and random.choice([True, False]) # Randomly determine if the customer has a lottery ticket
        self.processing_time = self.calculate_processing_time()

    def calculate_processing_time(self):
        # Method to calculate processing time based on the number of items
        processing_time_per_item = 4 if self.num_items >= 10 else 6 # Regular checkout: 4 seconds per item, Self checkout: 6 seconds per item
        return self.num_items * processing_time_per_item

    def __str__(self):
        global id_generator
        if self.num_items > 10:
            # Categorize customers based on the number of items
            customers_regular.append(self.num_items)
        else:
            customers_self_service.append(self.num_items)
            # store customer ID
        id_generator += 1
        return f"Customer {id_generator}: {self.num_items} items, Lottery Ticket: {self.lottery_ticket}, Processing Time: {self.processing_time} seconds"
        # display customer information

class CustomerAdder:
    def __init__(self, num_customers):
        self.customers = [Customer(i) for i in range(1, num_customers + 1)]
        # create multiple customers depending on how many customers randomly generated
    def run_customer_adder(self):
        for customer in self.customers:
            print(customer)
            # display each customer

if __name__ == "__main__":
    num_customers = random.randint(1, 10)
    simulation = CustomerAdder(num_customers)
    simulation.run_customer_adder()

print()


class LaneManagement:
    # parent class for CheckOutLane and SelfServingLane

    def __init__(self, lane_type):
        self.lane_type = lane_type
        # initialise lane type as attribute

    def remove_customer(self):
        pass
    # method to be used in subclass as polymorphism

    def sim_customer(self):
        pass
    # method to be used in subclass as polymorphism

    def display_lane_status(self):
        pass
    # method to be used in subclass as polymorphism

    def process_checkout(self):
        pass
    # method to be used in subclass as polymorphism


class CheckoutLane(LaneManagement):
    def __init__(self, customer_queue):
        super().__init__("CheckOut Lane")
        self.customer_queue = customer_queue
        self.lane_list = []
        # lane_type attribute is now "CheckOut Lane" in this class
        # customer_queue attribute used to be input the example list into lane 1
        # a list to store the regular lanes

    def generate_queues(self):
        for x in range(5):
            self.lane_list.append([])
        self.lane_list[0] = self.customer_queue
        # method used to generate the 5 regular lanes as lists and put them into lane_list
        # sets the first lane equal to customers_less_than_10_items

    def add_customer(self):
        for i in range(len(self.lane_list)):
            while len(self.lane_list[i]) < 5 and len(extra_customers) > 0:
                self.lane_list[i].append(extra_customers.pop(0))
        #

    def remove_customer(self):
        for i in range(len(self.lane_list)):
            while len(self.lane_list[i]) > 5:
                self.lane_list[i].reverse()
                extra_customers.append(self.lane_list[i].pop(0))
                self.lane_list[i].reverse()

    def display_lane_status(self):
        for i in range(len(self.lane_list)):
            lane_index = i + 1
            if len(self.lane_list[i]) == 0:
                print(f" L{lane_index} - {self.lane_type}: Closed;")
            else:
                print(f" L{lane_index} - {self.lane_type}: {['*' for _ in range(len(self.lane_list[i]))]}; Customers = {len(self.lane_list[i])}")
                # displays the status of all the regular lanes

    def process_checkout(self):
        checkout_threads = []

        def process_single_lane(i):
            if len(self.lane_list[i]) > 0:
                time.sleep((self.lane_list[i][0] * 4))
                self.lane_list[i].pop(0)
                print(f"Regular Lane {i + 1} Customer Checked Out at: {round(time.time()-start_time)} seconds")
                print()

        for i in range(len(self.lane_list)):
            checkout_thread = threading.Thread(target=process_single_lane, args=(i,))
            checkout_threads.append(checkout_thread)

        for thread in checkout_threads:
            thread.start()

        for thread in checkout_threads:
            thread.join()

    def lane_saturation(self):
        if all(len(lane) == 5 for lane in self.lane_list):
            print("Regular Lane Saturation")


class SelfServiceLane(LaneManagement):
    def __init__(self, service_queue):
        super().__init__("Self-Service Lane")
        self.service_queue = service_queue
        # lane_type attribute is now "Self-Service Lane" in this class
        # service_queue is the queue for self-service lane

    def add_customer(self):
        if len(self.service_queue) < 15:
            extra_customers_copy = extra_customers.copy()
            for item in extra_customers_copy:
                if item < 10:
                    self.service_queue.append(item)
                    extra_customers.remove(item)
                    extra_customers_copy.remove(item)

    def remove_customer(self):
        while len(self.service_queue) > 15:
            self.service_queue.reverse()
            extra_customers.append(self.service_queue.pop())
            self.service_queue.reverse()

    def display_lane_status(self):
        if len(self.service_queue) == 0:
            print(f"L6 - {self.lane_type}: Closed;")
        else:
            print(f"L6 - {self.lane_type}: {['*' for i in range(len(self.service_queue))]}; Customers = {len(self.service_queue)}")
            # displays the status of the self-serving lane

    def process_checkout(self):
        while len(self.service_queue) > 0:
            time.sleep((self.service_queue[0])*6)
            self.service_queue.pop()
            print(f"Self-Service Lane Customer Checked Out at: {round(time.time() - start_time)} seconds")
            print()
            # carries out same method as process_checkout in the CheckoutLane class
            # no for loop however, as there is only 1 self-serving lane

    def lane_saturation(self):
        if len(self.service_queue) == 15:
            print("Self-Service Lane Saturation")


regularLanes = CheckoutLane(customer_queue=customers_regular)
selfServe = SelfServiceLane(service_queue=customers_self_service)
regularLanes.generate_queues()
print(f"Current time in seconds: {round(time.time()-start_time)}")
regularLanes.display_lane_status()
selfServe.display_lane_status()
print()

stop_sim = False


def run_simulation():
    global stop_sim
    time.sleep(2)
    while time.time() - start_time <= 120:
        print(f"Current time in Seconds: {round(time.time()-start_time)}")
        regularLanes.remove_customer()
        selfServe.remove_customer()
        selfServe.add_customer()
        regularLanes.add_customer()
        regularLanes.display_lane_status()
        selfServe.display_lane_status()
        print(f"Extra customers = {len(extra_customers)}")
        regularLanes.lane_saturation()
        selfServe.lane_saturation()
        print()
        time.sleep(2)
    stop_sim = True
    print()
    print("Simulation Finished")


def sim_customer():
    global stop_sim
    while time.time() - start_time <= 120:
        time.sleep(30)
        print()
        if __name__ == "__main__":
            new_simulation = CustomerAdder(random.randint(1, 10))
            new_simulation.run_customer_adder()
        print()
    breakpoint()


def sim_regular_checkout():
    global stop_sim
    while not stop_sim:
        regularLanes.process_checkout()
    breakpoint()


def sim_self_serve_checkout():
    global stop_sim
    while not stop_sim:
        selfServe.process_checkout()
    breakpoint()


iteration_thread = threading.Thread(target=run_simulation)
iteration_thread.start()
sim_customer_thread = threading.Thread(target=sim_customer)
sim_customer_thread.start()
sim_regular_checkout_thread = threading.Thread(target=sim_regular_checkout)
sim_regular_checkout_thread.start()
sim_self_serve_checkout_thread = threading.Thread(target=sim_self_serve_checkout)
sim_self_serve_checkout_thread.start()

iteration_thread.join()
sim_customer_thread.join()
sim_regular_checkout_thread.join()
sim_self_serve_checkout_thread.join()