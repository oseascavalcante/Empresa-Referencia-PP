# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Visão Geral do Projeto

Sistema Django para precificação de contratos de serviços para concessionárias elétricas (Equatorial). O sistema calcula custos de mão de obra, encargos sociais e custos diretos através de um fluxo estruturado de trabalho.

## Comandos de Desenvolvimento

### Servidor e Banco de Dados
```bash
# Iniciar servidor de desenvolvimento
python manage.py runserver

# Aplicar migrações do banco
python manage.py migrate

# Criar novas migrações após mudanças nos models
python manage.py makemigrations

# Criar superusuário para acesso ao admin
python manage.py createsuperuser

# Gerar diagramas de relacionamento dos models
python manage.py graph_models cad_contrato cadastro_equipe mao_obra --group-models --rankdir=TB -o models_diagram.png
```

### Configuração do Ambiente
```bash
# Ativar ambiente virtual
# Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

## Arquitetura do Sistema

### Estrutura de 4 Apps Django

1. **`cad_contrato`** - Cadastro de contratos e gerenciamento de regionais
2. **`cadastro_equipe`** - Composição de equipes, funções e escopos de atividade
3. **`mao_obra`** - Cálculo de encargos sociais (Grupos A, B, C, D, E)
4. **`custo_direto`** - Consolidação de custos diretos e relatórios

### Padrão Service Layer
Lógica de negócio centralizada em arquivos `services.py`:
- `cad_contrato/services.py` - Inicialização de contratos
- `mao_obra/services.py` - Cálculos de encargos sociais
- `custo_direto/services.py` - Funções de cálculo de custos

### Arquitetura Baseada em Signals
Sistema usa Django signals para recálculo automático:
- Mudanças em encargos sociais (Grupos A-C) disparam recálculo de todos os grupos
- Alterações em funções/equipes atualizam automaticamente custos diretos
- Mudanças em benefícios propagam para cálculos de custos

## Fluxo de Precificação de Contratos

### 1. Fluxo de Configuração do Contrato
```
Criação do Contrato → Definição de Regionais → Configuração de Equipes → 
Definição de Funções/Salários → Definição de Escopo de Atividades → 
Composição de Equipes → Cálculo de Custos
```

### 2. Seleção de Contrato via Session
- Sistema usa `request.session['contrato_id']` para contexto global do contrato
- `app/context_processors.py` fornece dados do contrato para todos os templates
- Usuários devem selecionar um contrato antes de acessar a maioria das funcionalidades

### 3. Cálculo de Encargos Sociais
Sistema calcula 5 grupos de encargos sociais:
- **Grupo A**: Contribuições previdenciárias (INSS, FGTS, etc.)
- **Grupo B**: Indenizações rescisórias
- **Grupo C**: Substituições e ausências
- **Grupo D**: (Reservado para uso futuro)
- **Grupo E**: (Reservado para uso futuro)

### 4. Triggers de Cálculo de Custos
Recálculo automático via signals quando:
- Dados de encargos sociais mudam
- Composição de equipes é alterada
- Salários de funções são modificados
- Benefícios são atualizados

## Principais Models e Relacionamentos

### Entidades Centrais
- `CadastroContrato` - Contrato base com suporte a versionamento
- `Regional` - Divisões geográficas dentro dos contratos
- `Equipe` - Definições de equipes
- `Funcao` - Funções de trabalho com salários
- `EscopoAtividade` - Escopos de atividades
- `ComposicaoEquipe` - Liga regional + escopo + equipe com quantidades

### Models de Cálculo de Custos
- `FuncaoEquipe` - Detalhes de funções dentro da composição de equipes
- `CustoDiretoFuncao` - Custos diretos calculados por função
- `EncargosSociaisCentralizados` - Encargos sociais consolidados

## Problemas Conhecidos (de anotacoes.txt)

1. **Tela duplicada de edição de salários** em `/cadastro_equipe/editar-salarios/` precisa ser removida
2. **Padronização de estruturas** necessária para regionais e escopos seguirem padrão das equipes
3. **Dashboard de custos** com funcionalidade quebrada que precisa de correção

## Arquitetura de Templates

- Templates base em `app/templates/` com estilização Bootstrap
- Integração HTMX para atualizações dinâmicas de conteúdo
- Formulários inline para operações CRUD usando padrão `_form_*_inline.html`
- Templates baseados em componentes em `templates/components/`

## Constraints do Banco de Dados

Sistema força regras de negócio através de constraints:
- Combinações únicas de contrato+regional+escopo+equipe nas composições
- Nomes únicos de funções por contrato
- Nomes únicos de equipes por contrato
- Nomes únicos de regionais por contrato

## Notas de Desenvolvimento
- Dê as instruções sempre no idioma português do Brasil
- Não insira emoges nos prints
- Banco SQLite (`db.sqlite3`) para desenvolvimento
- Django 5.1.6 com django-extensions para comandos aprimorados
- Configuração em português brasileiro (`LANGUAGE_CODE = 'pt-br'`)
- Arquivos estáticos configurados para Bootstrap e estilização customizada
- Proteção CSRF habilitada para todos os formulários

## Padrões de Código Adotados

- **PEP 8**: Estilo de código Python
- **SOLID**: Princípios de design orientado a objetos
- **Clean Architecture**: Separação clara entre camadas (models, services, views)
- **Django Best Practices**: Uso de CBVs, signals, context processors nativos
- **Service Layer Pattern**: Lógica de negócio isolada em services

## Testes e Validação

Sempre verificar cálculos de custos ao fazer mudanças em:
- Models ou cálculos de encargos sociais
- Lógica de salários de funções
- Algoritmos de composição de equipes
- Fórmulas de cálculo de benefícios

Use o dashboard em `/custo_direto/dashboard/` para validar cálculos de custos com diferentes filtros e cenários.

## Convenções de Nomenclatura

- Models em PascalCase (ex: `CadastroContrato`)
- Funções e variáveis em snake_case (ex: `calcular_custo_total`)
- Templates em snake_case com hífens (ex: `adicionar_equipe.html`)
- URLs em kebab-case (ex: `adicionar-regional/`)
- Services seguem padrão `[Entity]Service` (ex: `CadastroContratoService`)