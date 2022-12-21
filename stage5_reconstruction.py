import pandas as pd
import base64

if __name__ == '__main__':
    mensajes_df = pd.read_csv('./files/mensajes_parciales.csv')
    mensajes = mensajes_df['Mensaje']

    str_file = ""
    for mensaje in mensajes:
        str_file += mensaje
    str_file = str_file.encode('ASCII')
    str_file = base64.b64decode(str_file)

    file = open('secret_file.png', 'wb+')
    file.write(str_file)
    file.close()