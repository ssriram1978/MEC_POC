from kafka import KafkaProducer
import os
import sys, traceback

sys.path.append("..")  # Adds higher directory to python modules path.
from log.log_file import logging_to_console_and_syslog
import time
from redisClient.redis_client import RedisClient


class RedisInterface:
    """
    This class does the following:
    """

    def __init__(self,thread_identifer=None):
        self.total_job_enqueued_count_redis_name = None
        self.total_job_dequeued_count_redis_name = None
        self.redis_log_keyname = None
        self.thread_identifer = thread_identifer
        self.read_environment_variables()
        self.redis_instance = RedisClient()

    def read_environment_variables(self):
        """
        This method is used to read the environment variables defined in the OS.
        :return:
        """
        while self.redis_log_keyname is None or \
                self.total_job_dequeued_count_redis_name is None:
            time.sleep(2)
            logging_to_console_and_syslog("RedisInterface:{} "
                                          "Trying to read the environment variables..."
                                          .format(self.thread_identifer))
            self.redis_log_keyname = os.getenv("redis_log_keyname_key",
                                               default=None)
            self.total_job_enqueued_count_redis_name = os.getenv("total_job_enqueued_count_redis_name_key",
                                                                 default=None)
            self.total_job_dequeued_count_redis_name = os.getenv("total_job_dequeued_count_redis_name_key",
                                                                 default=None)
        logging_to_console_and_syslog("RedisInterface:{} "
                                      "redis_log_keyname={}"
                                      .format(self.thread_identifer,
                                              self.redis_log_keyname))

        logging_to_console_and_syslog("RedisInterface:{} "
                                      "total_job_enqueued_count_redis_name={}"
                                      "total_job_dequeued_count_redis_name={}"
                                      .format(self.thread_identifer,
                                              self.total_job_enqueued_count_redis_name,
                                              self.total_job_dequeued_count_redis_name))

    def get_current_enqueue_count(self):
        logging_to_console_and_syslog("RedisInterface:{}."
                                      "total_job_enqueued_count={}"
                                      .format(self.thread_identifer,
                                              self.total_job_enqueued_count_redis_name))
        return self.redis_instance.read_key_value_from_redis_db(self.total_job_enqueued_count_redis_name)

    def get_current_dequeue_count(self):
        logging_to_console_and_syslog("RedisInterface:{}."
                                      "total_job_dequeued_count={}"
                                      .format(self.thread_identifer,
                                              self.total_job_dequeued_count_redis_name))
        return self.redis_instance.read_key_value_from_redis_db(self.total_job_dequeued_count_redis_name)

    def increment_enqueue_count(self):
        logging_to_console_and_syslog("RedisInterface:{}."
                                      "Incrementing total_job_enqueued_count={}"
                                      .format(self.thread_identifer,
                                              self.total_job_enqueued_count_redis_name))
        self.redis_instance.increment_key_in_redis_db(self.total_job_enqueued_count_redis_name)

    def increment_dequeue_count(self):
        logging_to_console_and_syslog("RedisInterface:{}."
                                      "Incrementing total_job_dequeued_count={}"
                                      .format(self.thread_identifer,
                                              self.total_job_dequeued_count_redis_name))
        self.redis_instance.increment_key_in_redis_db(self.total_job_dequeued_count_redis_name)

    def write_an_event_in_redis_db(self, event):
        logging_to_console_and_syslog("RedisInterface:{}."
                                      "Writing at key={}"
                                      "event={}"
                                      .format(self.thread_identifer,
                                              self.redis_log_keyname,
                                              event))
        self.redis_instance.write_an_event_on_redis_db(event, self.redis_log_keyname)

    def cleanup(self):
        pass
