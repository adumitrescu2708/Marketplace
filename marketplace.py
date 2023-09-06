"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2023

Dumitrescu Alexandra - 333CA
"""

import time
import unittest
from threading import Lock
import logging
from logging.handlers import RotatingFileHandler


class TestMarketplace(unittest.TestCase):
    """
    Class that tests main methods in marketplace class
    """

    def setUp(self):
        self.marketplace = Marketplace(3)

    def test_register_producer(self):
        """
        This test checks the ids of first 3 producers and whether they were
        added in the dictionary that maps the producers with its corresponding
        number of published products that are available for sale in marketplace.
        """

        first_producer_id = self.marketplace.register_producer()
        self.assertEqual(first_producer_id, str(1))

        second_producer_id = self.marketplace.register_producer()
        self.assertEqual(second_producer_id, str(2))

        third_producer_id = self.marketplace.register_producer()
        self.assertEqual(third_producer_id, str(3))

        self.assertEqual(self.marketplace.products_of_producer[first_producer_id], 0)
        self.assertEqual(self.marketplace.products_of_producer[second_producer_id], 0)
        self.assertEqual(self.marketplace.products_of_producer[third_producer_id], 0)

    def test_publish(self):
        """
        This test checks the publish method and treats the following cases:
        (A) The producer publishes items in the requested limit. Each element in the
            shared buffer is maintained in the list with its corresponding publisher's
            id, cart's id and a Lock. We check for each publish action the accuracy of the data
            introduced in the buffer.
        (B) The same producer tries to publish more items than allowed. Once a publisher
            published more than the queue_size_per_producer parameter products, he has to
            wait and retry the action. In this case, the method fails and no item is added.
            Therefore, we check the length of the buffer to remain the same.
        (C) The method was called with an invalid producer id.
        """

        publisher_id = self.marketplace.register_producer()

        # (A)
        published_product = "Green Tea"
        self.assertTrue(self.marketplace.publish(publisher_id, published_product))

        self.assertEqual(self.marketplace.buffer[0][0], published_product)
        self.assertEqual(self.marketplace.buffer[0][1], publisher_id)
        self.assertEqual(self.marketplace.buffer[0][2], -1)

        published_product = "Americano Coffee"
        self.assertTrue(self.marketplace.publish(publisher_id, published_product))

        self.assertEqual(self.marketplace.buffer[1][0], published_product)
        self.assertEqual(self.marketplace.buffer[1][1], publisher_id)
        self.assertEqual(self.marketplace.buffer[1][2], -1)

        published_product = "Capuccino"
        self.assertTrue(self.marketplace.publish(publisher_id, published_product))

        self.assertEqual(self.marketplace.buffer[2][0], published_product)
        self.assertEqual(self.marketplace.buffer[2][1], publisher_id)
        self.assertEqual(self.marketplace.buffer[2][2], -1)

        # (B)
        published_product = "Infusion Tea"
        self.assertEqual(len(self.marketplace.buffer), 3)
        self.assertFalse(self.marketplace.publish(publisher_id, published_product))

        # (C)
        self.assertFalse(self.marketplace.publish("2", published_product))

    def test_new_cart(self):
        """
        This test checks the ids of the first 3 carts in the marketplace.
        """
        first_cart = 1
        self.assertEqual(first_cart, self.marketplace.new_cart())

        second_cart = 2
        self.assertEqual(second_cart, self.marketplace.new_cart())

        third_cart = 3
        self.assertEqual(third_cart, self.marketplace.new_cart())

    def test_print_info(self):
        """
        This test checks the printing method.
        """
        producer = 'producer_name'
        product = 'product_name'
        output = self.marketplace.print_info(producer, product)
        expected_output = producer + " bought " + product
        self.assertEqual(output, expected_output)

    def test_add_to_cart(self):
        """
        This test checks the following cases:
        (A) The product from the buffer is marked as being not available,
            since it was added to one of the consumer's cart. In this case,
            we also check the accuracy of the data inserted in the cart.
        (B) The given cart's id is an invalid one.
        (C) The product could not be found in the buffer. In this case, no item is
            added in the given cart.
        (D) The product was already taken by another consumer. In this case, no item is
            added in the given cart.
        """

        first_cart = self.marketplace.new_cart()
        second_cart = self.marketplace.new_cart()

        publisher = self.marketplace.register_producer()

        added_item = "Green Tea"

        # (B)
        self.assertFalse(self.marketplace.add_to_cart(-1, added_item))
        # (C)
        self.assertFalse(self.marketplace.add_to_cart(first_cart, added_item))
        self.assertListEqual(self.marketplace.carts[first_cart], [])
        # (A)
        self.marketplace.publish(publisher, added_item)
        self.assertTrue(self.marketplace.add_to_cart(first_cart, added_item))

        self.assertEqual(self.marketplace.carts[first_cart][0][0], added_item)
        self.assertEqual(self.marketplace.carts[first_cart][0][1], publisher)
        self.assertEqual(self.marketplace.carts[first_cart][0][2], first_cart)
        # (D)
        self.assertFalse(self.marketplace.add_to_cart(second_cart, added_item))
        self.assertEqual(self.marketplace.carts[second_cart], [])

    def test_remove_from_cart(self):
        """
        In this test we first publish an item, then we add it to one consumer's cart,
        and then we remove it.
        (A) Check whether the item was removed from the consumer's cart.
        (B) Check whether the item was marked as being available again in the shared buffer.
        """
        cart = self.marketplace.new_cart()
        publisher = self.marketplace.register_producer()

        added_item = "Green Tea"

        self.marketplace.publish(publisher, added_item)
        self.marketplace.add_to_cart(cart, added_item)
        self.marketplace.remove_from_cart(cart, added_item)

        # (A)
        self.assertEqual(self.marketplace.carts[cart].count([added_item, publisher, cart]), 0)

        # (B)
        for item in self.marketplace.buffer:
            if item[0] == added_item:
                self.assertEqual(item[2], -1)

    def test_place_order(self):
        """
        In this test 2 items are published and then added to one consumer's cart.
        The following cases are covered:
        (A) The place order command is properly placed, in which case we check the accuracy
            of the returned list of elements.
        (B) The method was called on an invalid cart id.
        """
        cart = self.marketplace.new_cart()
        publisher = self.marketplace.register_producer()

        first_item = "Green Tea"
        second_item = "Americano Coffee"
        self.marketplace.publish(publisher, first_item)
        self.marketplace.publish(publisher, second_item)

        self.marketplace.add_to_cart(cart, first_item)
        self.marketplace.add_to_cart(cart, second_item)
        # (A)
        self.assertListEqual(self.marketplace.place_order(cart),
                             [first_item, second_item])
        # (B)
        self.assertEqual(self.marketplace.place_order(-1), [])


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer

        In the constructor the logger, formatter and handler are set.
        The counters for producers and consumers are initialised to 0.
        The shared buffer and the dictionaries are initialised.
        """

        self.queue_size_per_producer = queue_size_per_producer

        self.number_of_producers = 0
        self.number_of_consumers = 0

        self.logger = logging.getLogger('marketplace_logger')
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler("marketplace.log", mode='w')
        self.logger.addHandler(handler)
        formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(message)s')
        formatter.converter = time.gmtime
        handler.setFormatter(formatter)

        self.buffer = []
        self.carts = {}
        self.products_of_producer = {}

        self.lock_print = Lock()
        self.lock_counter_producers = Lock()
        self.lock_counter_consumers = Lock()

    def print_info(self, name, product):
        """
        Printer

        :type name: Int
        :param name: The name of the consumer that placed an order
        :type product: Product
        :param product: The product in the cart that was purchased

        Returns the output message printed to stdout.
        """
        with self.lock_print:
            print(name + " bought " + str(product))

        output_message = name + " bought " + str(product)
        return output_message

    def register_producer(self):
        """
        Register Producer

        Returns an id for the producer that calls this. (A)
        Increments the number of producers in the marketplace and initialises
        the number of published products of the producers to 0. (B)

        (A) The id of a newly added producer is equal to str(index of the producer)
            First producer => str(1)
            Second producer => str(2) etc.
        (B) We store in a dictionary the number of available products published by
            the producer in order to check the limit to queue_size_per_producer
            products_of_producer[producer_id] = X, meaning producer_id has X products available
        """
        self.logger.info(" was called.")

        with self.lock_counter_producers:
            self.number_of_producers += 1
            id_producer = str(self.number_of_producers)
        self.products_of_producer[id_producer] = 0

        self.logger.info(" returned %s.", id_producer)
        return id_producer

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.

        In order to check whether a publisher must wait and retry, we check the dictionary
        products_od_producer, where we keep track for every producer in the marketplace
        its corresponding number of available items. When someone publishes in the marketplace,
        we increment this counter and add the item, along with some more data, at the end of
        the shared buffer.

        For each item we add:
            (item, producer_id, cart_id/AVAILABLE, Lock)
            @ item - used for searching in remove/add to cart operations
            @ producer_id - multiple producers can produce the same product, therefore
                            we need to keep track of the author
            @ cart_id/AVAILABLE - used to track whether the product is available for sale
                                or not, and to help in deleting the item after an
                                order is placed.
            @ Lock - when modifying the availability state of a product, we do not want
                     to block entire list (e.g. The other consumers should be free to
                     modify other products, therefor we associate for each product one lock)
        """

        self.logger.info(" was called with parameters: producer_id=%s, product=%s."
                         , producer_id, str(product))

        if self.products_of_producer.get(producer_id) is None:
            self.logger.error("invalid producer id %s!", producer_id)
            return False

        if self.products_of_producer[producer_id] == self.queue_size_per_producer:
            self.logger.info(" returned False.")
            return False

        self.buffer.append([product, producer_id, -1, Lock()])
        self.products_of_producer[producer_id] += 1
        self.logger.info(" returned True.")
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id

        When a cart is added in the marketplace, in order to keep track
        of the elements added/removed we associate for each cart a list, that
        will be returned when placing the order.
        The cart_id is the index in the added consumers:
        first cart => cart_id = 1
        second cart => cart_id = 2 etc.
        """
        self.logger.info(" was called.")
        with self.lock_counter_consumers:
            self.number_of_consumers += 1
            id_cart = self.number_of_consumers
            self.carts[id_cart] = []

        self.logger.info(" returned %s.", str(id_cart))
        return id_cart

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again

        When searching for an item to add in the cart, we first search in the shared
        buffer for an item of the given type that is also available, then using its lock
        we modify its state and add it in the corresponding cart while also marking it
        as being unavailable.
        """

        self.logger.info(" was called with parameters: cart_id= %s, product=%s."
                         , str(cart_id), str(product))

        if cart_id > self.number_of_consumers or cart_id < 0:
            self.logger.error("invalid cart id %s!", str(cart_id))
            return False

        length = 0
        for exposed_product in self.buffer:
            if exposed_product[0] == product and exposed_product[2] == -1:
                # multiple consumers might want to modify this object, but only one can have it.
                exposed_product[3].acquire()
                if exposed_product[2] == -1:
                    # if the object remained available (meaning the consumer is the first one to
                    # get it, it modifies it, otherwise keep searching for other one)
                    self.buffer[length][2] = cart_id
                    self.carts[cart_id].append([self.buffer[length][0],
                                                self.buffer[length][1],
                                                self.buffer[length][2]])
                    exposed_product[3].release()
                    self.logger.info(" returned True.")
                    return True
                exposed_product[3].release()
            length += 1
        self.logger.info(" returned False.")
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart

        This method modifies the state of the product in the shared buffer and
        removes the element from its cart.
        """

        self.logger.info(" was called with parameters: cart_id= %s, product=%s.",
                         str(cart_id), str(product))

        if cart_id > self.number_of_consumers or cart_id < 0:
            self.logger.error("invalid cart id %s!", str(cart_id))
            return

        to_add = -1
        for product_info in self.carts[cart_id]:
            if product_info[0] == product:
                self.carts[cart_id].remove(product_info)
                to_add = product_info
                break
        for exposed_product in self.buffer:
            if exposed_product[0] == to_add[0] \
                    and exposed_product[1] == to_add[1] \
                    and exposed_product[2] == to_add[2]:
                with exposed_product[3]:
                    exposed_product[2] = -1
                break

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart

        This method removes all elements in the cart from the shared buffer and
        decrements the number of available products of the corresponding publisher in
        products_of_producer dictionary
        """

        self.logger.info(" was called with parameters: cart_id=%s.", str(cart_id))

        if cart_id > self.number_of_consumers or cart_id < 0:
            self.logger.error("invalid cart id %s!", str(cart_id))
            return []

        for product in self.carts[cart_id]:
            for exposed_elem in self.buffer:
                if exposed_elem[0] == product[0] \
                        and exposed_elem[1] == product[1] \
                        and exposed_elem[2] == product[2]:
                    self.buffer.remove(exposed_elem)
                    break

            self.products_of_producer[product[1]] -= 1

        products_cart = []
        for product in self.carts[cart_id]:
            products_cart.append(product[0])

        self.logger.info(" returned %s.", str(products_cart))
        return products_cart
