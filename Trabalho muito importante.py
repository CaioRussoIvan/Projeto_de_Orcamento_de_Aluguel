"""
Projeto: Orçamento de Aluguel - Parte Prática
Arquivo: main.py (único arquivo contendo a aplicação em linha de comando)

Instruções:
- Execute com: python Projeto_Orçamento_Aluguel.py
- A aplicação solicita dados do usuário, calcula o valor do aluguel mensal, o parcelamento do contrato
  (R$ 2.000,00 em até 5x) e gera um arquivo .csv com 12 parcelas do orçamento (mensalidades do ano),
  indicando também em quais meses há pagamento das parcelas do contrato.

Classe principal: RentalQuote
- encapsula regras de negócio da imobiliária R.M.
- fornece método to_csv para gerar o arquivo de 12 meses.

Regras implementadas (conforme enunciado):
- Tipos e valores base:
  - Apartamento: R$ 700,00 / 1 Quarto
  - Casa: R$ 900,00 / 1 Quarto
  - Estudio: R$ 1200,00
- Contrato: R$ 2.000,00, pode ser dividido em até 5 vezes (opcional parcelamento)
- Apartamento com 2 quartos: +R$ 200,00
- Casa com 2 quartos: +R$ 250,00
- Vaga de garagem (apartamentos e casas): +R$ 300,00
- Estudio: possibilidade de adicionar 2 vagas por R$ 250,00 (pacote) e vagas adicionais por R$ 60,00 cada
- Desconto: Apartamento sem crianças -> 5% no valor do aluguel

"""
from dataclasses import dataclass, asdict
from datetime import datetime
import csv
import os


@dataclass
class RentalQuote:
    property_type: str  # 'apartamento', 'casa', 'estudio'
    bedrooms: int = 1
    garage: bool = False
    studio_base_parking: bool = False  # pacote de 2 vagas para estudio
    studio_extra_vagas: int = 0  # vagas adicionais para estudio (além do pacote de 2)
    has_children: bool = True  # usado para desconto em apartamentos
    contract_installments: int = 1  # 1..5

    CONTRACT_VALUE: float = 2000.0

    def base_rent(self) -> float:
        t = self.property_type.lower()
        if t == 'apartamento':
            return 700.0
        elif t == 'casa':
            return 900.0
        elif t == 'estudio':
            return 1200.0
        else:
            raise ValueError(f"Tipo de imóvel desconhecido: {self.property_type}")

    def compute_monthly_rent(self) -> float:
        rent = self.base_rent()
        t = self.property_type.lower()

        # Ajuste por quartos
        if t == 'apartamento' and self.bedrooms == 2:
            rent += 200.0
        if t == 'casa' and self.bedrooms == 2:
            rent += 250.0

        # Vaga de garagem para casas e apartamentos
        if t in ('apartamento', 'casa') and self.garage:
            rent += 300.0

        # Estudio - pacote de 2 vagas + vagas extras
        if t == 'estudio' and self.studio_base_parking:
            # pacote de 2 vagas por 250
            rent += 250.0
            # vagas extras (cada uma 60)
            if self.studio_extra_vagas > 0:
                rent += 60.0 * self.studio_extra_vagas

        # Desconto: 5% para apartamento sem crianças
        if t == 'apartamento' and not self.has_children:
            rent = rent * 0.95

        # arredondar para 2 casas decimais
        return round(rent, 2)

    def contract_installment_value(self) -> float:
        # Divide os R$ 2000,00 em até 5x
        n = max(1, min(self.contract_installments, 5))
        return round(self.CONTRACT_VALUE / n, 2)

    def total_monthly_with_contract(self) -> float:
        # Caso queira somar a parcela do contrato ao valor mensal (apenas nos meses com parcela)
        # Aqui não soma automaticamente; é uma utilidade: mensalidade + contrato_parcela
        return round(self.compute_monthly_rent() + self.contract_installment_value(), 2)

    def to_csv(self, filename: str = None) -> str:
        """Gera um CSV com 12 parcelas do orçamento (lista dos 12 meses).
        Para os meses 1..contract_installments, inclui o valor da parcela do contrato.
        Colunas: mes, mensalidade, contrato_parcela, total_no_mes
        Retorna o caminho do arquivo gerado.
        """
        mensalidade = self.compute_monthly_rent()
        contrato_parcela = self.contract_installment_value()
        installments = max(1, min(self.contract_installments, 5))

        if filename is None:
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'orcamento_{ts}.csv'

        # Garante pasta 'output' existindo
        out_dir = 'output'
        os.makedirs(out_dir, exist_ok=True)
        filepath = os.path.join(out_dir, filename)

        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['mes', 'mensalidade', 'contrato_parcela', 'total_no_mes'])
            for m in range(1, 13):
                contrato_here = contrato_parcela if m <= installments else 0.0
                total = round(mensalidade + contrato_here, 2)
                writer.writerow([m, f'{mensalidade:.2f}', f'{contrato_here:.2f}', f'{total:.2f}'])

        return filepath


