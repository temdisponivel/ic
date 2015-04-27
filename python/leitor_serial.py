# -*- coding: utf-8 -*-
import serial
import platform
import threading
import serial.tools.list_ports


#classe para leitura dos dados que chegam da porta serial
class Leitor(threading.Thread):

    porta = '/dev/ttyUSB0'
    frequencia_leitura = 9600
    arquivo_gravacao = "saida_serial_arduino.txt"

    def __init__(self):
        #contrutor da thread
        threading.Thread.__init__(self)

        #pega todas as portas seriais
        portas = list(serial.tools.list_ports.comports())

        #para cada porta serial
        for porta in portas:
            #se estamos rodando no windows
            if platform.system() == 'Windows':
                if "USB Serial Port (COM3)" in porta[1]:
                    Leitor.porta = porta[0]

        self.lendo = False

    def Inicia(self):
        #abre o arquivo para leitura
        if self.lendo is False:
            self.lendo = True
            self.arquivo = open(Leitor.arquivo_gravacao, "w")
            self.porta_serial = serial.Serial(Leitor.porta, Leitor.frequencia_leitura)
            self.stop_event = threading.Event()
            self.start()

    def run(self):
        while (not self.stop_event.is_set()):
            #le as informações do arduino
            linha_leitura = self.porta_serial.read()

            #coloca as informações do arduino na tela
            print(linha_leitura)

            """
                abre, escreve e fecha o arquivo. Aberto e fechado a toda leitura de linha
                para que mesmo se a leitura for cancelada, haja dados no arquivo
            """
            if (not self.arquivo.closed):
                self.arquivo.write(linha_leitura + "\n")

    def Finaliza(self):
        if self.lendo:
            self.stop_event.set()
            self.arquivo.close()
            self.porta_serial.close()
            self.lendo = False