"""Leitura e busca pontuada na base de conhecimento JSON."""

import json
import unicodedata
from pathlib import Path

from orientacao import Orientacao


CAMPOS_OBRIGATORIOS = {
    "id",
    "categoria",
    "titulo",
    "palavras_chave",
    "resposta",
    "documentos",
    "onde",
    "fonte",
    "verificado_em",
}


def normalizar(texto):
    """Converte para minúsculas, remove acentos e pontuação e normaliza espaços."""
    texto = unicodedata.normalize("NFD", str(texto).lower().strip())
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )
    texto = "".join(
        caractere if caractere.isalnum() or caractere.isspace() else " "
        for caractere in texto
    )
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """Agrupa orientações e oferece busca por pontuação."""

    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.orientacoes = []

    def carregar(self):
        """Lê o JSON e instancia Orientacao; arquivo ausente/corrompido não encerra o app."""
        if not self.caminho.exists():
            print(f"Aviso: base de conhecimento não encontrada: {self.caminho}")
            self.orientacoes = []
            return False

        try:
            dados = json.loads(self.caminho.read_text(encoding="utf-8"))
            if not isinstance(dados, list):
                raise ValueError("a raiz do JSON precisa ser uma lista")

            orientacoes_carregadas = []
            for indice, registro in enumerate(dados, start=1):
                if not isinstance(registro, dict):
                    print(f"Aviso: registro {indice} ignorado (não é um objeto JSON).")
                    continue
                faltantes = CAMPOS_OBRIGATORIOS - registro.keys()
                if faltantes:
                    nomes = ", ".join(sorted(faltantes))
                    print(f"Aviso: registro {indice} ignorado (campos ausentes: {nomes}).")
                    continue
                if not isinstance(registro["palavras_chave"], list):
                    print(f"Aviso: registro {indice} ignorado (palavras_chave precisa ser uma lista).")
                    continue
                if not isinstance(registro["documentos"], list):
                    print(f"Aviso: registro {indice} ignorado (documentos precisa ser uma lista).")
                    continue
                orientacoes_carregadas.append(Orientacao(registro))

            self.orientacoes = orientacoes_carregadas
            if not self.orientacoes:
                print("Aviso: a base não contém orientações válidas.")
            return bool(self.orientacoes)
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as erro:
            print(f"Aviso: não foi possível carregar a base de conhecimento ({erro}).")
            self.orientacoes = []
            return False

    def categorias(self):
        """Retorna as categorias únicas em ordem alfabética."""
        return sorted({orientacao.categoria for orientacao in self.orientacoes}, key=str.casefold)

    def por_categoria(self, categoria):
        """Retorna as orientações pertencentes a uma categoria."""
        return sorted(
            [o for o in self.orientacoes if o.categoria == categoria],
            key=lambda orientacao: orientacao.titulo.casefold(),
        )

    def pontuar(self, pergunta, orientacao):
        """Soma +3 por palavra-chave e +1 por palavra de 4+ letras presente no título."""
        pergunta_normalizada = normalizar(pergunta)
        titulo_normalizado = normalizar(orientacao.titulo).strip().split()
        palavras_titulo = set(titulo_normalizado)
        palavras_pergunta = set(pergunta_normalizada.strip().split())

        pontos = 0
        for palavra_chave in orientacao.palavras_chave:
            chave = normalizar(palavra_chave).strip()
            if chave and f" {chave} " in pergunta_normalizada:
                pontos += 3

        for palavra in palavras_pergunta:
            if len(palavra) >= 4 and palavra in palavras_titulo:
                pontos += 1

        return pontos

    def buscar(self, pergunta):
        """Devolve tuplas (pontos, orientação), da maior para a menor pontuação."""
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda item: (-item[0], item[1].id))
        return resultados
