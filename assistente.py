"""Interface de terminal, histórico, indicadores e exportação CSV."""

import csv
import json
import re
import time
from datetime import datetime
from pathlib import Path


CAMPOS_ATENDIMENTO = [
    "data",
    "origem",
    "pergunta",
    "orientacao_id",
    "encontrou",
    "ajudou",
    "tentativas",
    "tempo_segundos",
]


class Assistente:
    """Conversa com o cidadão e usa uma BaseConhecimento por composição."""

    def __init__(self, nome, base, diretorio_dados=None):
        self.nome = nome
        self.base = base
        self.diretorio_dados = Path(diretorio_dados or (Path(__file__).resolve().parent / "data"))
        self.diretorio_dados.mkdir(parents=True, exist_ok=True)
        self.caminho_historico = self.diretorio_dados / "historico.json"
        self.caminho_csv = self.diretorio_dados / "atendimentos.csv"
        self.caminho_facilidade = self.diretorio_dados / "avaliacoes_facilidade.json"
        self.historico = self._carregar_lista_json(self.caminho_historico, "histórico")
        self.avaliacoes_facilidade = self._carregar_lista_json(
            self.caminho_facilidade, "avaliações de facilidade"
        )

    @staticmethod
    def _carregar_lista_json(caminho, descricao):
        if not caminho.exists():
            return []
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
            if isinstance(dados, list):
                return [registro for registro in dados if isinstance(registro, dict)]
            print(f"Aviso: o arquivo de {descricao} não contém uma lista. Será iniciado vazio.")
        except (OSError, json.JSONDecodeError, TypeError) as erro:
            print(f"Aviso: o arquivo de {descricao} não pôde ser lido ({erro}). Será iniciado vazio.")
        return []

    @staticmethod
    def _salvar_json(caminho, dados):
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(
            json.dumps(dados, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def contem_dado_pessoal(texto):
        """Bloqueia e descarta consultas com @ ou oito ou mais dígitos."""
        quantidade_digitos = len(re.findall(r"\d", texto))
        return "@" in texto or quantidade_digitos >= 8

    @staticmethod
    def _perguntar_sn(mensagem):
        """Retorna True/False; 0 permite voltar sem forçar uma resposta."""
        while True:
            resposta = input(mensagem).strip().lower()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            if resposta == "0":
                return None
            print("Entrada inválida. Digite s, n ou 0 para voltar.")

    def _registrar(self, origem, pergunta, orientacao_id, encontrou, ajudou, tentativas, inicio):
        atendimento = {
            "data": datetime.now().isoformat(timespec="seconds"),
            "origem": origem,
            "pergunta": pergunta,
            "orientacao_id": orientacao_id,
            "encontrou": bool(encontrou),
            "ajudou": ajudou if isinstance(ajudou, bool) else None,
            "tentativas": max(0, int(tentativas)),
            "tempo_segundos": round(time.time() - inicio, 1),
        }
        self.historico.append(atendimento)
        try:
            self._salvar_json(self.caminho_historico, self.historico)
        except OSError as erro:
            print(f"Aviso: não foi possível gravar o histórico ({erro}).")
        caminho_csv = self.exportar_csv()
        if caminho_csv is None:
            print("Aviso: o atendimento foi mantido em memória, mas o CSV não pôde ser atualizado.")
        return atendimento

    def _mostrar_nao_encontrada(self):
        print("\nNão encontrei uma orientação com confiança suficiente na base atual.")
        categorias = self.base.categorias()
        if categorias:
            print("Você pode tentar outras palavras ou navegar por estas categorias:")
            for categoria in categorias:
                print(f"  - {categoria}")
        else:
            print("A base de conhecimento está indisponível ou vazia neste momento.")
        print("Aviso: este assistente não é canal oficial.")

    def _exibir_resultados(self, resultados):
        pontos, orientacao = resultados[0]
        if pontos >= 6:
            confianca = "ALTA"
        elif pontos >= 3:
            confianca = "MÉDIA"
        else:
            self._mostrar_nao_encontrada()
            return None, 0

        print(f"\nConfiança da resposta: {confianca} ({pontos} pontos)")
        orientacao.exibir()

        alternativas = []
        ids_adicionados = {orientacao.id}
        for pontos_alternativa, alternativa in resultados[1:]:
            if pontos_alternativa >= 3 and alternativa.id not in ids_adicionados:
                alternativas.append((pontos_alternativa, alternativa))
                ids_adicionados.add(alternativa.id)
            if len(alternativas) == 2:
                break

        if alternativas:
            print("\nOutras orientações que podem ajudar:")
            for pontos_alternativa, alternativa in alternativas:
                print(f"  - {alternativa.titulo} [{alternativa.categoria}] ({pontos_alternativa} pontos)")
        return orientacao, pontos

    def perguntar(self):
        """Atende uma dúvida livre; reformulações contam como tentativas do mesmo atendimento."""
        inicio = time.time()
        pergunta_inicial = ""
        tentativas = 0
        melhor_orientacao = None
        melhor_pontuacao = 0
        encontrou_alguma = False
        ajudou = None

        while True:
            try:
                pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()
            except EOFError:
                pergunta = "0"

            if pergunta == "0":
                if tentativas > 0:
                    self._registrar(
                        "pergunta", pergunta_inicial, 
                        melhor_orientacao.id if melhor_orientacao else None,
                        encontrou_alguma, ajudou, tentativas, inicio,
                    )
                    print("Atendimento encerrado.")
                return

            if not pergunta:
                print("A pergunta não pode ficar vazia. Tente novamente.")
                continue

            if self.contem_dado_pessoal(pergunta):
                print("Atenção: não digite CPF, telefone, e-mail ou sequências com 8 ou mais dígitos.")
                print("Essa entrada foi recusada e não será registrada. Reescreva a dúvida sem dados pessoais.")
                continue

            tentativas += 1
            if not pergunta_inicial:
                pergunta_inicial = pergunta

            resultados = self.base.buscar(pergunta)
            if resultados and resultados[0][0] >= 3:
                orientacao, pontos = self._exibir_resultados(resultados)
                encontrou_alguma = True
                if orientacao is not None and pontos > melhor_pontuacao:
                    melhor_orientacao = orientacao
                    melhor_pontuacao = pontos
                resolvida = self._perguntar_sn("Essa orientação resolveu sua dúvida? (s/n; 0 para voltar): ")
                if resolvida is True:
                    ajudou = True
                    break
                if resolvida is None:
                    ajudou = None
                    break
                ajudou = False
                tentar_novamente = self._perguntar_sn(
                    "Deseja reformular a dúvida e tentar novamente? (s/n; 0 para voltar): "
                )
                if tentar_novamente is True:
                    continue
                if tentar_novamente is None:
                    ajudou = None
                break

            self._mostrar_nao_encontrada()
            tentar_novamente = self._perguntar_sn(
                "Deseja tentar outra forma de perguntar? (s/n; 0 para voltar): "
            )
            if tentar_novamente is True:
                continue
            if tentar_novamente is False:
                ajudou = False
            break

        self._registrar(
            "pergunta",
            pergunta_inicial,
            melhor_orientacao.id if melhor_orientacao else None,
            encontrou_alguma,
            ajudou,
            tentativas,
            inicio,
        )
        print("Atendimento registrado sem nome ou contato do usuário.")

    def navegar(self):
        """Permite navegar por categoria e selecionar uma orientação numerada."""
        categorias = self.base.categorias()
        if not categorias:
            print("Não há categorias disponíveis. Confira data/base_conhecimento.json.")
            print("Aviso: este assistente não é canal oficial.")
            return

        while True:
            print("\n=== Categorias ===")
            for indice, categoria in enumerate(categorias, start=1):
                print(f"[{indice}] {categoria}")
            print("[0] Voltar ao menu principal")
            opcao = input("Escolha uma categoria: ").strip()
            if opcao == "0":
                return
            if not opcao.isdigit() or not (1 <= int(opcao) <= len(categorias)):
                print("Opção inválida. Escolha um número da lista.")
                continue

            categoria = categorias[int(opcao) - 1]
            orientacoes = self.base.por_categoria(categoria)
            while True:
                print(f"\n=== {categoria} ===")
                for indice, orientacao in enumerate(orientacoes, start=1):
                    print(f"[{indice}] {orientacao.titulo}")
                print("[0] Voltar às categorias")
                escolha = input("Escolha uma orientação: ").strip()
                if escolha == "0":
                    break
                if not escolha.isdigit() or not (1 <= int(escolha) <= len(orientacoes)):
                    print("Opção inválida. Escolha um número da lista.")
                    continue

                orientacao = orientacoes[int(escolha) - 1]
                inicio = time.time()
                orientacao.exibir()
                ajudou = self._perguntar_sn(
                    "Essa orientação resolveu sua dúvida? (s/n; 0 para voltar): "
                )
                self._registrar(
                    "categoria",
                    f"Categoria: {categoria} — {orientacao.titulo}",
                    orientacao.id,
                    True,
                    ajudou,
                    1,
                    inicio,
                )
                if ajudou is True:
                    print("Obrigado pelo retorno!")
                elif ajudou is False:
                    print("Obrigado. Essa dúvida será considerada sem solução confirmada.")
                else:
                    # O 0 na pergunta de avaliação volta à tela anterior (lista de categorias).
                    break
                # Após exibir uma orientação, retorna à lista para permitir outra escolha.

    def exportar_csv(self):
        """Exporta histórico com csv.DictWriter, inclusive quando ainda não há atendimentos."""
        try:
            self.caminho_csv.parent.mkdir(parents=True, exist_ok=True)
            with self.caminho_csv.open("w", newline="", encoding="utf-8-sig") as arquivo_csv:
                escritor = csv.DictWriter(arquivo_csv, fieldnames=CAMPOS_ATENDIMENTO, extrasaction="ignore")
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow(atendimento)
            return self.caminho_csv
        except (OSError, csv.Error) as erro:
            print(f"Aviso: erro ao exportar CSV ({erro}).")
            return None

    def indicadores(self):
        """Calcula e apresenta os indicadores definidos no enunciado."""
        total = len(self.historico)
        print("\n=== Indicadores de atendimento ===")
        print(f"Total de atendimentos: {total}")

        if total == 0:
            print("Resposta encontrada: sem dados")
            print("Taxa de acerto (ajudou): sem dados")
            print("Tempo médio para encontrar: sem dados")
            print("Tentativas por atendimento: sem dados")
        else:
            encontrados = sum(1 for item in self.historico if item.get("encontrou") is True)
            taxa_encontrada = encontrados / total * 100
            resultados_conhecidos = [item for item in self.historico if isinstance(item.get("ajudou"), bool)]
            resolvidos = sum(1 for item in resultados_conhecidos if item.get("ajudou") is True)
            if resultados_conhecidos:
                taxa_acerto = resolvidos / len(resultados_conhecidos) * 100
                print(f"Taxa de acerto (ajudou): {taxa_acerto:.1f}%")
            else:
                print("Taxa de acerto (ajudou): sem avaliações")
            tempo_medio = sum(float(item.get("tempo_segundos", 0)) for item in self.historico) / total
            tentativas_media = sum(int(item.get("tentativas", 0)) for item in self.historico) / total
            print(f"Resposta encontrada: {taxa_encontrada:.1f}%")
            print(f"Tempo médio para encontrar: {tempo_medio:.1f} segundos")
            print(f"Tentativas por atendimento: {tentativas_media:.2f}")

        notas = [item.get("nota") for item in self.avaliacoes_facilidade if isinstance(item.get("nota"), int) and 1 <= item["nota"] <= 5]
        if notas:
            print(f"Facilidade de uso (1 a 5): {sum(notas) / len(notas):.2f} (média de {len(notas)} avaliações)")
        else:
            print("Facilidade de uso (1 a 5): sem avaliações")

        sem_solucao = [
            item for item in self.historico
            if item.get("encontrou") is not True or item.get("ajudou") is not True
        ]
        print("Dúvidas sem solução confirmada:")
        if not sem_solucao:
            print("  - Nenhuma registrada.")
        else:
            for item in sem_solucao:
                status = "orientação não encontrada" if not item.get("encontrou") else "orientação não confirmou solução"
                print(f"  - {item.get('pergunta', '(pergunta ausente)')} [{status}]")

    def avaliar_facilidade(self):
        """Pede nota de 1 a 5 ao sair; 0 permite pular a avaliação."""
        while True:
            nota = input("Antes de sair, avalie a facilidade de uso de 1 a 5 (0 para pular): ").strip()
            if nota == "0":
                print("Avaliação não registrada.")
                return
            if nota.isdigit() and 1 <= int(nota) <= 5:
                registro = {"data": datetime.now().isoformat(timespec="seconds"), "nota": int(nota)}
                self.avaliacoes_facilidade.append(registro)
                try:
                    self._salvar_json(self.caminho_facilidade, self.avaliacoes_facilidade)
                    print("Obrigado pela avaliação!")
                except OSError as erro:
                    print(f"Aviso: não foi possível salvar a avaliação ({erro}).")
                return
            print("Nota inválida. Digite um número de 1 a 5 ou 0 para pular.")

    def executar(self):
        """Loop principal de terminal; entradas inválidas nunca encerram o programa."""
        while True:
            print(f"\n=== {self.nome} ===")
            print("Orientação simples para a pessoa idosa")
            print("[1] Fazer uma pergunta")
            print("[2] Navegar por categorias")
            print("[3] Ver indicadores")
            print("[0] Sair")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                self.perguntar()
            elif opcao == "2":
                self.navegar()
            elif opcao == "3":
                self.indicadores()
            elif opcao == "0":
                self.avaliar_facilidade()
                caminho_csv = self.exportar_csv()
                if caminho_csv:
                    print(f"Atendimentos exportados para: {caminho_csv}")
                self.indicadores()
                print("Até mais! Lembre-se: este assistente não é canal oficial.")
                break
            else:
                print("Opção inválida. Digite 1, 2, 3 ou 0.")
