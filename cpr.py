import argparse
import requests
import json


def read_file(file_location):
    with open(file_location, "r") as f:
        return json.loads(f.read())


def read_dot_env():
    with open("./.env", "r") as f:
        data = f.read().split("\n")
        for x in data:
            temp = x.split("=")
            if temp[0] == "GITHUB_TOKEN":
                return temp[1]
    raise IndexError("GITHUB_TOKEN not found on .env file")


def get_student_name(students, github):
    for student in students:
        if student["github"] == github:
            return student["name"]
    raise IndexError("student not found")


def argument_parser():
    parser = argparse.ArgumentParser(description="Check pull requests of challenges")
    parser.add_argument("-w", "--week",
                        help="week of the challenges",
                        default="1", type=str, metavar="week")
    parser.add_argument("-d", "--day",
                        help="day of the challenges",
                        default="1", type=str, metavar="day")
    return parser.parse_args()


def main():
    args = argument_parser()
    url = "https://api.github.com"
    GITHUB_TOKEN = read_dot_env()
    headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {GITHUB_TOKEN}"
            }
    params = {"per_page": "100"}
    config = read_file("./config.json")
    students_github = list(map(lambda student: student["github"],
                                config["students"]))
    challenges = read_file("./challenges.json")["week"][args.week]["day"][args.day]

    for challenge in challenges:
        students_who_pull_request = []
        students_who_dont = []
        response = requests.get(f"{url}/repos/{config['organization']}/{challenge}/pulls",
                                headers=headers, params=params)
        pulls = response.json()
        number = 1

        for pull in pulls:
            if pull["user"]["login"] in students_github:
                students_who_pull_request.append(pull["user"]["login"])

        for student in students_github:
            if student not in students_who_pull_request:
                students_who_dont.append(get_student_name(config["students"], student))

        if len(students_who_dont) > 0:
            for student in students_who_dont:
                print(f"{student} tidak mengumpulkan challenge {challenge}")
        else:
            print(f"Congrats... semua buddy mengumpulkan challenge {challenge}")


if __name__ == '__main__':
    main()

