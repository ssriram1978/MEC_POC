import os
import time
import sys
import traceback
import unittest
import subprocess
import threading

sys.path.append("..")  # Adds higher directory to python modules path.
from log.log_file import logging_to_console_and_syslog
from kafka_msgq_api import KafkaMsgQAPI

class TestProducerConsumer(unittest.TestCase):
    def setUp(self):
        os.environ["broker_name_key"] = "localhost:9094"
        os.environ["topic_key"] = "video-file-name"
        os.environ["redis_log_keyname_key"] = "briefcam"
        os.environ["total_job_enqueued_count_redis_name_key"] = "enqueue"
        os.environ["total_job_dequeued_count_redis_name_key"] = "dequeue"
        os.environ["redis_server_hostname_key"] = "localhost"
        os.environ["redis_server_port_key"] = "6379"
        self.max_consumer_threads = 10
        self.create_test_docker_container()
        self.producer_instance = KafkaMsgQAPI(isProducer=True)
        self.consumer_threads = None
        self.create_consumer_threads()

    @staticmethod
    def run_consumer_instance():
        logging_to_console_and_syslog("Starting {}".format(threading.current_thread().getName()))
        consumer_instance = KafkaMsgQAPI(isConsumer=True,
                                         thread_identifier=threading.current_thread().getName())
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            consumer_instance.dequeue()
        logging_to_console_and_syslog("Exiting {}".format(threading.current_thread().getName()))

    def create_consumer_threads(self):
        self.consumer_threads = [0] * self.max_consumer_threads
        for index in range(self.max_consumer_threads):
            self.consumer_threads[index] = threading.Thread(name="{}{}".format("thread", index),
                                                            target=TestProducerConsumer.run_consumer_instance)
            self.consumer_threads[index].do_run = True
            self.consumer_threads[index].start()

    def test_run(self):
        logging_to_console_and_syslog("Validating producer instance to be not null.")
        self.assertIsNotNone(self.producer_instance)

        logging_to_console_and_syslog("Validating consumer threads to be not null.")
        for index in range(self.max_consumer_threads):
            self.assertIsNotNone(self.consumer_threads[index])

        time.sleep(20)

        logging_to_console_and_syslog("Posting messages.")
        self.assertTrue(self.post_messages())

        time.sleep(60)

        logging_to_console_and_syslog("Validating if the consumer successfully dequeued messages.")
        consumer_instance = KafkaMsgQAPI(isConsumer=True,
                                         thread_identifier="X")
        self.assertEqual(self.producer_instance.get_current_enqueue_count(),
                         consumer_instance.get_current_dequeue_count())

    def post_messages(self):
        messages = [str(x) for x in range(10)]
        for message in messages:
            self.producer_instance.enqueue(message)
        return True

    def create_test_docker_container(self):
        completedProcess = subprocess.run(["docker-compose",
                                           "-f",
                                           "docker-compose_wurstmeister_kafka.yml",
                                           "up",
                                           "-d"],
                                          stdout=subprocess.PIPE)
        self.assertIsNotNone(completedProcess)
        self.assertIsNotNone(completedProcess.stdout)
        # time.sleep(120)

    def delete_test_docker_container(self):
        completedProcess = subprocess.run(["docker-compose",
                                           "-f",
                                           "docker-compose_wurstmeister_kafka.yml",
                                           "down"],
                                          stdout=subprocess.PIPE)
        self.assertIsNotNone(completedProcess)
        self.assertIsNotNone(completedProcess.stdout)

    def tearDown(self):
        self.producer_instance.cleanup()
        self.delete_test_docker_container()
        time.sleep(5)
        for index in range(self.max_consumer_threads):
            self.consumer_threads[index].do_run = False
            time.sleep(1)
            self.consumer_threads[index].join(1.0)
            if self.consumer_threads[index].is_alive():
                try:
                    self.consumer_threads[index]._stop()

                except:
                    logging_to_console_and_syslog("Caught an exception while stopping thread {}"
                                                  .format(self.consumer_threads[index].getName()))

if __name__ == "__main__":
    unittest.main()