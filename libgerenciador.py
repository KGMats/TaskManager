import datetime
import calendar
import copy
from typing import List, Optional, Tuple
import json
from dataclasses import dataclass, field
from enum import Enum

class PRIORIDADE(Enum):
    """Níveis de prioridade atribuíveis a uma tarefa."""
    SEM_PRIORIDADE = 0
    BAIXA = 1
    MEDIA = 2
    ALTA = 3

class FREQUENCIA(Enum):
    """Frequencia de uma tarefa recorrente."""
    NENHUMA = 0
    DIARIA = 1
    SEMANAL = 2
    MENSAL = 3
    ANUAL = 4

@dataclass
class Tarefa:
    """
    Representa uma tarefa com atributos como título, nota, data, tags, prioridade,
    frequência e status de conclusão.
    """
    id: int = 0
    titulo: str = ""
    nota: str = ""
    data: datetime.date = field(default_factory=lambda: datetime.date(1970, 1, 1))
    tags: List[str] = field(default_factory=list)
    prioridade: PRIORIDADE = PRIORIDADE.SEM_PRIORIDADE
    repeticao: FREQUENCIA = FREQUENCIA.NENHUMA
    concluida: bool = False

    def to_dict(self):
        return {
            'id': self.id, 'titulo': self.titulo, 'nota': self.nota,
            'data': self.data.isoformat(), 'tags': self.tags,
            'prioridade': self.prioridade.name, 'repeticao': self.repeticao.name,
            'concluida': self.concluida
        }

    @staticmethod
    def from_dict(d):
        return Tarefa(
            id=int(d['id']), titulo=d['titulo'], nota=d['nota'],
            data=datetime.date.fromisoformat(d['data']), tags=d.get('tags', []),
            prioridade=PRIORIDADE[d['prioridade']], repeticao=FREQUENCIA[d['repeticao']],
            concluida=d['concluida']
        )

@dataclass
class ListaDeTarefas:
    """
    Representa uma lista que agrupa várias tarefas.
    """
    id: int = 0
    titulo: str = ""
    tarefas: List[Tarefa] = field(default_factory=list)

    def to_dict(self):
        return {'id': self.id, 'titulo': self.titulo, 'tarefas': [t.to_dict() for t in self.tarefas]}

    @staticmethod
    def from_dict(d):
        return ListaDeTarefas(
            id=int(d['id']), titulo=d['titulo'],
            tarefas=[Tarefa.from_dict(t_dict) for t_dict in d['tarefas']]
        )

