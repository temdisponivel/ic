# -*- coding: utf-8 -*-
import wx
import wx.grid as wxgrid


#classe do programa, contem os controles de tela, a janela, etc. Herda de wx.Frame
class Interface(wx.Frame):

    LARGURA_TELA = 500
    ALTURA_TELA = 300
    LARGURA_BOTOES = 75
    ALTURA_BOTOES = 25

    def __init__(self):
        #cria o aplicativo
        self.app = wx.App()

        #chama o contrutor do pai - wx.Frame
        wx.Frame.__init__(self, None, -1, "Sensor Sônico", (0, 0), (Interface.LARGURA_TELA, Interface.ALTURA_TELA))

        #cria botão de iniciar e finalizar
        self.btn_iniciar = wx.Button(self, 0, "Iniciar", (10, 10), (Interface.LARGURA_BOTOES, Interface.ALTURA_BOTOES))
        self.btn_finalizar = wx.Button(self, 1, "Finalizar", (10, 40), (Interface.LARGURA_BOTOES, Interface.ALTURA_BOTOES))

        #cria a grid para mostrar os dados da leitura mostrando no Frame
        self.grid_dados = wxgrid.Grid(self)
        self.grid_dados.CreateGrid(15, 8)

        #cria um sizer vertical para a grid
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        #adiciona a grid criado nosizer
        self.sizer.Add(self.grid_dados, 1, wx.EXPAND)

        #mostra a tela e entra no loop de eventos do aplicativo
        self.Show(True)
        self.app.MainLoop()