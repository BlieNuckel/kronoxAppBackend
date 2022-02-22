from src.mongo_connector import MongoConnector
import random


def getColor(course: str) -> str:
    if not colorAssigned(course):
        courseColor = generateColor()
        assignColor(course, courseColor)
    else:
        colors = MongoConnector.getCollection("course_colors")
        for color in colors:
            if course.lower() in color["_id"]:
                courseColor = color["color"]

            if color["_id"] == course.lower():
                courseColor = color["color"]
                break

    return courseColor


def colorAssigned(course: str) -> bool:
    colors = MongoConnector.getCollection("course_colors")

    for color in colors:
        if color["_id"] == course.lower():
            return True

    for color in colors:
        if course.lower() in course.lower():
            return True

    return False


def generateColor() -> str:
    return "#%06x" % random.randint(0xCCFFFF, 0xED7B7B)


def assignColor(course: str, color: str) -> None:
    MongoConnector.updateOne(
        "course_colors",
        {"_id": course.lower()},
        {"_id": course.lower(), "color": color},
        True,
    )