class GerenciadorTarefas:
    """
    Classe responsável por gerenciar todas as listas de tarefas, sendo
    responsavel pela criacao, edicao e remocao de tarefas e de listas
    de tarefas. Basicamente e a principal classe desse projeto.
    Foi pensado para ter um nivel de abstracao que permita ser
    reutilizado em outros projetos no futuro, sem necessidade de
    estar integrado com o restante do sistema.
    """
    def __init__(self):
        self.database_path = "userdata.json"
        self._proximo_id_lista = 1
        self._proximo_id_tarefa = 1
        self.listas: List[ListaDeTarefas] = self.load_database()

    def load_database(self) -> List[ListaDeTarefas]:
        try:
            with open(self.database_path, 'r') as f:
                data = json.load(f)
                listas = [ListaDeTarefas.from_dict(d) for d in data]
                if listas:
                    max_lista_id = max(l.id for l in listas) if listas else 0
                    self._proximo_id_lista = max_lista_id + 1
                    
                    all_tasks = [t for l in listas for t in l.tarefas]
                    max_task_id = max(t.id for t in all_tasks) if all_tasks else 0
                    self._proximo_id_tarefa = max_task_id + 1
                return listas
        except (FileNotFoundError, json.JSONDecodeError):
            # Cria uma lista, caso nao existam listas salvas
            lista_padrao = ListaDeTarefas(id=self._proximo_id_lista, titulo='Minha lista de tarefas')
            self._proximo_id_lista += 1
            return [lista_padrao]

    def save_database(self):
        with open(self.database_path, 'w') as fp:
            json.dump([lista.to_dict() for lista in self.listas], fp, indent=4)

    def criar_lista_de_tarefas(self, titulo: str) -> Optional[ListaDeTarefas]:
        if any(lista.titulo.lower() == titulo.lower() for lista in self.listas):
            return None
        nova_lista = ListaDeTarefas(id=self._proximo_id_lista, titulo=titulo)
        self._proximo_id_lista += 1
        self.listas.append(nova_lista)
        return nova_lista

    def editar_lista_de_tarefas(self, lista_id: int, novo_titulo: str) -> bool:
        if any(l.id != lista_id and l.titulo.lower() == novo_titulo.lower() for l in self.listas):
            return False
        target_lista = next((l for l in self.listas if l.id == lista_id), None)
        if target_lista:
            target_lista.titulo = novo_titulo
            return True
        return False

    def remover_lista_de_tarefas(self, lista_id: int) -> bool:
        if len(self.listas) <= 1:
            return False
        lista_original_len = len(self.listas)
        self.listas = [lista for lista in self.listas if lista.id != lista_id]
        return len(self.listas) < lista_original_len

    def get_todas_listas(self) -> List[ListaDeTarefas]:
        return self.listas

    def criar_tarefa(self, lista_id: int, **kwargs) -> Optional[Tarefa]:
        target_lista = next((l for l in self.listas if l.id == lista_id), None)
        if not target_lista: return None
        
        kwargs['id'] = self._proximo_id_tarefa
        self._proximo_id_tarefa += 1
        
        tarefa = Tarefa(**kwargs)
        if isinstance(tarefa.data, str): tarefa.data = datetime.date.fromisoformat(tarefa.data)
        target_lista.tarefas.append(tarefa)
        return tarefa
        
    def editar_tarefa(self, tarefa: Tarefa, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                if key == 'data' and isinstance(value, str):
                    value = datetime.date.fromisoformat(value)
                setattr(tarefa, key, value)
    
    def mover_tarefa(self, tarefa_id: int, lista_origem_id: int, lista_destino_id: int) -> bool:
        if lista_origem_id == lista_destino_id: return True
        lista_origem = next((l for l in self.listas if l.id == lista_origem_id), None)
        lista_destino = next((l for l in self.listas if l.id == lista_destino_id), None)
        if not lista_origem or not lista_destino: return False
        tarefa_para_mover = next((t for t in lista_origem.tarefas if t.id == tarefa_id), None)
        if not tarefa_para_mover: return False
        lista_origem.tarefas.remove(tarefa_para_mover)
        lista_destino.tarefas.append(tarefa_para_mover)
        return True

    def remover_tarefa(self, lista_id: int, tarefa_id: int):
        target_lista = next((l for l in self.listas if l.id == lista_id), None)
        if target_lista:
            target_lista.tarefas = [t for t in target_lista.tarefas if t.id != tarefa_id]

    def remover_tarefas_concluidas(self):
        for lista in self.listas:
            lista.tarefas = [t for t in lista.tarefas if not t.concluida]

    def toggle_tarefa_concluida(self, lista_id: int, tarefa_id: int) -> Optional[Tarefa]:
        target_lista = next((l for l in self.listas if l.id == lista_id), None)
        if not target_lista: return None
        target_tarefa = next((t for t in target_lista.tarefas if t.id == tarefa_id), None)
        if not target_tarefa: return None

        if not target_tarefa.concluida:
            target_tarefa.concluida = True
            if target_tarefa.repeticao != FREQUENCIA.NENHUMA:
                nova_tarefa = copy.copy(target_tarefa)
                nova_tarefa.id, nova_tarefa.concluida = self._proximo_id_tarefa, False
                self._proximo_id_tarefa += 1
                data_base = target_tarefa.data if target_tarefa.data != datetime.date(1970, 1, 1) else datetime.date.today()
                if target_tarefa.repeticao == FREQUENCIA.DIARIA: nova_tarefa.data = data_base + datetime.timedelta(days=1)
                elif target_tarefa.repeticao == FREQUENCIA.SEMANAL: nova_tarefa.data = data_base + datetime.timedelta(days=7)
                elif target_tarefa.repeticao == FREQUENCIA.MENSAL:
                    y, m = (data_base.year, data_base.month + 1) if data_base.month < 12 else (data_base.year + 1, 1)
                    d = min(data_base.day, calendar.monthrange(y, m)[1])
                    nova_tarefa.data = datetime.date(y, m, d)
                elif target_tarefa.repeticao == FREQUENCIA.ANUAL:
                    try: nova_tarefa.data = data_base.replace(year=data_base.year + 1)
                    except ValueError: nova_tarefa.data = data_base.replace(year=data_base.year + 1, day=28)
                target_tarefa.repeticao = FREQUENCIA.NENHUMA
                target_lista.tarefas.append(nova_tarefa)
                return nova_tarefa
        else:
            target_tarefa.concluida = False
        return None

    def buscar_tarefas(self, termo_busca: str) -> list:
        termo = termo_busca.lower()
        resultados = []
        if not termo: return resultados
        for lista in self.listas:
            for tarefa in lista.tarefas:
                encontrado = (termo in tarefa.titulo.lower() or
                              termo in tarefa.nota.lower() or
                              any(termo in tag.lower() for tag in tarefa.tags))
                if encontrado:
                    resultados.append((tarefa, lista))
        return resultados

    def get_visualizacao_tarefas(self, filtro_tempo: str, filtro_status: str, ordenacao: str,
                                 contexto_lista: Optional[ListaDeTarefas] = None, contexto_tag: Optional[str] = None) -> list:
        tarefas_brutas = []
        if contexto_lista:
            for tarefa in contexto_lista.tarefas: tarefas_brutas.append((tarefa, contexto_lista))
        else:
            for lista in self.listas:
                for tarefa in lista.tarefas: tarefas_brutas.append((tarefa, lista))
        
        resultados = tarefas_brutas
        if contexto_tag:
            resultados = [(t, l) for t, l in resultados if contexto_tag.lower() in [tag.lower() for tag in t.tags]]
        if filtro_status == "INCOMPLETAS": resultados = [(t, l) for t, l in resultados if not t.concluida]
        elif filtro_status == "COMPLETAS": resultados = [(t, l) for t, l in resultados if t.concluida]

        hoje = datetime.date.today()
        if filtro_tempo == "HOJE":
            resultados = [(t, l) for t, l in resultados if t.data <= hoje and t.data != datetime.date(1970, 1, 1)]
        elif filtro_tempo == "SETE_DIAS":
            data_limite = hoje + datetime.timedelta(days=7)
            resultados = [(t, l) for t, l in resultados if t.data <= data_limite and t.data != datetime.date(1970, 1, 1)]

        data_final = datetime.date.max
        if ordenacao == "DATA":
            resultados.sort(key=lambda i: (i[0].data if i[0].data != datetime.date(1970,1,1) else data_final, -i[0].prioridade.value, i[1].titulo))
        elif ordenacao == "PRIORIDADE":
            resultados.sort(key=lambda i: (-i[0].prioridade.value, i[0].data if i[0].data != datetime.date(1970,1,1) else data_final, i[1].titulo))
            
        return resultados

