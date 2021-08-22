import random
import string

from fastapi.testclient import TestClient

from limits import KEY_MAXIMUM_LENGTH
from main import Store
from main import app
from models import User

client = TestClient(app)

TEST_USER_INFOS_1 = {
    "username": "raphael",
    "password": "raphael",
    "credits": 1
}

TEST_USER_INFOS_2 = {
    "username": "bar",
    "password": "bar",
    "credits": 10
}

TEST_TOP_TEN_USERS = [
    ["u1", "u1", 10, 1],
    ["u2", "u1", 10, 2],
    ["u3", "u1", 10, 3],
    ["u4", "u1", 10, 4],
    ["u5", "u1", 10, 5],
    ["u6", "u1", 10, 6],
    ["u7", "u1", 10, 7],
    ["u8", "u1", 10, 8],
    ["u9", "u1", 10, 9],
    ["u10", "u1", 10, 10],
    ["u11", "u1", 11, 11],
]


def test_create_user():
    """
    Test user creation and unicity of username
    :return:
    """
    response = client.post("/users", json=TEST_USER_INFOS_1, headers={"X-Token": "super_admin"})

    assert response.status_code == 200
    try:
        Store.get_user("raphael")
    except User.DoesNotExist:
        assert False
    response = client.post("/users", json=TEST_USER_INFOS_1, headers={"X-Token": "super_admin"})
    assert response.status_code == 400
    assert response.json() == {"msg": "already_exists"}


def test_get_user():
    response = client.get(f"/users/{TEST_USER_INFOS_1['username']}", json=TEST_USER_INFOS_1,
                          headers={"X-Token": "super_admin"})
    assert response.status_code == 200
    assert response.json() == TEST_USER_INFOS_1


def test_modify_user():
    response = client.patch(f"/users/{TEST_USER_INFOS_1['username']}", json={"username": "RAPHAEL", "credits": 100},
                            headers={"X-Token": "super_admin"})
    assert response.status_code == 200


def test_delete_user():
    """
    Test delete user
    :return:
    """

    username = "raphael"
    response = client.delete(f"/users/{username}", headers={"X-Token": "super_admin"})
    assert response.status_code == 200
    try:
        Store.get_user("raphael")
    except User.DoesNotExist:
        assert True
    else:
        assert False


def test_create_user_with_long_username():
    username = ''.join(random.choice(string.ascii_letters) for i in range(KEY_MAXIMUM_LENGTH + 1))
    response = client.post("/users", json={"username": username,
                                           "password": username,
                                           "credits": 10},
                           headers={"X-Token": "super_admin"})
    assert response.status_code == 400
    assert response.json() == {'msg': 'length of username is higher than max length'}


def add_task(username, json):
    return client.post("/tasks", headers={"X-Token": f"{username}"}, json=json)


def test_add_tasks_and_credits_exhausted():
    client.post("/users", json=TEST_USER_INFOS_2, headers={"X-Token": "super_admin"})
    nb_credits = TEST_USER_INFOS_2["credits"]
    for i in range(0, nb_credits):
        response = add_task(TEST_USER_INFOS_2["username"], json={"completed": True})
        assert response.status_code == 200
    response = add_task(TEST_USER_INFOS_2["username"], json={"completed": True})
    assert response.status_code == 400
    assert response.json() == {"msg": "Credits Exhausted"}


def test_global_metrics():
    response = client.get("/global_metrics")
    assert response.status_code == 403
    response = client.get("/global_metrics", headers={"X-Token": "super_admin"})
    assert response.status_code == 200
    assert response.json() == {'nb_of_objects': TEST_USER_INFOS_2["credits"] + 1, 'nb_of_users': 1}


def test_my_metrics():
    response = client.get("/metrics/bar")
    assert response.status_code == 403
    response = client.get("/metrics/me", headers={"X-Token": "bar"})
    assert response.status_code == 200
    assert response.json() == {'credits': 10, 'remaining_credits': 0}


def test_get_metrics_for_user_as_admin():
    response = client.get("/metrics/bar")
    assert response.status_code == 403
    response = client.get("/metrics/bar", headers={"X-Token": "super_admin"})
    assert response.status_code == 200
    assert response.json() == {'credits': 10, 'remaining_credits': 0}


def test_top_ten_metrics():
    def generate_test_case():
        for user in TEST_TOP_TEN_USERS:
            client.post("/users", json={"username": user[0],
                                        "password": user[1],
                                        "credits": user[2]}, headers={"X-Token": "super_admin"})
            for i in range(0, user[3]):
                add_task(user[0], json={"completed": True})

    generate_test_case()

    response = client.get("/top_metrics")
    assert response.status_code == 403
    response = client.get("/top_metrics", headers={"X-Token": "super_admin"})
    assert response.status_code == 200
    assert response.json() == ['u11', 'bar', 'u10', 'u9', 'u8', 'u7', 'u6', 'u5', 'u4', 'u3']
