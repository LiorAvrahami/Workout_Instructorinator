from dataclasses import dataclass


@dataclass
class Speaker():
    # fields
    accent: str
    speed: float

    def __hash__(self) -> int:
        return hash((self.accent, self.speed))

    @staticmethod
    def from_str(speaker_str) -> 'Speaker':
        if ":" not in speaker_str:  # add speed if no speed was given
            speaker_str += ":x1.0"
        accent, speed = speaker_str.split(":")
        if accent not in Speaker.accent_options:
            raise Exception(f"speaker accent {accent} not found")

        if speed[0] == "x":
            speed = speed[1:]
        speed = float(speed)
        return Speaker(accent, speed)

    accent_options = ["us", "com.ng", "com.au", "co.uk", "ca", "co.in", "ie", "co.za",
                      "com.br", "pt", "com.mx", "es", "fr"]
