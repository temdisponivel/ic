# -*- coding: utf-8 -*-
import wx
import wx.grid as wxgrid
import wx.lib.scrolledpanel as scrolledpanel
import leitor_serial as Leitor
import wx.lib.plot as plot


class Grafico(plot.PlotCanvas):

    LARGURA_GRAFICOS = 400
    ALTURA_GRAFICOS = 250

    def __init__(self, parente, nome, label_x, label_y):
        plot.PlotCanvas.__init__(self, parente, -1, style=wx.BORDER_NONE, size=wx.Size(Grafico.LARGURA_GRAFICOS, Grafico.ALTURA_GRAFICOS))
        self.data = [(1, 2), (2, 3), (3, 5), (4, 6), (5, 8), (6, 8), (10, 10)]
        line = plot.PolyLine(self.data, legend='', colour='pink', width=2)
        gc = plot.PlotGraphics([line], nome, label_x, label_y)
        self.Draw(gc, xAxis=(0, 15), yAxis=(0, 15))


#classe do programa, contem os controles de tela, a janela, etc. Herda de wx.Frame
class Interface(wx.Frame):

    LARGURA_TELA = 1024
    ALTURA_TELA = 768
    LARGURA_BOTOES = 75
    ALTURA_BOTOES = 25

    def __init__(self):
        #cria o aplicativo
        self.app = wx.App()

        #chama o contrutor do pai - wx.Frame
        wx.Frame.__init__(self, None, 0, "Sensor Sônico", (0, 0), (Interface.LARGURA_TELA, Interface.ALTURA_TELA))

        #seta cor de fundo branca
        #self.SetBackgroundColour("white")

        #inicia o leitor serial
        self.leitor = Leitor.Leitor()

        #cria botão de iniciar e finalizar
        self.btn_iniciar = wx.Button(self, 2, "Iniciar", (10, 10), (Interface.LARGURA_BOTOES, Interface.ALTURA_BOTOES))
        self.btn_finalizar = wx.Button(self, 3, "Finalizar", (20 + Interface.LARGURA_BOTOES, 10), (Interface.LARGURA_BOTOES, Interface.ALTURA_BOTOES))
        self.Bind(wx.EVT_BUTTON, self.OnIniciar, id=2)
        self.Bind(wx.EVT_BUTTON, self.OnFinalizar, id=3)

        #cria o panel onde ficará a grid
        self.panel_grid = scrolledpanel.ScrolledPanel(self, -1, (10, 70), (100, 300))
        self.grafico_velocidade = Grafico(self, "VELOCIDADE", "X", "T")
        self.grafico_aceleracao = Grafico(self, "ACELERAÇÃO", "V", "T")

        #cria a grid para mostrar os dados da leitura mostrando no panel
        self.grid_dados = wxgrid.Grid(self.panel_grid)
        self.grid_dados.CreateGrid(10, 4)

        #cria os sizer para os objetos da tela
        self.sizer_grid = wx.BoxSizer(wx.VERTICAL)
        self.sizer_velocidade = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_aceleracao = wx.BoxSizer(wx.HORIZONTAL)

        #adiciona os objetos nos sizers
        self.sizer_velocidade.Add(self.grafico_velocidade)
        self.sizer_aceleracao.Add(self.grafico_aceleracao)
        self.sizer_grid.Add(self.grid_dados)
        self.panel_grid.SetSizerAndFit(self.sizer_grid)
        self.grafico_velocidade.SetSizerAndFit(self.sizer_velocidade)
        self.grafico_aceleracao.SetSizerAndFit(self.sizer_aceleracao)

        #mostra a tela e entra no loop de eventos do aplicativo
        self.Show(True)
        self.DesenhaLinhaVelocidade(wx.Point(0, 0), wx.Point(1000, 100))
        self.DesenhaLinhaAceleracao(wx.Point(0, 0), wx.Point(1000, 100))
        self.app.MainLoop()

    #Evento do botao iniciar
    def OnIniciar(self, event):
        self.leitor.Inicia()

    #Evento do botão finalizar
    def OnFinalizar(self, event):
        self.leitor.Finaliza()