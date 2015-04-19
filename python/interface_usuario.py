# -*- coding: utf-8 -*-
import wx


#classe do programa, contem os controles de tela, a janela, etc.
class Interface:

    def __init__(self):
        app = wx.App()
        janela = wx.Frame(None, -1, "Sensor Sônico")
        janela.Show(True)
        app.MainLoop()

    def MostraDados(self, dado):
        print(dado)