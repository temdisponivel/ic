# -*- coding: utf-8 -*-
import serial
import platform
import threading
import serial.tools.list_ports
import time

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

    intervalo_leitura = 1.0/30.0

    def __init__(self, interface):
        #contrutor da thread
        threading.Thread.__init__(self)

        if not hasattr(interface, "receber"):
            raise Exception("O objeto deve conter o método de interface para o leitor. Definido em ComunicacaoArduino.RecebeLeitura")

        #define a porta padrão como ttyUSB0 para sistemas Unix
        self.porta = '/dev/ttyUSB0'

        #pega todas as portas seriais
        self.portas = list(serial.tools.list_ports.comports())

        #para cada porta serial
        for porta in self.portas:
            #se estamos rodando no windows
            if platform.system() == 'Windows':
                if "USB Serial Port" in porta[1]:
                    self.porta = porta[0]

        self.lendo = False
        self.frequencia_leitura = 9600
        self.interface = interface

    def inicia(self):
        #abre o arquivo para leitura
        if self.lendo is False:
            self.lendo = True
            self.porta_serial = serial.Serial(self.porta, self.frequencia_leitura)
            self.stop_event = threading.Event()
            self.tempo_leitura = 0
            self.start()

    def run(self):
        while (not self.stop_event.is_set()):
            #le as informações do arduino
            linha_leitura = self.porta_serial.readline()

            #manda as informações para o objeto de interface
            self.interface.receber(DadoLeitura(linha_leitura, self.tempo_leitura))

            #pega o tempo da leitura
            self.tempo_leitura += Leitor.intervalo_leitura;

            #espera o intervalo definido na classe
            time.sleep(Leitor.intervalo_leitura)

    def finaliza(self):
        if self.lendo:
            self.stop_event.set()
            self.porta_serial.close()
            self.lendo = False