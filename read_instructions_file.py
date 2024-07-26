from typing import List


class InstructionLine:
    pass


class TextLine(InstructionLine):
    text: str


class WaitLine(InstructionLine):
    time_seconds: float
    b_countdown: bool


def read_instructions_file() -> list[InstructionLine]:
    lines = []
    with open("instructions.txt", "r") as f:
        lines = f.readlines()

    instructions_list = []
    is_text_line = True
    for line_index, line in enumerate(lines):
        try:
            if line[0] == "#":
                continue
            if is_text_line:
                instruction = TextLine()
                instruction.text = line
            else:
                instruction = WaitLine()
                args = line.replace(" ", "").split(",")
                time = args[0]
                args = args[1:]
                min, sec = time.split(":")
                min = float(min)
                sec = float(sec)
                instruction.time_seconds = min * 60 + sec
                instruction.b_countdown = any(["countdown" in a for a in args])
            instructions_list.append(instruction)
            is_text_line = not is_text_line
        except Exception as e:
            raise Exception(f"problem with line {line[:-1]}. line number is {line_index}.\n Exception was {e.with_traceback()}")
    apply_preliminary_keywords(instructions_list)
    # remove empty waits
    instructions_list = [line for line in instructions_list if (type(line) != WaitLine or line.time_seconds != 0)]
    # merge consecutive instruction lines and remove "\n"'s
    line_index = 0
    while line_index < len(instructions_list) - 1:
        if type(instructions_list[line_index]) == TextLine and type(instructions_list[line_index + 1]) == TextLine:
            instructions_list[line_index].text += " " + instructions_list[line_index + 1].text
            del instructions_list[line_index + 1]
        else:
            if type(instructions_list[line_index]) == TextLine:
                instructions_list[line_index].text = instructions_list[line_index].text.replace("\n", "")
            line_index += 1

    return instructions_list


def apply_preliminary_keywords(instructions_list: List[InstructionLine]):
    line_index = -1
    while True:
        line_index += 1
        if not line_index < len(instructions_list):
            break
        line = instructions_list[line_index]
        if type(line) == WaitLine:
            if line.b_countdown:
                original_time = int(line.time_seconds)
                del instructions_list[line_index]
                times: list[int] = [0]  # the times after which countdown happens
                comments = []  # the texts to be said in the countdowns

                # first announce the total time of the exercise
                if original_time < 60:
                    comments.append(f"{original_time} seconds")
                elif original_time % 60 != 0:
                    comments.append(f"{int(original_time//60)} minutes {original_time%60} seconds")
                else:
                    comments.append(f"{int(original_time//60)} minutes")

                time_left = original_time
                while time_left != 0:
                    if time_left >= 3 * 60:  # announce the next hole minute
                        times.append(60 + time_left % 60)
                        time_left -= times[-1]
                        comments.append(f"{int(time_left//60)} minutes")
                    if time_left >= 90:  # announce the last minute
                        times.append(time_left - 60)
                        time_left -= times[-1]
                        comments.append(f"1 minute")
                    elif time_left >= 55:
                        times.append(time_left - 30)
                        time_left -= times[-1]
                        comments.append(f"30 seconds")
                    elif time_left >= 30:
                        times.append(time_left - 10)
                        time_left -= times[-1]
                        comments.append(f"10 seconds")
                    else:
                        times.append(time_left)
                        time_left -= times[-1]
                expected_announcements_time = [len(comment.split(" ")) for comment in comments]  # time it takes to say the countdowns
                # remove the expected_announcements_times from the wait times
                times = [times[0]] + \
                        [times[i] - expected_announcements_time[i - 1] for i in range(1, len(times))]
                for i in range(len(times)):
                    new_line = WaitLine()
                    new_line.time_seconds = times[i]
                    new_line.b_countdown = False
                    instructions_list.insert(line_index + i * 2, new_line)
                    if i < len(comments):
                        new_line = TextLine()
                        new_line.text = comments[i]
                        instructions_list.insert(line_index + i * 2 + 1, new_line)
    return instructions_list
