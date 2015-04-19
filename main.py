# -*- coding: utf-8 -*-
import interface_usuario
import leitor_serial

#inicia a aplicação
interface_usuario = interface_usuario.Interface()
leitor = leitor_serial.Leitor()
leitor.Le()