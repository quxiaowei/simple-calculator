from collections import deque

DEBUG = False

NAME_STR = "abcdcfghighlmnopqrstuvwxyz"
NAME_SET = set(NAME_STR)

class QueueRegister:
    def __init__(self):
        self._registor = dict()
        self._registor_name = deque(NAME_STR)

        self._top_cursor = "a"

    def next_cursor(self):
        DEBUG and print("---fr---", self._top_cursor)
        self._registor_name.rotate(-1)
        self._top_cursor = self._registor_name[0]
        DEBUG and print("---to---", self._top_cursor)

    def __getitem__(self, key):
        return self._read(key)
    
    def __setitem__(self, key, new_value):
        self.write(new_value, key)
    
    def _read(self, key):
        if key in self._registor:
            return self._registor[key]
        return None
    
    def contains(self, key: str) -> bool:
        if key not in NAME_SET:
            # print("not in name set")
            return False

        if key not in self._registor:
            # print("not in register")
            return False

        if self._registor[key] == None:
            # print("register value is None")
            return False
        
        return True
    
    def get_cursor(self):
        return self._top_cursor

    def write(self, value, key=None):
        l_key = key if key else self._top_cursor
        try:
            self._registor_name.index(l_key) 
        except ValueError:
            raise ValueError
        
        if l_key in self._registor:
            self._registor[l_key] = value
        else:
            self._registor[l_key] = value


if __name__ == "__main__":
    DEBUG = True
    reg = QueueRegister();
    reg.write(1111)
    reg.next_cursor()
    reg.write(2222)
    reg.next_cursor()
    reg.write(3333)

    print(reg["a"])
    print(reg["b"])
    print(reg["c"])

