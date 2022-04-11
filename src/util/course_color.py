from src.services.mongo_connector import MongoConnector
from random import Random

global NEXT_COLOR_GROUP
global COLOR_GROUPS
NEXT_COLOR_GROUP = 0

RED_COLORS = ["#ff424f", "#ff4242", "#ff5e42"]
ORANGE_COLORS = ["#ff7142", "#ff9442", "#ffad42"]
YELLOW_COLORS = ["#ffc342", "#ffe642", "#f9ff42"]
GREEN_COLORS = ["#bdff42", "#7eff42", "#42ff45", "#42ff8a"]
LIGHT_BLUE_COLORS = ["#42ffc0", "#42ffe0", "#42f6ff"]
BLUE_COLORS = ["#42aaff", "#426eff", "#5242ff"]
PURPLE_COLORS = ["#8142ff", "#ad42ff", "#d042ff"]
PINK_COLORS = ["#fc42ff", "#ff42e6", "#ff427b"]

COLOR_GROUPS = [
    RED_COLORS,
    PURPLE_COLORS,
    YELLOW_COLORS,
    GREEN_COLORS,
    BLUE_COLORS,
    PINK_COLORS,
    ORANGE_COLORS,
    LIGHT_BLUE_COLORS,
]


def getColor(course: str) -> str:
    if not colorAssigned(course):
        courseColor = generateColor()
        assignColor(course, courseColor)
    else:
        colors = MongoConnector.getCollection("course_colors")
        for color in colors:
            if course.lower() in color["_id"] or color["_id"] in course.lower():
                courseColor = color["color"]

            if color["_id"] == course.lower():
                courseColor = color["color"]
                break

    return courseColor


def colorAssigned(course: str) -> bool:
    colors = MongoConnector.getCollection("course_colors")

    for color in colors:
        if color["_id"] in course.lower() or course.lower() in color["_id"]:
            return True

    return False


def generateColor() -> str:
    global COLOR_GROUPS
    global NEXT_COLOR_GROUP

    print("PICKING RANDOM COLOR")
    print(f"COLOR GROUPS: {COLOR_GROUPS}")
    print(f"NEXT COLOR GROUP: {NEXT_COLOR_GROUP}")
    pickedColor = Random.choice(COLOR_GROUPS[NEXT_COLOR_GROUP % len(COLOR_GROUPS)])
    print(f"RANDOM COLOR: {pickedColor}")
    NEXT_COLOR_GROUP += 1
    print("NEXT COLOR")

    return pickedColor


def assignColor(course: str, color: str) -> None:
    MongoConnector.updateOne(
        "course_colors",
        {"_id": course.lower()},
        {"_id": course.lower(), "color": color},
        True,
    )
