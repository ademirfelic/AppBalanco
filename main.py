from kivy.app import App
from kivy.lang import Builder
from kivy.core.audio import SoundLoader
from kivy.uix.floatlayout import FloatLayout
from kivy_garden.zbarcam import ZBarCam
import kivy_garden.xcamera
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from telas import *
from botoes import *
from bannerProduto import *
import requests
import os
import certifi
from datetime import date
import time
from kivy.core.window import Window
Window.keyboard_anim_args = {'d': 0.2, 't': 'in_out_expo'}
Window.softinput_mode = 'below_target'
os.environ['SSL_CERT_FILE'] = certifi.where()
GUI = Builder.load_file('main.kv')
Window.size = (350, 700)


class MyApp(App):
    loja = ''
    lojas = ['Matriz', 'Prudente', 'Cabo Branco', 'Bessa', 'Mossoro', 'Afonso Pena', 'Princesa Isabel', 'São Paulo']
    som_erro = SoundLoader.load('sons/erro.mp3')
    som_envio = SoundLoader.load('sons/envio.mp3')
    som_beep = SoundLoader.load('sons/beep.mp3')
    tabela = atualizacao_data_tabelas = ultima_atualizacao = None

    def build(self):
        return GUI

    def on_start(self):
        self.root.ids['loginpage'].ids['lojas'].values = self.lojas
        try:
            with open('login.txt', 'r') as arquivo:
                dados = arquivo.read()
            self.id_usuario = dados.split('|')[0]
            self.loja = dados.split('|')[2]
            self.atualizacao_data_tabelas = dados.split('|')[3]
            if self.buscar_login(self.id_usuario,dados.split('|')[1],self.loja):
                self.mudar_tela('coletapage')
            else:
                os.remove('login.txt')
                self.atualizacao_data_tabelas = None

        except:
            pass
        try:
            with open('coleta.txt', 'r') as arquivo:
                dados = arquivo.read()
            dados = reversed(dados.split(','))
            i = 0
            for texto in dados:
                homepage = self.root.ids['coletapage']
                cor, descricao, preco, tamanho = self.conferir_produto(texto)
                homepage.ids['lista_referencias'].add_widget(BannerProduto(codigo=texto, cor=cor, descricao=descricao,
                                                                           preco=preco,tamanho = tamanho))
                i += 1
            self.atualizar_qnt(i)
            homepage.ids['btn_excluir'].disabled = False
            homepage.ids['btn_enviar'].disabled = False
        except Exception as e:
            print(e)
            pass

    def buscar_login(self,login,data,loja):
        link = f'https://appbalanco-27229-default-rtdb.firebaseio.com/{loja}/{login}.json'
        if requests.get(link).json():
            data_cadastro = requests.get(link).json()['data']
            hj = date.today().strftime("%d/%m/%Y")
            if data_cadastro != hj:
                return False
            return True
        else:
            return False

    def btn_camera(self, id_tela):
        homepage = self.root.ids['coletapage']
        texto = homepage.ids['referencia'].text
        if texto!= '':
            self.carregar_lista_referencias(texto)
        else:  # inserted
            self.mudar_tela(id_tela)

    def opcao_loja(self,spinner,text):
        self.loja = text
    def popup(self, *args):
        box = FloatLayout(orientation='vertical')
        pop = Popup(title='Atenção', content=box, size_hint=(None, None), size=(800, 600), auto_dismiss=False)
        sim = Button(text='OK', pos_hint={'right': 1, 'top': 0.35}, size_hint=(1, 0.25), on_release=partial(self.atualizar_tabelas, pop))
        label = Label(text='Favor, Atualizar Tabelas', pos_hint={'right': 1, 'top': 1}, size_hint=(1, 1))
        box.add_widget(sim)
        box.add_widget(label)
        pop.open()

    def popup_excluir(self, *args):
        box = FloatLayout(orientation='vertical')
        pop = Popup(title='Atenção', content=box, size_hint=(None, None), size=(800, 600), auto_dismiss=False)
        sim = Button(text='Sim', pos_hint={'right': 0.45, 'top': 0.35}, size_hint=(0.4, 0.25), on_release=partial(self.excluir_todos, pop))
        nao = Button(text='Não', pos_hint={'right': 0.95, 'top': 0.35}, size_hint=(0.4, 0.25), on_release=partial(self.fechar,pop))
        label = Label(text='Deseja Excluir Todos os Itens?', pos_hint={'right': 1, 'top': 1}, size_hint=(1, 1))
        box.add_widget(sim)
        box.add_widget(nao)
        box.add_widget(label)
        pop.open()

    def fechar(self, pop, *args):
        self.root.ids['coletapage'].ids['btn_enviar'].disabled = False
        pop.dismiss()

    def carregar_lista_referencias(self, texto):
        homepage = self.root.ids['coletapage']
        cor, descricao, preco, tamanho = self.conferir_produto(texto)
        if descricao!= '' and cor!= '' and (tamanho!= '') and (preco!= ''):
            homepage.ids['lista_referencias'].add_widget(BannerProduto(codigo=texto, cor=cor, descricao=descricao,
                                                                       preco=preco,tamanho= tamanho))
            self.atualizar_qnt(1)
            self.bkp_produto(texto)
            homepage.ids['referencia'].text = ''
            homepage.ids['mensagem'].text = ''
            homepage.ids['btn_excluir'].disabled = False
            homepage.ids['btn_enviar'].disabled = False
        else:  # inserted
            self.som_erro.play()
            homepage.ids['mensagem'].text = '[color=#FF0000]Erro: Referencia não encontrada[/color]'

    def incluir_item_camera(self, codigo):
        if self.root.ids['screen_manager'].current != 'coletapage':
            homepage = self.root.ids['coletapage']
            homepage.ids['mensagem'].text = ''
            codigo = codigo.replace('\'', '').replace('b', '')
            if self.is_ean(codigo):
                self.som_beep.play()
                self.root.ids['coletapage'].ids['referencia'].text = codigo
                self.mudar_tela('coletapage')

    def excluir_item(self, item, *args):
        homepage = self.root.ids['coletapage']
        lista_produto = homepage.ids['lista_referencias']
        for produto in list(lista_produto.children):
            if produto.id == item:
                self.excluir_item_bkp(item)
                homepage.ids['lista_referencias'].remove_widget(produto)
                quantidade = int(homepage.ids['quantidade'].text.replace('Qnt.: [color=#000000]', '').replace('[/color]', '')) - 1
                homepage.ids['quantidade'].text = f'Qnt.: [color=#000000]{quantidade}[/color]'
                self.root.ids['camerapage'].ids['quantidade'].text = f'Qnt.: [color=#000000]{quantidade}[/color]'
                break

    def excluir_todos(self, pop, *args):
        homepage = self.root.ids['coletapage']
        lista_produto = homepage.ids['lista_referencias']
        for referencia in list(lista_produto.children):
            homepage.ids['lista_referencias'].remove_widget(referencia)
        try:
            os.remove('coleta.txt')
        except:
            pass
        homepage.ids['quantidade'].text = '[color=#000000]0[/color]'
        self.root.ids['camerapage'].ids['quantidade'].text = 'Qnt.: [color=#000000]0[/color]'
        homepage.ids['btn_excluir'].disabled = True
        self.fechar(pop)

    def enviar_coleta(self):
        coleta = ''
        homepage = self.root.ids['coletapage']
        lista_produto = homepage.ids['lista_referencias']
        try:
            for referencia in list(lista_produto.children):
                coleta += referencia.id + ','
            if len(coleta)!= 0:
                info = f'{{"coleta":"{coleta[:-1]}","leitura":"0"}}'
                link = f'https://appbalanco-27229-default-rtdb.firebaseio.com/{self.loja}/{self.id_usuario}/coletas.json'
                requests.post(link, data=info)
                self.som_envio.play()
                self.popup_excluir()
                homepage.ids['mensagem'].text = '[color=#00FF00]Coleta enviada[/color]'
                homepage.ids['btn_enviar'].disabled = True
            else:  # inserted
                self.som_erro()
                homepage.ids['mensagem'].text = '[color=#FF0000]Não há item a ser enviado[/color]'
        except:
            homepage.ids['mensagem'].text = '[color=#FF0000]Erro ao enviar arquivo, favor tente novamente[/color]'

    def logar(self):
        nome = self.root.ids['loginpage'].ids['nome'].text
        self.loja = self.root.ids['loginpage'].ids['lojas'].text
        if len(nome) >= 4 and self.loja != '':
            data = date.today().strftime("%d/%m/%Y")
            info = f'{{"nome":"{nome}","data":"{data}"}}'
            link = f'https://appbalanco-27229-default-rtdb.firebaseio.com/{self.loja}.json'
            id_usuario = requests.post(link, data=info).json()['name']
            self.id_usuario = id_usuario
            with open('login.txt', 'w') as arquivo:
                arquivo.write(id_usuario + '|'+data+'|'+self.loja)
            self.mudar_tela('coletapage')
        else:  # inserted
            self.root.ids['loginpage'].ids['mensagem_login'].text = ('[color=#FF0000]Erro:[/color] Nome tem que ter mais '
                                                                     'de 3 caracter e loja deve ser selecionada')

    def bkp_produto(self, codigo):
        try:
            with open('coleta.txt', 'r') as arquivo:
                dados = arquivo.read()
            codigo = f'{codigo},{dados}'
        except:
            pass
        with open('coleta.txt', 'w') as arquivo:
            arquivo.write(codigo)

    def excluir_item_bkp(self, codigo):
        with open('coleta.txt', 'r') as arquivo:
            dados = arquivo.read()
        dados = dados.split(',')
        if len(dados) == 1:
            os.remove('coleta.txt')
        else:  # inserted
            with open('coleta.txt', 'r') as arquivo:
                dados = arquivo.read()
            dados = dados.split(',')
            dados.remove(codigo)
            os.remove('coleta.txt')
            dados = str(dados).replace('[', '').replace(']', '').replace('\'', '').replace(' ', '')
            with open('coleta.txt', 'w') as arquivo:
                arquivo.write(dados)

    def mudar_tela(self, id_tela):
        if id_tela == 'historicopage':
            self.listar_coletas('1',id_tela)
        self.root.ids['screen_manager'].current = id_tela
        if id_tela == 'coletapage' and self.ultima_atualizacao == None:
            link = 'https://appbalanco-27229-default-rtdb.firebaseio.com/Tabela/atualizado.json'
            self.ultima_atualizacao = requests.get(link).json()
            if self.ultima_atualizacao!= self.atualizacao_data_tabelas:
                self.popup()

    def listar_coletas(self,status,id_tela):
        self.excluir_listagem(id_tela)
        link = f'https://appbalanco-27229-default-rtdb.firebaseio.com/{self.loja}/{self.id_usuario}.json'
        requisicao_dic = requests.get(link).json()
        qnt_coleta = False
        qnti = 0
        nome = requisicao_dic['nome'].upper()
        for dados in requisicao_dic['coletas']:
            try:
                id_usuario = dados
                qnt = len(requisicao_dic['coletas'][dados]['coleta'].split(','))
                status = requisicao_dic['coletas'][dados]['leitura']

                qnti += qnt
                qnt_coleta = True
                self.root.ids['historicopage'].ids['notificacao'].text = ''
                coletas = 'ola'
                self.root.ids[id_tela].ids['lista_coleta'].add_widget(
                        BannerColeta(codigo=coletas, nome=nome, quantidade=qnt, id_usuario=id_usuario,
                                    status= status,id_tela=id_tela))
            except:
                pass
        self.root.ids['historicopage'].ids['quantidade'].text = f'Qnt.: [color=#000000]{str(qnti)}[/color]'
        if not qnt_coleta:
            self.root.ids['historicopage'].ids['notificacao'].text = '[color=#FF6666]NÃO HÁ COLETAS[/color]'

    def excluir_listagem(self, id_tela):
        for item in list(self.root.ids[id_tela].ids['lista_coleta'].children):
            self.root.ids[id_tela].ids['lista_coleta'].remove_widget(item)

    def limpar_referencia(self):
        self.root.ids['coletapage'].ids['referencia'].text = ''
        self.root.ids['coletapage'].ids['mensagem'].text = ''

    def atualizar_qnt(self, qnt):
        homepage = self.root.ids['coletapage']
        quantidade = int(homepage.ids['quantidade'].text.replace('[color=#000000]', '').replace('[/color]', '')) + qnt
        homepage.ids['quantidade'].text = f'[color=#000000]{quantidade}[/color]'
        self.root.ids['camerapage'].ids['quantidade'].text = f'Qnt.: [color=#000000]{quantidade}[/color]'

    def conferir_produto(self, codigo):
        cor = descricao = preco = tamanho = ''
        try:
            codigo_descricao = codigo[:7]
            codigo_cor = codigo[7:10]
            codigo_tamanho = int(codigo[10:12]) - 1

            if not self.tabela:
                with open('tabela.txt', 'r') as arquivo:
                    self.tabela = arquivo.read().split('\n')
            if int(codigo_tamanho) <= 13:
                tamanho = codigo_tamanho
            for linha  in self.tabela:
                tab_referencia, tab_descricao, tab_preco , tab_cor , tab_tamanho = linha.split('|')
                if int(tab_referencia) == int(codigo_descricao) and tab_cor.split('-')[0] == codigo_cor:
                    cor = tab_cor.split('-')[1]
                    preco = tab_preco
                    descricao = tab_descricao
                    tamanho = tab_tamanho.split('/')[codigo_tamanho]
                    break
        except:
            pass
        return (cor, descricao, preco, tamanho)

    def is_ean(self, ean):
        try:
            err = 0
            even = 0
            odd = 0
            check_bit = ean[len(ean) - 1]
            check_val = ean[:(-1)]
            if len(ean)!= 13:
                return False
            for index, num in enumerate(check_val):
                if index % 2 == 0:
                    even += int(num)
                else:  # inserted
                    odd += int(num)
            if (3 * odd + even + int(check_bit)) % 10 == 0:
                return True
            return False
        except:
            return False


    def atualizar_tabela(self):
        link = 'https://appbalanco-27229-default-rtdb.firebaseio.com/Tabela/Tabela.json'
        dados = requests.get(link).json()
        texto = ''
        for linha in dados:
            tabela_descricao = dados[linha]
        self.tabela_descricao = tabela_descricao
        for linha in tabela_descricao:
            texto += linha + '\n'
        with open('tabela.txt', 'w') as arquivo:
            arquivo.write(texto)

    def atualizar_tabelas(self, pop, *args):
        self.atualizar_tabela()
        link = 'https://appbalanco-27229-default-rtdb.firebaseio.com/Tabela/atualizado.json'
        dados = requests.get(link).json()
        with open('login.txt', 'r') as arquivo:
            texto = arquivo.read().split('|')
            id_login = texto[0]
            data_login = texto[1]
            loja_login = texto[2]
        with open('login.txt', 'w') as arquivo:
            arquivo.write(f'{id_login}|{data_login}|{loja_login}|{dados}')
        self.atualizacao_data_tabelas = dados
        self.fechar(pop)
        self.root.ids['coletapage'].ids['mensagem'].text = '[color=#00FF00]Tabela atualizada[/color]'
MyApp().run()