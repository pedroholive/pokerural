import pygame
import sys


class TelaTitulo:
    def __init__(self, surface):
        self.display_surface = surface

        # --- 1. CARREGAMENTO DA IMAGEM ---
        # Tenta achar a imagem na pasta assets ou na raiz
        try:
            self.image = pygame.image.load("assets/tela_titulo.png").convert()
        except FileNotFoundError:
            try:
                self.image = pygame.image.load("tela_titulo.png").convert()
            except FileNotFoundError:
                print("ERRO CRÍTICO: Imagem 'tela_titulo.png' não encontrada!")
                print("Verifique se o nome está certo e se é png mesmo.")
                sys.exit()  # Fecha se não tiver imagem

        # Ajusta a imagem para o tamanho da janela
        largura = self.display_surface.get_width()
        altura = self.display_surface.get_height()
        self.image = pygame.transform.scale(self.image, (largura, altura))

        # --- 2. CONFIGURAÇÃO DA FONTE ---
        tamanho_fonte = 40
        try:
            self.fonte = pygame.font.Font("assets/fonte.ttf", tamanho_fonte)
        except FileNotFoundError:
            print("AVISO: Fonte não encontrada. Usando padrão.")
            self.fonte = pygame.font.Font(None, 60)

        # Prepara os textos (Branco e Preto para a borda)
        self.texto_principal = self.fonte.render("PRESS ANY KEY TO START", True, "White")
        self.texto_borda = self.fonte.render("PRESS ANY KEY TO START", True, "Black")

        # Centraliza
        self.texto_rect = self.texto_principal.get_rect(center=(largura / 2, altura - 80))

        # Variáveis de controle
        self.mostrar_texto = True
        self.ultimo_pisque = 0
        self.intervalo = 800
        self.ativo = True

    # --- O PULO DO GATO: A função run está alinhada na esquerda! ---
    def run(self):
        while self.ativo:
            # 1. Checa se apertou algo
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    print("Tecla pressionada! Saindo do menu...")
                    self.ativo = False  # Isso quebra o loop e volta pro main.py

            # 2. Lógica do Pisca
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - self.ultimo_pisque > self.intervalo:
                self.mostrar_texto = not self.mostrar_texto
                self.ultimo_pisque = tempo_atual

            # 3. Desenha tudo
            self.display_surface.blit(self.image, (0, 0))

            if self.mostrar_texto:
                # Desenha a borda preta (deslocada)
                offset = 3
                self.display_surface.blit(self.texto_borda, (self.texto_rect.x - offset, self.texto_rect.y))
                self.display_surface.blit(self.texto_borda, (self.texto_rect.x + offset, self.texto_rect.y))
                self.display_surface.blit(self.texto_borda, (self.texto_rect.x, self.texto_rect.y - offset))
                self.display_surface.blit(self.texto_borda, (self.texto_rect.x, self.texto_rect.y + offset))

                # Desenha o texto branco
                self.display_surface.blit(self.texto_principal, self.texto_rect)

            pygame.display.update()