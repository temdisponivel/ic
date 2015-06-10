# -*- coding: utf-8 -*-
import serial
import platform
import threading
import serial.tools.list_ports
import time


#classe para leitura dos dados que chegam da porta serial
class Leitor(threading.Thread):

    INTEVALO_LEITURA = 1.0/30.0

    def __init__(self, interface):
        #contrutor da thread
        threading.Thread.__init__(self)

        #define a porta padrão como ttyUSB0 para sistemas Unix
        self.porta = '/dev/ttyUSB0'

        #pega todas as portas seriais
        portas = list(serial.tools.list_ports.comports())

        #para cada porta serial
        for porta in portas:
            #se estamos rodando no windows
            if platform.system() == 'Windows':
                if "USB Serial Port" in porta[1]:
                    self.porta = porta[0]

        self.lendo = False
        self.frequencia_leitura = 9600
        self.interface = interface

    def Inicia(self):
        #abre o arquivo para leitura
        if self.lendo is False:
            self.lendo = True
            self.porta_serial = serial.Serial(self.porta, self.frequencia_leitura)
            self.stop_event = threading.Event()
            self.tempo_leitura = 0;
            self.start()

    def run(self):
        while (not self.stop_event.is_set()):
            #le as informações do arduino
            linha_leitura = self.porta_serial.readline()

            #coloca as informações do arduino na tela
            self.interface.RecebeLeitura(linha_leitura, self.tempo_leitura)

            #pega o tempo da leitura
            self.tempo_leitura += Leitor.INTEVALO_LEITURA;

            #só roda a cada 1/60 segundos
            time.sleep(Leitor.INTEVALO_LEITURA)

    def Finaliza(self):
        if self.lendo:
            self.stop_event.set()
            self.porta_serial.close()
            self.lendo = False