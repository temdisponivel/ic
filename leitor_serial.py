# -*- coding: utf-8 -*-
import serial


#classe para leitura dos dados que chegam da porta serial
class Leitor:

    porta = '/dev/ttyUSB0'
    frequencia_leitura = 9600

    def __init__(self):
        self.porta_serial = serial.Serial(Leitor.porta, Leitor.frequencia_leitura)

    def Le(self):
        print((self.porta_serial.read()))