# -*- coding: utf-8 -*-
import wx
import wx.grid as wxgrid
import wx.lib.scrolledpanel as scrolledpanel
import leitor_serial as Leitor


#classe do programa, contem os controles de tela, a janela, etc. Herda de wx.Frame
class Interface(wx.Frame):

    LARGURA_TELA = 800
    ALTURA_TELA = 600
    LARGURA_BOTOES = 75
    ALTURA_BOTOES = 25

    def __init__(self):
        #cria o aplicativo
        self.app = wx.App()

        #chama o contrutor do pai - wx.Frame
        wx.Frame.__init__(self, None, 0, "Sensor Sônico", (0, 0), (Interface.LARGURA_TELA, Interface.ALTURA_TELA))

        #seta cor de fundo branca
        self.SetBackgroundColour("white")

        #inicia o leitor serial
        self.leitor = Leitor.Leitor()

        #cria botão de iniciar e finalizar
        self.btn_iniciar = wx.Button(self, 2, "Iniciar", (10, 10), (Interface.LARGURA_BOTOES, Interface.ALTURA_BOTOES))
        self.btn_finalizar = wx.Button(self, 3, "Finalizar", (10, 40), (Interface.LARGURA_BOTOES, Interface.ALTURA_BOTOES))
        self.Bind(wx.EVT_BUTTON, self.OnIniciar, id=2)
        self.Bind(wx.EVT_BUTTON, self.OnFinalizar, id=3)

        #cria o panel onde ficará a grid
        self.panel_grid = scrolledpanel.ScrolledPanel(self, 1, (10, 70), (100, 300))

        #cria a grid para mostrar os dados da leitura mostrando no panel
        self.grid_dados = wxgrid.Grid(self.panel_grid)
        self.grid_dados.CreateGrid(10, 4)

        #cria um sizer vertical para a grid
        self.sizer_grid = wx.BoxSizer(wx.VERTICAL)

        #adiciona a grid criada no sizer
        self.sizer_grid.Add(self.grid_dados)
        self.panel_grid.SetSizerAndFit(self.sizer_grid)

        #mostra a tela e entra no loop de eventos do aplicativo
        self.Show(True)
        self.app.MainLoop()

    #Evento do botao iniciar
    def OnIniciar(self, event):
        self.leitor.Inicia()

    #Evento do botão finalizar
    def OnFinalizar(self, event):
        self.leitor.Finaliza()