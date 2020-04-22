from functools import total_ordering
from abc import ABCMeta, abstractmethod
from inspect import getargspec
import heapq
import os
import json
import logging
import base64
import pickle


@total_ordering
class Module(metaclass=ABCMeta):
    def __init__(self, pipe=None):
        self.pipe_list = []
        self.task_list = []
        if isinstance(pipe, list):
            self.pipe_list = pipe[:]
        elif isinstance(pipe, Module):
            self.pipe_list.append(pipe)
        elif pipe is None:
            pass
        else:
            raise TypeError("Expected a List or Pipe type")

    def add_task(self, task):
        self.task_list.append(task)

    def register_pipe(self, pipe):
        if not isinstance(pipe, Pipe):
            raise TypeError("Expected a Pipe")
        else:
            self.pipe_list.append(pipe)

    def send_to_pipe(self, data=None):
        if data is None:
            for pipe in self.pipe_list:
                pipe.send(self.get_output())
        else:
            for pipe in self.pipe_list:
                pipe.send(data)

    def run(self):
        logging.info(self.__class__.__name__ + " run")
        # self.task_list = list(set(self.task_list))
        logging.info(
            self.__class__.__name__ + " tasklist len: " + str(len(self.task_list))
        )
        self.exec()
        logging.info(self.__class__.__name__ + " exec finish")
        try:
            data = self.get_output()
        except Exception as e:
            logging.error(self.__class__.__name__ + " " + str(e))
        else:
            self.update_database(data)
            logging.info(self.__class__.__name__ + " send to pipe")
            self.send_to_pipe(data)
        self.empty()
        # after module exec the tasklist should be empty
        self.task_list = []

    def __eq__(self, other):
        return len(self.task_list) == len(other.task_list)

    def __lt__(self, other):
        return len(self.task_list) > len(other.task_list)

    def empty(self):
        """method for cleaning"""
        pass

    @abstractmethod
    def exec(self):
        pass

    @abstractmethod
    def get_output(self):
        pass

    @abstractmethod
    def update_database(self, data):
        """data is the object that the get_output() return"""
        pass


class Pipe:
    def __init__(self, func=None, module=None):
        if func is not None:
            if not callable(func):
                raise TypeError("Expected a function")
            if len(getargspec(func).args) > 1:
                raise Exception("function should have only one parameter")
            self.process_data = func
        else:
            self.process_data = None
        self.module_list = []
        if isinstance(module, list):
            for m in module:
                self.register_module(m)
        elif isinstance(module, Module):
            self.register_module(module)
        elif module is None:
            pass
        else:
            raise TypeError("Expected a List or Module type")

    def send(self, data):
        if self.process_data is not None:
            data = self.process_data(data)
        for module in self.module_list:
            logging.debug("sending data to module " + module.__class__.__name__)
            if isinstance(data, list):
                for i in data:
                    module.add_task(i)
            else:
                module.add_task(data)

    def register_module(self, module):
        if not isinstance(module, Module):
            raise TypeError("Expected a Module")
        else:
            self.module_list.append(module)


class Controller:
    def __init__(self):
        self.module_list = []

    def push(self, module):
        heapq.heappush(self.module_list, module)
        logging.info("add module" + module.__class__.__name__)

    def save_state(self):
        controller_state = dict()
        for module in self.module_list:
            task_list_serialized = base64.b64encode(
                pickle.dumps(module.task_list)
            ).decode()
            controller_state[module.__class__.__name__] = task_list_serialized
        with open("controller_state.json", "w") as f:
            json.dump(controller_state, f)

    def resume_state(self):
        with open("controller_state.json", "r") as f:
            state = json.load(f)

        for module in state:
            for m in self.module_list:
                if m.__class__.__name__ == module:
                    tasklist = pickle.loads(base64.b64decode(state[module]))
                    for task in tasklist:
                        m.add_task(task)

    def run(self):
        heapq.heapify(self.module_list)
        while len(self.module_list[0].task_list) != 0:
            self.module_list[0].run()
            self.save_state()
            heapq.heapify(self.module_list)
        os.remove("controller_state.json")
