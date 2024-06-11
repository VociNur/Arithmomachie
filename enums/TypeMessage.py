from enum import Enum


class TypeMessage(Enum):

    CONNECTION = "CONNECT   ", 100
    MATCH = "MATCH     ", 200
    #Grosso modo
    #evaluation: 6 flottants de 3 décimals donc 5 chiffes + séparation : total 36
    # match = 2 evaluations + result + imes
    END_CONNECTION = "END       ", 0

    
    def get_prefix_length():
        return 10

    def prefix(enum):
        return enum.value[0]
    
    def length(enum):
        return enum.value[1]
    
    def encode_package(enum, s):

        if len(s) > TypeMessage.length(enum):
            raise Exception("La taille n'est pas assez grande !!!", s, enum)
        return (TypeMessage.prefix(enum) + s + " " * (TypeMessage.length(enum) - len(s))).encode()

    def decode_package(s:str):
        if len(s) < 10:
            return [], s
        result = []
        decode = True
        while decode:
            decode = False
            for type in TypeMessage:
                if s[:TypeMessage.get_prefix_length()] == TypeMessage.prefix(type):
                    if len(s) < TypeMessage.get_prefix_length() + TypeMessage.length(type):
                        continue #attendre la fin du packet
                    result.append((type, s[TypeMessage.get_prefix_length():TypeMessage.get_prefix_length() + TypeMessage.length(type)].strip()))
                    s = s[TypeMessage.get_prefix_length() + TypeMessage.length(type):]
                    decode = True
                    break
                    
            
        return result, s
                        

if __name__ == "__main__":
    print(TypeMessage.prefix(TypeMessage.CONNECTION))
    print(TypeMessage.length(TypeMessage.CONNECTION))
