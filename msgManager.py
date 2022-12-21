import pandas as pd
import numpy as np


class MsgManager():
    @staticmethod
    def load_messages(filePath):
        mensajes = pd.read_csv(filePath, dtype=str)
        MensajesMap = dict(zip(mensajes['IDParte'], mensajes['Mensaje']))
        return MensajesMap

    @staticmethod
    def sort_messages(MensajesMap):
        IDParts = list(MensajesMap.keys())
        Parts = list(MensajesMap.values())
        Indexes = np.argsort([int(IDPart) for IDPart in IDParts])
        MensajesMap = {}
        for ind in Indexes:
            MensajesMap[IDParts[ind]] = Parts[ind]

        return MensajesMap

    @staticmethod
    def save_messages(MensajesMap, filename):
        MensajesMap = MsgManager.sort_messages(MensajesMap)
        mensajes = np.array([list(MensajesMap.keys()), list(MensajesMap.values())])
        mensajes = pd.DataFrame(mensajes.transpose())
        mensajes.columns = ['IDParte', 'Mensaje']
        mensajes.to_csv(filename, index=False)
