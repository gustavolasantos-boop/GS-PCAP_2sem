"""Modelo de uma orientação da base de conhecimento do Citizen Assist Idoso."""


class Orientacao:
    """Representa um registro de orientação carregado do JSON."""

    def __init__(self, dados):
        self.id = dados["id"]
        self.categoria = dados["categoria"]
        self.titulo = dados["titulo"]
        self.palavras_chave = dados["palavras_chave"]
        self.resposta = dados["resposta"]
        self.documentos = dados["documentos"]
        self.onde = dados["onde"]
        self.fonte = dados["fonte"]
        self.verificado_em = dados["verificado_em"]

    def exibir(self):
        """Exibe a orientação com os campos exigidos no enunciado."""
        print(f"\n>> {self.titulo} [{self.categoria}]")
        print(self.resposta)
        print("Documentos / comprovantes:")
        for documento in self.documentos:
            print(f"  - {documento}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("Aviso: este assistente não é canal oficial.")
