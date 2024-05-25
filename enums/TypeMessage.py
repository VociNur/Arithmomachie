from enum import Enum


class TypeMessage(Enum):
    PREFIX_LENGTH = 10
    CONNECTION = "CONNECT   ", 100
    MATCH = "MATCH     ", 50
    END_CONNECTION = "END       "
    
    def prefix(enum):
        return enum.value[0]
    
    def length(enum):
        return enum.value[1]
    
    def encode_package(enum, s):

        if len(s) > TypeMessage.length(enum):
            raise Exception("La taille n'est pas assez grande !!!", s, enum)
        return enum + s + " " * (TypeMessage.length(enum) - len(s))

    def decode_package(self, s:str):
        if len(s) < 10:
            return [], s
        result = []
        for type in TypeMessage:
            if s[:TypeMessage.PREFIX_LENGTH] == TypeMessage.prefix(type):
                result.append(s[TypeMessage.PREFIX_LENGTH:TypeMessage.PREFIX_LENGTH + TypeMessage.length(type)])
                s = s[TypeMessage.PREFIX_LENGTH + TypeMessage.length(type):]
                break
        return result, s
                        

if __name__ == "__main__":
    print(TypeMessage.prefix(TypeMessage.CONNECTION))
    print(TypeMessage.length(TypeMessage.CONNECTION))
