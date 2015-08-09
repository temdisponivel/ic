# -*- coding: utf-8 -*-
import serial
import threading
import serial.tools.list_ports
import time
import wx

#classe que representa uma interface de comunicação entre objetos para enviar os dados lidos do arduino
class RecebeLeitura(object):

    #recebe o dado lido do arduino, um objeto ComunicadorArduino.DadoLeitura.
    def receber(self, dado_leitura):
        raise NotImplementedError("Você deve implementar este método!")

#classe que representa os dados lidos do arduino. Que são basicamente a linha lida e o tempo de leitura.
class DadoLeitura(object):

    tempo = 0
    dado = 0

    #dado = dado lido do arduino (uma linha), tempo_leitura = tempo da leitura.
    def __init__(self, dado, tempo_leitura):
        self.tempo = tempo_leitura #tempo em millisegundos*
        self.dado = dado

    def __str__(self):
        return "Tempo: " + str(self.tempo) + " | Dado arduino: " + str(self.dado)

    def get_csv(self):
        return str(self.tempo) + "," + str(self.dado)

#classe para leitura dos dados que chegam da porta serial
class Leitor(threading.Thread):

    intervalo_leitura = 1.0/5.0

    def __init__(self, interface):
        #contrutor da thread
        threading.Thread.__init__(self)

        if not hasattr(interface, "receber"):
            raise Exception("O objeto deve conter o método de interface para o leitor. Definido em ComunicacaoArduino.RecebeLeitura")

        self.setDaemon(False)
        self.setName("LEITOR SERIAL ARDUINO")

        #pega todas as portas seriais
        portas = list(serial.tools.list_ports.comports())
        porta_valida = False

        #para cada porta serial
        for porta in portas:
            try:
                porta_serial = serial.Serial(porta[0], 9600)
                self.porta_serial = porta_serial
                porta_valida = True
                break
            except Exception as ex:
                print(ex)
                continue

        if (not porta_valida):
            raise IOError("Nao foi possivel conectar ao arduino via serial!")

        self.lendo = False
        self.interface = interface

    def inicia(self):
        #abre o arquivo para leitura
        self.tempo_leitura = 0
        self.stop_event = threading.Event()
        self.start()

    def run(self):
        while (not self.stop_event.is_set()):

            #le as informações do arduino
            linha_leitura = self.porta_serial.readline()

            #se nao é pra processar, n faz nd
            if (not self.lendo):
                continue

            #manda as informações para o objeto de interface
            wx.CallAfter(self.interface.receber, DadoLeitura(linha_leitura, self.tempo_leitura))

            #pega o tempo da leitura
            self.tempo_leitura += Leitor.intervalo_leitura

            #espera o intervalo definido na classe
            time.sleep(Leitor.intervalo_leitura)

    #pausa a leitura dos dados
    def pausa(self):
        self.lendo = False

    #continua a leitura dos dados
    def continua(self):
        self.lendo = True

    #reinicia a leitura dos dados
    def reinicia(self):
        self.tempo_leitura = 0

    #fecha porta serial e finaliza a thread. Se chamar inicia após disso, acontece erro.
    #para pausar e reiniciar, use os métodos pausa e continua
    def finaliza(self):
        self.stop_event.set()
        self.porta_serial.close()
        self.lendo = False