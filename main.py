"""Ponto de entrada do Citizen Assist Idoso."""

from pathlib import Path

from assistente import Assistente
from base_conhecimento import BaseConhecimento


DIRETORIO_PROJETO = Path(__file__).resolve().parent


def main():
    caminho_base = DIRETORIO_PROJETO / "data" / "base_conhecimento.json"
    base = BaseConhecimento(caminho_base)
    base.carregar()

    assistente = Assistente(
        "Citizen Assist Idoso",
        base,
        diretorio_dados=DIRETORIO_PROJETO / "data",
    )
    assistente.executar()


if __name__ == "__main__":
    main()
