"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021

Dumitrescu Alexandra - 333CA
"""

from threading import Thread
import time


class Producer(Thread):
    """
    Class that represents a producer.
    """
    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()

        Other than the given attributes, we use a producer_id to keep track of the
        activity of the producer in the marketplace.
        """
        Thread.__init__(self, daemon=True)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.producer_id = 0

    def run(self):
        """
        In this method, a thread parses the given list of products and using
        methods from marketplace, it tries to continuously publish elements.
        If the publish method in the marketplace returns False, the calling
        thread must wait republish_wait_time and try again. After publishing
        each product, the thread must wait a default time specified in the
        list of products.
        """
        while True:
            self.producer_id = self.marketplace.register_producer()
            for product_info in self.products:
                product = product_info[0]
                quantity = product_info[1]
                wait_time = product_info[2]
                publication_id = 0
                while publication_id < quantity:
                    publication_id += 1
                    while not self.marketplace.publish(self.producer_id, product):
                        time.sleep(self.republish_wait_time)
                    time.sleep(wait_time)
