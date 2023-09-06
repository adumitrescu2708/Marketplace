"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021

Dumitrescu Alexandra - 333CA
"""
import time
from threading import Thread


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()

        Other than the given attributes we also extract from the kwargs the name of the
        producer that will later on be used to print the output message to stdout. For
        keeping track of the consumer's activity in the marketplace, a cart_id is assigned
        to it at the beginning of run method.
        """

        Thread.__init__(self)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.cart_id = -1
        self.name = kwargs['name']

    def run(self):
        """
        In the beginning the thread must obtain a cart_id from the marketplace.
        After this, the list of operations in being parsed and for each command
        add/remove methods from the marketplace are called. After all commands
        are executed, the consumer can place the order and after receiving the
        final list of products it uses the print method in the marketplace
        to print the output message to stdout.
        """
        self.cart_id = self.marketplace.new_cart()
        for order in self.carts:
            for operation in order:
                operation_type = operation['type']
                quantity = operation['quantity']
                product = operation['product']
                quantity_idx = 0
                while quantity_idx < quantity:
                    quantity_idx += 1
                    if operation_type == 'add':
                        while not self.marketplace.add_to_cart(self.cart_id, product):
                            time.sleep(self.retry_wait_time)
                    else:
                        self.marketplace.remove_from_cart(self.cart_id, product)

        for product in self.marketplace.place_order(self.cart_id):
            self.marketplace.print_info(self.name, product)
