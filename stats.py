#!/usr/bin/env python
# -*- coding: utf-8 -*-

from catenae import Link, Electron
from threading import Lock


class Stats(Link):

    MEASURE_INTERVAL = 5

    def setup(self):
        self.measure_lock = Lock()

        self.total_posts_counter = 0
        self.current_posts_counter = 0
        self.max_posts_counter = 0

        self.elapsed_windows = 0
        self.metrics = {
            'avg_posts_per_second': 0,
            'current_posts_per_second': 0,
            'max_posts_per_second': 0
        }

        self.loop(self.take_measure, interval=Stats.MEASURE_INTERVAL)
        self.loop(self.show_stats, interval=Stats.MEASURE_INTERVAL - 1)

    def take_measure(self):
        self.measure_lock.acquire()
        self.elapsed_windows += 1

        self.metrics['avg_posts_per_second'] = self.total_posts_counter / (Stats.MEASURE_INTERVAL *
                                                                           self.elapsed_windows)
        self.metrics[
            'current_posts_per_second'] = self.current_posts_counter / Stats.MEASURE_INTERVAL
        if self.metrics[
                'current_posts_per_second'] > self.max_posts_counter and self.elapsed_windows > 3:
            self.max_posts_counter = self.metrics['current_posts_per_second']
        self.metrics['max_posts_per_second'] = self.max_posts_counter
        self.current_posts_counter = 0

        self.measure_lock.release()

    def show_stats(self):
        self.logger.log()
        self.logger.log('=== STATS ===')
        self.logger.log(f"AVG posts/s: {self.metrics['avg_posts_per_second']}")
        self.logger.log(f"CUR posts/s: {self.metrics['current_posts_per_second']}")
        self.logger.log(f"MAX posts/s: {self.metrics['max_posts_per_second']}")
        self.logger.log('=============\n')

    def countable_post(self, electron):
        if electron.previous_topic == 'submission_ids' or electron.value['type'] == 1:
            return True
        return False

    def transform(self, electron):
        self.measure_lock.acquire()
        if self.countable_post(electron):
            self.total_posts_counter += 1
            self.current_posts_counter += 1
        self.measure_lock.release()


if __name__ == "__main__":
    Stats().start()
