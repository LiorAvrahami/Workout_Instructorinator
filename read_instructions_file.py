class InstructionLine:
    pass
class TextLine(InstructionLine):
    text:str
class WaitLine(InstructionLine):
    time_seconds:float
    b_countdown:bool

def read_instructions_file() -> list[InstructionLine]:
    
    return []
