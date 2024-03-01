if not __package__:
    from define import WordType
else:
    from .define import WordType

__all__ = ["ParserLogger"]


class ParserLogger(dict[int, tuple[str, WordType, int]]):
    """logger for messages in parsing"""

    def add(self, message: str, *, at: int, to: int = 0, forced=False):
        """Add message

        Args:
            message: message text
            at:      position in raw input
            forced:  higher priority (default False)
        Returns:
            None
        """

        if not forced and at in self and self[at]:
            pass

        l_type: WordType

        l_type = WordType.PLACEHOLDER
        if at not in self or not self[at]:
            self[at] = (
                message,
                l_type,
                to,
            )

    def get(self) -> tuple[int, str, int]:
        i = max(list(self.keys()))
        return i, self[i][0], self[i][2]

    def message(self, s: str) -> str:
        l_buffer = list("-" * (len(s) + 4))
        l_pos, l_log, l_to = self.get()

        if l_to > l_pos:
            l_buffer = l_buffer[:l_pos] + ["^"] * (l_to - l_pos) + l_buffer[l_to:]
        else:
            l_buffer[l_pos] = "^"

        l_m1 = "  Input: " + s
        l_m2 = "         " + "".join(l_buffer)
        l_m3 = "  Error: " + l_log
        return "\n".join([l_m1, l_m2, l_m3])
