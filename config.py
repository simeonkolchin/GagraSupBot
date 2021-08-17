from enum import Enum

TOKEN = '1858033393:AAF3GZEnNNEjNEBsOoRJXyPtfgLO0OCO9Fk'
# TOKEN = '1850548629:AAFQisjm2Mh0zgpi9OWmNhhg3M2U4Z9fLtU'



db_file = "database.vdb"

class States(Enum):
    S_START = '0'  # Начало нового диалога
    S_ENTER_NAME = '1'
    S_ENTER_AGE = '2'
    S_ENTER_NUMBER = '3'
    S_ENTER_DATE = '4'

    S_EDIT_NAME = '5'
    S_EDIT_AGE = '6'
    S_EDIT_NUMBER = '7'
    S_EDIT_DATE = '8'
    S_EDIT_TIME = '9'

    S_USER = '10'

    S_USER_AGE = '11'
    S_USER_DATE = '12'

    ADMIN_SEND_ALL = '13'
    ADMIN_ADVERTISEMENT_PHOTO = '14'
    ADMIN_SEND_ONE = '15'
    ADMIN_SEND_ONE_M = '16'
    ADMIN_SEND_AD_PHOTO = '17'
    ADMIN_SEND_AD_PHOTO_BUTTON_H = '18'
    ADMIN_SEND_AD_VIDEO = '19'
    ADMIN_ADVERTISEMENT_VIDEO = '20'
    ADMIN_SEND_AD_VIDEO_BUTTON_H = '21'

    C_E_NAME = '22'
    C_E_TEXT = '23'
    C_E_PRICE = '24'
    C_E_PEOPLE = '25'

    N_USER_NAME = '26'
    N_USER_NUMBER = '27'

    ADMIN_SM_USER = '28'

    EDIT_NAME_EVENT = '29'
    EDIT_TEXT_EVENT = '30'
    EDIT_PRICE_EVENT = '31'
    EDIT_PEOPLE_EVENT = '32'