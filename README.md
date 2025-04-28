# ohook-compiler

### Esta ferramenta não está ligada ao massgrave.
Site Oficial do Massgrave: https://massgrave.dev/

📘 [Read this in English](README-EN.md)

[🔗Ativação Manual do Office](https://massgrave.dev/manual_ohook_activation) - Siga esses passos após finalizar a compilação das Dll's.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Atenção: Em alguns casos o script retornará erro na compilação, porém, pode ser apenas um falso positivo. Confira no diretório ```C:\OHookBuilder\ohook``` ou ```C:\OHookBuilder\Output``` se a dll foi gerada, se sim, deu tudo certo.
### Recomendação: Utilize uma máquina virtual para utilizar o script, um ambiente controlado.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Documentação do OHook Compiler (OHook Builder)

## 1. Visão Geral

O OHook Builder é um script Python automatizado que compila as bibliotecas dinâmicas (DLLs) do OHook 0.5, que são utilizadas para ativação de software específico. O script automatiza todo o processo de compilação descrito nas instruções originais, gerenciando downloads, configuração de ambiente, compilação e verificação de checksum.

## 2. Propósito

O script tem como objetivo:
- Automatizar o processo de compilação das bibliotecas sppc32.dll e sppc64.dll
- Garantir que os arquivos compilados sejam idênticos aos originais (através de checksums SHA-256)
- Simplificar um processo complexo que envolve:
  - Download de recursos específicos
  - Configuração de compiladores
  - Manipulação da data/hora do sistema
  - Verificação de integridade dos arquivos

## 3. Requisitos do Sistema

### 3.1 Software Necessário
- Windows (com privilégios de administrador)
- Python 3.x
- 7-Zip instalado
- PowerShell

### 3.2 Hardware Mínimo
- Processador x86/x64
- 2 GB de RAM (recomendado 4 GB)
- 2 GB de espaço livre em disco
- Conexão com a internet para download de recursos

## 4. Estrutura de Diretórios

O script cria e utiliza a seguinte estrutura de diretórios:

```
C:\OHookBuilder\
├── ohook\                  # Código-fonte do OHook 0.5
├── Compiladores\           
│   ├── mingw32\           # Compilador para arquivos 32-bit
│   └── mingw64\           # Compilador para arquivos 64-bit
├── Temp\                  # Arquivos temporários
├── Output\                # DLLs compiladas
└── ohook_compiler.log     # Arquivo de log
```

## 5. Funcionamento Detalhado

### 5.1 Preparação do Ambiente
1. Verifica privilégios de administrador
2. Cria estrutura de diretórios necessária
3. Localiza 7-Zip no sistema

### 5.2 Download de Recursos
O script baixa automaticamente:
- OHook 0.5 source code (.zip)
- MinGW 32-bit compiler (.7z)
- MinGW 64-bit compiler (.7z)

### 5.3 Extração e Configuração
1. Extrai todos os arquivos baixados
2. Cria links simbólicos conforme instruções:
   - `C:\mingw32` → Diretório do compilador 32-bit
   - `C:\mingw64` → Diretório do compilador 64-bit
   - `C:\ohook` → Diretório do código-fonte

### 5.4 Configuração de Data/Hora
O script:
1. Define o fuso horário como UTC
2. Fixa a data em "07/08/2023 12:00:00"
3. Mantém esta data durante o processo de compilação
4. Restaura a data/hora do sistema após a conclusão

### 5.5 Compilação
1. Executa o comando de compilação usando mingw32-make
2. Gera os arquivos sppc32.dll e sppc64.dll

### 5.6 Verificação de Integridade
O script verifica se os checksums SHA-256 dos arquivos compilados correspondem aos valores esperados:
- sppc32.dll: `09865ea5993215965e8f27a74b8a41d15fd0f60f5f404cb7a8b3c7757acdab02`
- sppc64.dll: `393a1fa26deb3663854e41f2b687c188a9eacd87b23f17ea09422c4715cb5a9f`

### 5.7 Finalização
1. Copia os arquivos DLL para o diretório de saída
2. Remove links simbólicos criados
3. Limpa arquivos temporários
4. Restaura a configuração de data/hora do sistema

## 6. Uso do Script

### 6.1 Execução Básica
1. Execute o PowerShell ou CMD como administrador
2. Navegue até o diretório que contém o script
3. Execute o comando: `python ohook-builder.py`

### 6.2 Saída do Script
- DLLs compiladas: Salvas em `C:\OHookBuilder\Output\`
- Log de execução: `C:\OHookBuilder\ohook_compiler.log`

### 6.3 Resolução de Problemas

#### Erro: "Este script precisa ser executado como administrador"
- Solução: Feche o PowerShell e abra novamente com privilégios de administrador

#### Erro: "7-Zip não encontrado no sistema"
- Solução: Instale o 7-Zip e reinicie o script

#### Erro: "Falha ao configurar data e hora"
- Solução: Verifique se o serviço de tempo do Windows está em execução

#### Erro: "A verificação dos checksums falhou"
- Solução: Certifique-se de que os recursos baixados estão completos e não corrompidos

## 7. Características Avançadas

### 7.1 Sistema de Logging
O script implementa um sistema de logging robusto que:
- Registra todas as operações em arquivo
- Exibe mensagens no console
- Captura erros e exceções

### 7.2 Controle de Integridade
- Verificação de checksums SHA-256
- Validação de downloads com retry
- Verificação de tamanho de arquivos

### 7.3 Gerenciamento de Recursos
- Download com tratamento de timeout
- Exibição de progresso para downloads grandes
- Limpeza automática de arquivos temporários

### 7.4 Tratamento de Erros
- Captura de exceções em todos os níveis
- Reversão automática de alterações em caso de erro
- Restauração segura da data/hora do sistema

## 8. Segurança e Boas Práticas

### 8.1 Segurança
- Requer privilégios de administrador para operações críticas
- Verifica integridade de todos os arquivos
- Usa links simbólicos temporários

### 8.2 Boas Práticas
- Mantém log detalhado de todas as operações
- Fornece feedback visual claro
- Limpa o ambiente após conclusão

## 9. Limitações e Considerações

### 9.1 Limitações
- Funciona apenas em sistemas Windows
- Requer acesso à internet para downloads
- Depende de URLs específicas estarem disponíveis

### 9.2 Considerações Importantes
- O script altera temporariamente a data/hora do sistema
- Cria e remove links simbólicos em C:\
- Requer privilégios de administrador

## 10. Conclusão

O OHook Builder automatiza um processo complexo de compilação que normalmente exigiria várias etapas manuais. Ao garantir a reprodutibilidade através de checksums e automatizar toda a configuração e compilação, o script torna o processo acessível e confiável para usuários técnicos.

O script é especialmente útil para:
- Desenvolvedores que precisam recompilar as DLLs do OHook
- Auditores verificando a integridade do código
- Usuários técnicos que necessitam de builds reproduzíveis

A implementação segue rigorosamente as instruções originais enquanto adiciona recursos de automação, logging e verificação de integridade que tornam o processo mais robusto e fácil de usar.
