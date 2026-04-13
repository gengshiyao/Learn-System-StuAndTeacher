import time

import requests


BASE_URL = "http://127.0.0.1:5000/api"


def run():
    username = f"student_{int(time.time())}"
    password = "pass123"

    resp = requests.post(f"{BASE_URL}/auth/register", json={"username": username, "password": password})
    resp.raise_for_status()

    resp = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
    resp.raise_for_status()
    token = resp.json()["data"]["token"]

    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(f"{BASE_URL}/courses", headers=headers)
    resp.raise_for_status()
    courses = resp.json()["data"]
    course_id = courses[0]["id"]

    resp = requests.get(f"{BASE_URL}/kps", params={"course_id": course_id}, headers=headers)
    resp.raise_for_status()
    kps = resp.json()["data"]
    kp_id = kps[0]["id"]

    resp = requests.get(f"{BASE_URL}/resources", params={"kp_id": kp_id}, headers=headers)
    resp.raise_for_status()
    resources = resp.json()["data"]
    resource_id = resources[0]["id"]

    resp = requests.post(
        f"{BASE_URL}/learning_events",
        json={
            "kp_id": kp_id,
            "resource_id": resource_id,
            "event_type": "complete_exercise",
            "duration_sec": 600,
        },
        headers=headers,
    )
    resp.raise_for_status()

    resp = requests.get(f"{BASE_URL}/assessments", params={"kp_id": kp_id}, headers=headers)
    resp.raise_for_status()
    assessments = resp.json()["data"]
    assessment_id = assessments[0]["id"]

    resp = requests.post(
        f"{BASE_URL}/assessment_records",
        json={"assessment_id": assessment_id, "score": 80},
        headers=headers,
    )
    resp.raise_for_status()

    resp = requests.get(
        f"{BASE_URL}/mastery", params={"course_id": course_id}, headers=headers
    )
    resp.raise_for_status()

    resp = requests.post(
        f"{BASE_URL}/paths/generate",
        json={"course_id": course_id, "time_budget_per_week_minutes": 300},
        headers=headers,
    )
    resp.raise_for_status()

    resp = requests.get(
        f"{BASE_URL}/paths/latest", params={"course_id": course_id}, headers=headers
    )
    resp.raise_for_status()

    print("smoke test passed")


if __name__ == "__main__":
    run()
