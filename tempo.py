from pygame.time import get_ticks  # Importa a função que retorna o tempo em milissegundos desde que o jogo iniciou

class Tempo:
    """
    Uma classe de temporizador personalizada para gerenciar eventos baseados em tempo no jogo.
    Útil para: Cooldown de ataques, duração de efeitos, atrasos de animação, etc.
    """
    def __init__(self, duration, repeat = False, autostart = False, func = None):
        # Configurações iniciais do timer
        self.duration = duration  # Duração do timer em milissegundos
        self.start_time = 0       # Armazena o momento exato (timestamp) em que o timer começou
        self.active = False       # Flag para saber se o timer está rodando ou parado
        self.repeat = repeat      # Se True, o timer reinicia automaticamente quando acaba
        self.func = func          # Uma função (callback) opcional para executar quando o tempo acabar
        
        # Se autostart for True, inicia o timer imediatamente ao criar o objeto
        if autostart:
            self.activate()

    def activate(self):
        """
        Inicia ou reinicia o timer.
        """
        self.active = True
        # Captura o momento atual (em ms) para usar como ponto de partida
        self.start_time = get_ticks()

    def deactivate(self):
        """
        Para o timer e reseta o estado.
        Se 'repeat' estiver ativo, ele reinicia o ciclo.
        """
        self.active = False
        self.start_time = 0
        
        # Lógica de repetição: Se for um timer cíclico, ativa novamente assim que terminar
        if self.repeat:
            self.activate()

    def update(self):
        """
        Verifica a cada frame se o tempo já acabou.
        Deve ser chamado dentro do loop principal do jogo ou no update da entidade.
        """
        # Só executa a lógica se o timer estiver ativo
        if self.active:
            # Pega o tempo atual
            current_time = get_ticks()
            
            # Matemática do tempo: Se (Agora - Início) for maior ou igual a Duração...
            if current_time - self.start_time >= self.duration:
                # Se houver uma função configurada, executa ela agora
                if self.func: 
                    self.func()
                
                # Desativa (ou reinicia se tiver repeat)
                self.deactivate()