from game_data import MONSTER_DATA, ATTACK_DATA
from random import randint

class Monster:
    """
    Classe que representa a Lógica e os Dados de um monstro.
    Gerencia HP, Energia, Status, XP e Cálculos de Dano.
    Não lida com imagens ou desenhos.
    """
    def __init__(self, name, level):
        self.name, self.level = name, level
        self.paused = False # Se True, o monstro para de ganhar iniciativa (pausa no turno)

        # --- INICIALIZAÇÃO DE ESTATÍSTICAS ---
        # Busca os dados base no arquivo game_data.py usando o nome do monstro
        self.element = MONSTER_DATA[name]['stats']['element']
        self.base_stats = MONSTER_DATA[name]['stats']

        # Calcula os atributos atuais baseados no nível.
        # A fórmula é simples: Atributo Base * Nível Atual.
        self.health = self.base_stats['max_health'] * self.level
        self.energy = self.base_stats['max_energy'] * self.level
        
        # Iniciativa começa em 0 e enche até 100 para o monstro poder atacar (sistema ATB)
        self.initiative = 0
        
        self.abilities = MONSTER_DATA[name]['abilities']
        self.defending = False # Flag para saber se o monstro escolheu "Defender" no turno

        # --- SISTEMA DE NÍVEL ---
        self.xp = 0
        # Define quanto XP é necessário para o próximo nível (Nível * 150)
        self.level_up = self.level * 150
        # Guarda o nome da próxima evolução (ou None se não tiver)
        self.evolution = MONSTER_DATA[self.name]['evolve']

    def __repr__(self):
        # Representação em string para debug (aparece no print do console)
        return f'monster: {self.name}, lvl: {self.level}'

    def get_stat(self, stat):
        """
        Retorna o valor atual de um atributo específico (Ataque, Defesa, etc)
        multiplicado pelo nível do monstro.
        """
        return self.base_stats[stat] * self.level

    def get_stats(self):
        """
        Retorna um dicionário com TODOS os atributos calculados para o nível atual.
        Útil para preencher a UI de detalhes.
        """
        return {
            'health': self.get_stat('max_health'),
            'energy': self.get_stat('max_energy'),
            'attack': self.get_stat('attack'),
            'defense': self.get_stat('defense'),
            'speed': self.get_stat('speed'),
            'recovery': self.get_stat('recovery'),
        }

    def get_abilities(self, all=True):
        """
        Retorna a lista de habilidades que o monstro pode usar.
        all=True: Retorna todas as habilidades desbloqueadas pelo nível.
        all=False: Retorna apenas as desbloqueadas QUE o monstro tem energia para pagar.
        """
        if all:
            # Lista de compreensão: Pega habilidade se Nível do Monstro >= Nível Desbloqueio
            return [ability for lvl, ability in self.abilities.items() if self.level >= lvl]
        else:
            # Filtro adicional: Verifica se o Custo (ATTACK_DATA) < Energia Atual
            return [ability for lvl, ability in self.abilities.items() if self.level >= lvl and ATTACK_DATA[ability]['cost'] < self.energy]

    def get_info(self):
        """
        Retorna tuplas (Valor Atual, Valor Máximo) para desenhar as barras na UI de batalha.
        Retorna: Vida, Energia e Iniciativa.
        """
        return (
            (self.health, self.get_stat('max_health')),
            (self.energy, self.get_stat('max_energy')),
            (self.initiative, 100)
            )

    def reduce_energy(self, attack):
        # Deduz o custo da habilidade da energia atual
        self.energy -= ATTACK_DATA[attack]['cost']

    def get_base_damage(self, attack):
        # Calcula o dano bruto: Ataque do Monstro * Multiplicador da Habilidade
        return self.get_stat('attack') * ATTACK_DATA[attack]['amount']

    def update_xp(self, amount):
        """
        Adiciona XP e verifica se o monstro subiu de nível.
        """
        # Se a XP atual + ganho for MENOR que o necessário para upar
        if self.level_up - self.xp > amount:
            self.xp += amount
        else:
            # LEVEL UP!
            self.level += 1
            # O XP excedente é transportado para o próximo nível
            self.xp = amount - (self.level_up - self.xp)
            # Recalcula a meta de XP para o novo nível
            self.level_up = self.level * 150

    def stat_limiter(self):
        """
        Garante que Vida e Energia nunca fiquem negativos ou acima do máximo.
        Clamp (Grampo) de valores.
        """
        self.health = max(0, min(self.health, self.get_stat('max_health')))
        self.energy = max(0, min(self.energy, self.get_stat('max_energy')))

    def update(self, dt):
        """
        Atualiza o estado do monstro a cada frame.
        """
        # Garante que os stats estão dentro dos limites
        self.stat_limiter()
        
        # Lógica de BATALHA POR TEMPO (Active Time Battle - ATB)
        # Se não estiver pausado (turno de alguém), a barra de iniciativa enche
        # baseada na velocidade do monstro.
        if not self.paused:
            self.initiative += self.get_stat('speed') * dt