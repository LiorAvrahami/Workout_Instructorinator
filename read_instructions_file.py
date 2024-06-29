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
            if "countdown" in args:
                instruction.b_countdown = True
        instructions_list.append(instruction)
        is_text_line = not is_text_line
    return instructions_list
