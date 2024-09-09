from typing import List
import re


class InstructionLine:
    original_index: int
    pass


class TextLine(InstructionLine):
    text: str
    b_new_chapter: bool

    def __init__(self) -> None:
        super().__init__()
        self.b_new_chapter = False


class WaitLine(InstructionLine):
    time_seconds: float
    b_countdown: bool
    b_beepreps: bool  # whether or not to indicate repetitions with beeps
    b_announce_time: bool
    b_delaybeep: bool
    delaybeep_time: float = 0
    num_beep_reps: int = 0

    def __init__(self) -> None:
        super().__init__()
        self.time_seconds = False
        self.b_countdown = False
        self.b_beepreps = False
        self.b_announce_time = False
        self.b_delaybeep = False
        self.delaybeep_time = 0
        self.num_beep_reps = 0


def read_instructions_file() -> list[InstructionLine]:
    lines = []
    with open("instructions.txt", "r") as f:
        lines = f.read().replace("\r", "").split("\n")

    instructions_list = []
    is_text_line = True
    for line_index, line in enumerate(lines):
        try:
            if line[0] == "#":
                continue
            if is_text_line:
                instruction = TextLine()
                instruction.text = line
                instruction.b_new_chapter = True
            else:
                instruction = WaitLine()
                args = line.replace(" ", "").split(",")
                time = args[0]
                args = args[1:]
                min, sec = time.split(":")
                min = float(min)
                sec = float(sec)
                instruction.time_seconds = min * 60 + sec
                instruction.b_countdown = "countdown" in args
                instruction.b_beepreps = "beepreps" in args
                instruction.b_announce_time = any(["announce_time" in a for a in args])
                if any(["delaybeep" in a for a in args]):
                    delay_index = args.index("delaybeep")
                    instruction.b_delaybeep = True
                    instruction.delaybeep_time = float(args[delay_index + 1])
                else:
                    instruction.b_delaybeep = False
                    instruction.delaybeep_time = 0
                if instruction.b_beepreps:
                    instruction.num_beep_reps = extract_number_of_repetitions(len(instructions_list) - 1, instructions_list)
            instruction.original_index = line_index
            instructions_list.append(instruction)
            is_text_line = not is_text_line
        except Exception as e:
            tb = e.__traceback__
            raise Exception(f"problem with line {line[:-1]}. line number is {line_index+1}.\n Exception was {e.with_traceback(tb)}")
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
            original_time = int(line.time_seconds)
            if line.b_announce_time or line.b_countdown:
                # announce time
                if original_time < 60:
                    time_announcement = f"for {original_time} seconds"
                elif original_time % 60 != 0:
                    time_announcement = f"for {int(original_time//60)} minutes {original_time%60} seconds"
                else:
                    time_announcement = f"for {int(original_time//60)} minutes"
                new_line = TextLine()
                new_line.text = time_announcement
                instructions_list.insert(line_index, new_line)
                line_index += 1  # this line is crucial, it keeps line_index and line in sinc.
                assert (line == instructions_list[line_index])
                line.b_announce_time = False
            if line.b_countdown:
                del instructions_list[line_index]
                times: list[int] = []  # the times after which countdown happens
                comments = []  # the texts to be said in the countdowns

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
                    elif time_left >= 45:
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
                    new_line.original_index = line.original_index
                    new_line.b_announce_time = False
                    new_line.b_beepreps = False
                    new_line.num_beep_reps = False
                    if i == 0:
                        new_line.b_delaybeep = line.b_delaybeep
                        new_line.delaybeep_time = line.delaybeep_time
                    instructions_list.insert(line_index + i * 2, new_line)
                    if i < len(comments):
                        new_line = TextLine()
                        new_line.text = comments[i]
                        new_line.original_index = line.original_index
                        instructions_list.insert(line_index + i * 2 + 1, new_line)
    return instructions_list


def extract_number_of_repetitions(current_index, instructions_list):
    line = instructions_list[current_index]
    if type(line) != TextLine:
        raise (Exception(f"Implementation-Bug. inconsistency of type 15986 at line {current_index}"))
    try:
        number_of_repetitions = int(re.search(r"\d+", line.text).group())  # extract the first number from last line
    except:
        if line.text[:6] == "change" or line.text[:6] == "switch":
            number_of_repetitions = extract_number_of_repetitions(current_index - 2, instructions_list)
        else:
            raise (Exception(f"Error: couldn't find number in line {line.original_index+1} \n{line.text}"))
    return number_of_repetitions
