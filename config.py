from enum import Enum

TOKEN = '1858033393:AAF3GZEnNNEjNEBsOoRJXyPtfgLO0OCO9Fk'
db_file = "database.vdb"

class States(Enum):
    S_START = "0"  # Начало нового диалога
    S_ENTER_NAME = "1"
    S_ENTER_AGE = "2"
    S_ENTER_NUMBER = "3"
    S_ENTER_DATE = '4'

    S_EDIT_NAME = '5'
    S_EDIT_AGE = '6'
    S_EDIT_NUMBER = '7'
    S_EDIT_DATE = '8'
    S_EDIT_TIME = '9'

    S_USER = '10'
    S_USER_AGE = '11'
    S_USER_DATE = '12'
