#!/usr/bin/env python3
"""
Módulo para análise e extração de temas dos normativos do BACEN
"""
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

class NormativoAnalyzer:
    def __init__(self):
        # Palavras-chave comuns em normativos do BACEN
        self.temas_bacen = {
            'crédito rural': ['crédito rural', 'produtor rural', 'agricultura', 'agronegócio', 'cpr', 'cédula de produto rural'],
            'poupança': ['poupança', 'sbpe', 'sistema brasileiro de poupança', 'depósitos de poupança'],
            'habitação': ['habitação', 'sfh', 'sfi', 'financiamento imobiliário', 'pmcmv', 'minha casa minha vida'],
            'recursos compulsórios': ['recursos compulsórios', 'recolhimento compulsório', 'depósitos compulsórios'],
            'política monetária': ['política monetária', 'taxa selic', 'copom', 'inflação'],
            'regulamentação bancária': ['regulamentação', 'instituições financeiras', 'bancos', 'cooperativas'],
            'prevenção a lavagem': ['lavagem de dinheiro', 'prevenção', 'combate ao crime', 'ldb'],
            'cyber segurança': ['cyber', 'segurança digital', 'fraudes', 'crime cibernético'],
            'sustentabilidade': ['sustentabilidade', 'esg', 'meio ambiente', 'risco climático'],
            'pagamentos': ['pagamentos', 'pix', 'cartões', 'meios de pagamento'],
            'câmbio': ['câmbio', 'dólar', 'moeda estrangeira', 'operações cambiais'],
            'gestão de risco': ['gestão de risco', 'risco operacional', 'risco de crédito', 'basel'],
            'compliance': ['compliance', 'conformidade', 'auditoria', 'controles internos'],
            'recursos humanos': ['recursos humanos', 'servidores', 'carreira', 'estágio probatório'],
            'infraestrutura': ['infraestrutura', 'fiis', 'fundo nacional', 'investimento']
        }
    
    def extrair_tema_principal(self, titulo: str, resumo: str) -> str:
        """Extrai o tema principal baseado no título e resumo"""
        texto_completo = f"{titulo} {resumo}".lower()
        
        # Conta ocorrências de cada tema
        temas_encontrados = {}
        for tema, palavras_chave in self.temas_bacen.items():
            contagem = 0
            for palavra in palavras_chave:
                contagem += texto_completo.count(palavra.lower())
            if contagem > 0:
                temas_encontrados[tema] = contagem
        
        # Retorna o tema com maior contagem
        if temas_encontrados:
            tema_principal = max(temas_encontrados, key=temas_encontrados.get)
            return tema_principal.title()
        
        # Fallback: extrai tema do título
        return self._extrair_tema_do_titulo(titulo)
    
    def _extrair_tema_do_titulo(self, titulo: str) -> str:
        """Extrai tema básico do título quando não há palavras-chave específicas"""
        titulo_lower = titulo.lower()
        
        if 'instrução normativa' in titulo_lower:
            return 'Regulamentação Operacional'
        elif 'resolução' in titulo_lower:
            return 'Política Regulatória'
        elif 'circular' in titulo_lower:
            return 'Comunicação Oficial'
        elif 'comunicado' in titulo_lower:
            return 'Comunicação Oficial'
        else:
            return 'Normativo BACEN'
    
    def gerar_mini_resumo(self, titulo: str, resumo: str, tema: str) -> str:
        """Gera um mini-resumo de 1 parágrafo do normativo"""
        # Limpa o resumo
        resumo_limpo = self._limpar_resumo(resumo)
        
        # Se o resumo for muito curto, usa informações do título
        if len(resumo_limpo) < 50:
            return self._gerar_resumo_do_titulo(titulo, tema)
        
        # Extrai as primeiras 2-3 frases mais relevantes
        frases = self._extrair_frases_relevantes(resumo_limpo)
        
        if frases:
            mini_resumo = ' '.join(frases[:2])  # Máximo 2 frases
            # Garante que não seja muito longo
            if len(mini_resumo) > 200:
                mini_resumo = mini_resumo[:200] + '...'
            return mini_resumo
        
        return self._gerar_resumo_do_titulo(titulo, tema)
    
    def _limpar_resumo(self, resumo: str) -> str:
        """Limpa e normaliza o resumo"""
        if not resumo:
            return ""
        
        # Remove HTML
        soup = BeautifulSoup(resumo, 'html.parser')
        texto = soup.get_text()
        
        # Remove quebras de linha excessivas
        texto = re.sub(r'\s+', ' ', texto)
        
        # Remove caracteres especiais desnecessários
        texto = re.sub(r'[^\w\s.,;:!?-]', '', texto)
        
        return texto.strip()
    
    def _extrair_frases_relevantes(self, texto: str) -> List[str]:
        """Extrai as frases mais relevantes do texto"""
        # Divide em frases
        frases = re.split(r'[.!?]+', texto)
        
        # Filtra frases muito curtas ou vazias
        frases_validas = [f.strip() for f in frases if len(f.strip()) > 20]
        
        # Prioriza frases que contêm palavras-chave importantes
        frases_priorizadas = []
        palavras_importantes = ['estabelece', 'define', 'altera', 'institui', 'dispõe', 'cria', 'modifica']
        
        for frase in frases_validas:
            if any(palavra in frase.lower() for palavra in palavras_importantes):
                frases_priorizadas.append(frase)
        
        # Se não encontrou frases priorizadas, usa as primeiras válidas
        if not frases_priorizadas:
            frases_priorizadas = frases_validas
        
        return frases_priorizadas
    
    def _gerar_resumo_do_titulo(self, titulo: str, tema: str) -> str:
        """Gera resumo baseado no título quando não há resumo disponível"""
        # Extrai informações do título
        if 'instrução normativa' in titulo.lower():
            numero = self._extrair_numero_normativo(titulo)
            return f"Instrução Normativa BCB nº {numero} que estabelece procedimentos e diretrizes relacionadas a {tema.lower()}."
        elif 'resolução' in titulo.lower():
            numero = self._extrair_numero_normativo(titulo)
            return f"Resolução que define normas e regulamentações sobre {tema.lower()}."
        else:
            return f"Normativo do BACEN relacionado a {tema.lower()}."
    
    def _extrair_numero_normativo(self, titulo: str) -> str:
        """Extrai o número do normativo do título"""
        # Procura por padrões como "N° 123" ou "nº 123"
        match = re.search(r'n[°º]\s*(\d+)', titulo.lower())
        if match:
            return match.group(1)
        return ""

def analisar_normativo(titulo: str, resumo: str) -> Dict[str, str]:
    """Função principal para analisar um normativo"""
    analyzer = NormativoAnalyzer()
    
    tema = analyzer.extrair_tema_principal(titulo, resumo)
    mini_resumo = analyzer.gerar_mini_resumo(titulo, resumo, tema)
    
    return {
        'tema': tema,
        'mini_resumo': mini_resumo
    }
