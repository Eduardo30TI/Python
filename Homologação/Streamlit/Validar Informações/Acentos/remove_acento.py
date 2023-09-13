import unicodedata
import re

class Acentuacao:

    def RemoverAcento(string: str)->str:

        normalized=unicodedata.normalize('NFD',string)

        return ''.join([l for l in normalized if not unicodedata.combining(l)])

        pass

    pass