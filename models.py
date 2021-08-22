import threading
from typing import Dict, List, Optional

from pydantic import BaseModel

from limits import KEY_MAXIMUM_LENGTH, VALUE_MAXIMUM_LENGTH


class Task(BaseModel):
    completed: Optional[bool]


class User(BaseModel):
    username: str
    password: Optional[str]
    credits: int

    class MaximumLengthKey(Exception):
        pass

    class MaximumLengthValue(Exception):
        pass

    class DoesNotExist(Exception):
        pass

    class UsernameAlreadyExists(Exception):
        pass

    class NoMoreCredits(Exception):
        pass

    def add_task(self, task):
        Store().add_tasks(self.username, task)

    def get_tasks(self):
        return Store().get_tasks(username=self.username)


class Store:
    _instance = None
    _lock = threading.Lock()
    _user_lock = threading.Lock()
    _users = dict()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Store, cls).__new__(cls)
        return cls._instance

    def get_number_of_objects(self) -> Dict:
        with self._user_lock:
            nb_of_users = len(self.get_users())
            nb_of_objects = nb_of_users + sum([len(u[1]) for u in Store().get_users().values()])
            return {"nb_of_users": nb_of_users, "nb_of_objects": nb_of_objects}

    def get_users(self) -> Dict:
        return self._users

    def get_user(self, username) -> User:
        try:
            return self._users[username][0]
        except KeyError:
            raise User.DoesNotExist

    def delete_user(self, username):
        try:
            del self._users[username]
        except KeyError:
            return User.DoesNotExist

    def add_user(self, user: User):
        if len(user.username) > KEY_MAXIMUM_LENGTH:
            raise User.MaximumLengthKey
        with self._user_lock:
            if user.username in self._users.keys():
                raise User.UsernameAlreadyExists
            else:
                self._users[user.username] = [user, []]

    def get_tasks(self, username):
        try:
            return self._users[username][1]
        except KeyError:
            raise User.DoesNotExist

    def add_tasks(self, username, task: Task):
        try:
            with self._user_lock:

                user = self._users[username][0]
                tasks = self._users[username][1]

                if user.credits == len(tasks):
                    raise User.NoMoreCredits

                if user.credits == VALUE_MAXIMUM_LENGTH:
                    raise User.MaximumLengthValue

                tasks = self._users[username][1]
                tasks.append(task)
        except KeyError:
            raise User.DoesNotExist

    def delete_task(self, id_task):
        pass
