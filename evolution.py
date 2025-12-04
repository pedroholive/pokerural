from settings import * 
from tempo import Tempo

class Evolution:
    """
    Gerencia a sequência de animação de evolução.
    Controla a transição visual, efeitos de luz, texto e a troca de sprites.
    """
    def __init__(self, frames, start_monster, end_monster, font, end_evolution, star_frames):
        # Obtém a referência da tela principal do jogo para desenhar
        self.display_surface = pygame.display.get_surface()
        
        # Carrega e dobra o tamanho (scale2x) da imagem do monstro atual e da sua evolução
        # Usa o frame 0 da animação 'idle' (parado) como referência
        self.start_monster_surf = pygame.transform.scale2x(frames[start_monster]['idle'][0])
        self.end_monster_surf = pygame.transform.scale2x(frames[end_monster]['idle'][0])
        
        # Define os temporizadores da cena:
        # 'start': Um atraso inicial de 800ms antes da animação começar.
        # 'end': Um atraso de 1800ms após a evolução terminar para fechar a tela.
        self.timers = {
            'start': Tempo(800, autostart = True),
            'end': Tempo(1800, func = end_evolution)
        }

        # Configuração da animação de estrelas (efeito de sucesso)
        # Cria uma lista onde cada frame da estrela é dobrado de tamanho
        self.star_frames = [pygame.transform.scale2x(frame) for frame in star_frames]
        self.frame_index = 0

        # Cria uma superfície preta semi-transparente para escurecer o fundo do jogo
        self.tint_surf = pygame.Surface(self.display_surface.get_size())
        self.tint_surf.set_alpha(200) # 0 é transparente, 255 é sólido. 200 é bem escuro.

        # Configuração do efeito de "Flash Branco" (whitening)
        # 1. Cria uma máscara (mask) da silhueta do monstro.
        # 2. Converte essa máscara de volta para uma superfície (imagem sólida).
        self.start_monster_surf_white = pygame.mask.from_surface(self.start_monster_surf).to_surface()
        # 3. Define que a cor de fundo da máscara será transparente (remove o retângulo preto padrão).
        self.start_monster_surf_white.set_colorkey('black')
        
        # Variáveis para controlar a intensidade do branco
        self.tint_amount, self.tint_speed = 0, 80 # Começa transparente (0) e aumenta 80 por segundo
        self.start_monster_surf_white.set_alpha(self.tint_amount)

        # Renderiza os textos que aparecerão na tela
        self.start_text_surf = font.render(f'{start_monster} is evolving', False, COLORS['black'])
        self.end_text_surf = font.render(f'{start_monster} evolved into {end_monster}', False, COLORS['black'])

    def display_stars(self, dt):
        """
        Gerencia a animação das estrelas explodindo após a evolução.
        """
        # Incrementa o índice do frame baseado no tempo (20 quadros por segundo)
        self.frame_index += 20 * dt
        
        # Enquanto houver frames de animação da estrela para mostrar:
        if self.frame_index < len(self.star_frames):
            frame = self.star_frames[int(self.frame_index)]
            # Centraliza a estrela na tela
            rect = frame.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
            self.display_surface.blit(frame, rect)

    def update(self, dt):
        """
        Loop principal da animação de evolução.
        dt: Delta Time (tempo desde o último frame) para suavizar movimentos.
        """
        # Atualiza os temporizadores internos
        for timer in self.timers.values():
            timer.update()

        # A lógica só começa quando o timer inicial ('start') termina
        if not self.timers['start'].active:
            
            # 1. Desenha o fundo escuro sobre o jogo
            self.display_surface.blit(self.tint_surf, (0,0))
            
            # ESTÁGIO 1: O monstro antigo brilha até ficar branco
            if self.tint_amount < 255:
                # Posiciona e desenha o monstro original no centro
                rect = self.start_monster_surf.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
                self.display_surface.blit(self.start_monster_surf, rect)

                # Aumenta a opacidade da silhueta branca
                self.tint_amount += self.tint_speed * dt
                self.start_monster_surf_white.set_alpha(self.tint_amount)
                
                # Desenha a silhueta branca POR CIMA do monstro original
                self.display_surface.blit(self.start_monster_surf_white, rect)

                # Desenha o texto "X está evoluindo" com uma caixa branca atrás
                text_rect = self.start_text_surf.get_frect(midtop = rect.midbottom + vector(0,20))
                pygame.draw.rect(self.display_surface, COLORS['white'], text_rect.inflate(20,20), 0, 5)
                self.display_surface.blit(self.start_text_surf, text_rect)

            # ESTÁGIO 2: Troca para o novo monstro
            else:
                # Posiciona e desenha o NOVO monstro
                rect = self.end_monster_surf.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
                self.display_surface.blit(self.end_monster_surf, rect)
                
                # Desenha o texto "X evoluiu para Y"
                text_rect = self.end_text_surf.get_frect(midtop = rect.midbottom + vector(0,20))
                pygame.draw.rect(self.display_surface, COLORS['white'], text_rect.inflate(20,20), 0, 5)
                self.display_surface.blit(self.end_text_surf, text_rect)
                
                # Roda a animação das estrelas
                self.display_stars(dt)

                # Inicia o timer final para encerrar a cena, se ainda não estiver rodando
                if not self.timers['end'].active:
                    self.timers['end'].activate()