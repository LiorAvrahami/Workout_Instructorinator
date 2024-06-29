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
    for line in lines:
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
    apply_preliminary_keywords(instructions_list)
    return instructions_list


def apply_preliminary_keywords(instructions_list: List[InstructionLine]):
    for line_index in range(len(instructions_list)):
        line = instructions_list[line_index]
        if type(line) == WaitLine:
            if line.b_countdown:
                del instructions_list[line_index]
                original_time = line.time_seconds
                if original_time < 40:
                    times = [original_time / 2]
                    comments = ["half way done"]
                    text_time = [1]
                elif original_time < 60:
                    times = [original_time / 2, original_time / 2 - 10]
                    comments = ["half way done", "ten seconds left"]
                    text_time = [1, 1.5]
                else:
                    times = [original_time / 2, original_time / 4, original_time / 4 - 10]
                    comments = ["half way done", "one quarter left", "ten seconds left"]
                    text_time = [1, 1.5, 1.5]
                last_wait_time = original_time - sum(times)
                times = [times[i] - text_time[i] for i in range(len(times))]
                times.append(last_wait_time)

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
