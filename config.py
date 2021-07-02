from enum import Enum

TOKEN = '1858033393:AAF3GZEnNNEjNEBsOoRJXyPtfgLO0OCO9Fk'
db_file = "database.vdb"

class States(Enum):
    """
    Мы используем БД Vedis, в которой хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    """
    S_START = "0"  # Начало нового диалога
    S_ENTER_NAME = "1"
    S_ENTER_AGE = "2"
    S_ENTER_NUMBER = "3"
    S_ENTER_DATE = '4'