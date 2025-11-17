from database.impianto_DAO import ImpiantoDAO
from database.consumo_DAO import ConsumoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        self._impianti_dao= ImpiantoDAO()
        self._consumo_dao= ConsumoDAO()

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        # TODO
        impianti= self._impianti_dao.get_impianti()
        impianti_con_consumi_mese= []
        for impianto in impianti:
            consumi_per_impianto= self._consumo_dao.get_consumi(impianto.id)
            consumi_impianto_mese=[]
            for consumo in consumi_per_impianto:
                if int(consumo.data.month)== mese:
                    consumi_impianto_mese.append(int(consumo.kwh))
            if len(consumi_impianto_mese)==0:
                media=0
            else:
                media= sum(consumi_impianto_mese)/len(consumi_impianto_mese)
            impianto=[impianto.nome, media]
            impianti_con_consumi_mese.append(impianto)
        return impianti_con_consumi_mese

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        # TODO
        #condizione terminale: arrivo al settimo giorno
        if giorno>7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return
        #condizione ricorsiva
        for impianto in consumi_settimana:
            id_impianto = impianto['id_impianto']
            costo = int(impianto['consumi_prima_settimana_del_mese'][giorno - 1])
            if id_impianto != ultimo_impianto:
                costo += 5
            sequenza_parziale.append(id_impianto)
            self.__ricorsione(sequenza_parziale, giorno + 1, id_impianto, costo_corrente + costo, consumi_settimana)
            sequenza_parziale.pop()



    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        # TODO
        impianti= self._impianti_dao.get_impianti()
        impianti_consumi_prima_settimana= []
        for impianto in impianti:
            consumi_prima_settimana=[]
            consumi_impianto= self._consumo_dao.get_consumi(impianto.id)
            for consumo in consumi_impianto:
                if consumo.data.day<=7 and int(consumo.data.month)== mese:
                    consumi_prima_settimana.append(consumo.kwh)
            consumi_prima_settimana_impianto= {'id_impianto': impianto.id, 'consumi_prima_settimana_del_mese': consumi_prima_settimana}
            impianti_consumi_prima_settimana.append(consumi_prima_settimana_impianto)
        return impianti_consumi_prima_settimana