def pergunta_sim_nao(prompt: str) -> bool:
    while True:
        r = input(prompt + ' (s/n): ').strip().lower()
        if r in ('s', 'sim'):
            return True
        if r in ('n', 'nao', 'não'):
            return False
        print('Resposta inválida. Digite s ou n.')


def escolhe_tipo() -> str:
    options = {'1': 'apartamento', '2': 'casa', '3': 'estudio'}
    print('Escolha o tipo de imóvel:')
    print('1) Apartamento')
    print('2) Casa')
    print('3) Estudio')
    while True:
        ch = input('Opção (1/2/3): ').strip()
        if ch in options:
            return options[ch]
        print('Opção inválida.')


def le_inteiro(prompt: str, default: int = 1, min_v: int = None, max_v: int = None) -> int:
    while True:
        r = input(f"{prompt} [{default}]: ").strip()
        if r == '':
            return default
        try:
            v = int(r)
            if (min_v is not None and v < min_v) or (max_v is not None and v > max_v):
                print(f'Valor fora do intervalo permitido ({min_v}..{max_v}).')
                continue
            return v
        except ValueError:
            print('Digite um número inteiro válido.')


def main():
    print('=== Gerador de Orçamento - Imobiliária R.M. ===')
    tipo = escolhe_tipo()
    bedrooms = 1
    garage = False
    studio_base_parking = False
    studio_extra_vagas = 0

    if tipo in ('apartamento', 'casa'):
        bedrooms = le_inteiro('Número de quartos (1 ou 2)', default=1, min_v=1, max_v=2)
        garage = pergunta_sim_nao('Deseja vaga de garagem?')
    elif tipo == 'estudio':
        studio_base_parking = pergunta_sim_nao('Deseja pacote de 2 vagas por R$ 250,00?')
        if studio_base_parking:
            studio_extra_vagas = le_inteiro('Quantas vagas extras além do pacote de 2 (cada uma R$ 60,00)?', default=0, min_v=0)

    has_children = pergunta_sim_nao('Possui crianças no domicílio? (Se "não" e for apartamento, aplica desconto de 5%)')

    contract_installments = le_inteiro('Parcelas do contrato (1 a 5) [padrão 1]', default=1, min_v=1, max_v=5)

    quote = RentalQuote(
        property_type=tipo,
        bedrooms=bedrooms,
        garage=garage,
        studio_base_parking=studio_base_parking,
        studio_extra_vagas=studio_extra_vagas,
        has_children=has_children,
        contract_installments=contract_installments
    )

    mensal = quote.compute_monthly_rent()
    parcela_contrato = quote.contract_installment_value()

    print('\n--- Resultado do Orçamento ---')
    print(f'Tipo de imóvel: {quote.property_type}')
    print(f'Quartos: {quote.bedrooms}')
    print(f'Vaga de garagem (aplicável): {"Sim" if quote.garage or (quote.property_type=="estudio" and quote.studio_base_parking) else "Não"}')
    print(f'Valor do aluguel mensal (mensalidade): R$ {mensal:.2f}')
    print(f'Valor do contrato total: R$ {quote.CONTRACT_VALUE:.2f} | Parcelas escolhidas: {quote.contract_installments} x R$ {parcela_contrato:.2f} (aplicadas nos primeiros {quote.contract_installments} meses)')

    filepath = quote.to_csv()
    print(f'Arquivo CSV com 12 parcelas gerado em: {filepath}')
    print('\nObservação: o arquivo CSV lista os 12 meses do ano com a mensalidade e, nos primeiros meses, o valor da parcela do contrato.')


if __name__ == '__main__':
    main()
