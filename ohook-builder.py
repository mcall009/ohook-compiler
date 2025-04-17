import os
import sys
import subprocess
import tempfile
import shutil
import hashlib
import ctypes
import zipfile
import urllib.request
import time
from datetime import datetime
import winreg
import threading
import logging
from pathlib import Path

# Estrutura de diretórios principal
MAIN_DIR = Path("C:\\OHookBuilder")
SOURCE_DIR = MAIN_DIR / "ohook"
COMPILERS_DIR = MAIN_DIR / "Compiladores"
MINGW32_DIR = COMPILERS_DIR / "mingw32"
MINGW64_DIR = COMPILERS_DIR / "mingw64"
TEMP_DIR = MAIN_DIR / "Temp"
OUTPUT_DIR = MAIN_DIR / "Output"

# Diretório necessário para compilação conforme instruções originais
OHOOK_COMPILE_DIR = Path("C:\\ohook")

# Checksums esperados para verificação
EXPECTED_CHECKSUMS = {
    "sppc32.dll": "09865ea5993215965e8f27a74b8a41d15fd0f60f5f404cb7a8b3c7757acdab02",
    "sppc64.dll": "393a1fa26deb3663854e41f2b687c188a9eacd87b23f17ea09422c4715cb5a9f"
}

# URLs para download dos recursos necessários
RESOURCES = {
    "ohook": "https://github.com/asdcorp/ohook/archive/refs/tags/0.5.zip",
    "mingw32": "https://github.com/brechtsanders/winlibs_mingw/releases/download/11.4.0-11.0.0-ucrt-r1/winlibs-i686-posix-dwarf-gcc-11.4.0-mingw-w64ucrt-11.0.0-r1.7z",
    "mingw64": "https://github.com/brechtsanders/winlibs_mingw/releases/download/11.4.0-11.0.0-ucrt-r1/winlibs-x86_64-posix-seh-gcc-11.4.0-mingw-w64ucrt-11.0.0-r1.7z"
}

# Variáveis globais para controle da data
keep_date_fixed = False
date_thread = None
log_file = MAIN_DIR / "ohook_compiler.log"

def setup_logging():
    MAIN_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(log_file),
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)

def check_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        logging.error(f"Erro ao verificar privilégios de administrador: {e}")
        return False

def print_status(message, status=None):
    prefix = {
        "success": "\r[✓] ",
        "error": "\r[✗] ",
        "warning": "\r[!] ",
        "info": "\r[i] ",
        "progress": "\r[...] "
    }.get(status, "\r")
    
    end = "" if status == "progress" else None
    print(f"{prefix}{message}", end=end)
    
    log_level = {
        "success": logging.INFO,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "progress": logging.DEBUG
    }.get(status, logging.INFO)
    
    logging.log(log_level, message)

def initialize_directories():
    directories = [MAIN_DIR, SOURCE_DIR, COMPILERS_DIR, MINGW32_DIR, MINGW64_DIR, TEMP_DIR, OUTPUT_DIR]
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logging.debug(f"Diretório criado/verificado: {directory}")
        except Exception as e:
            logging.error(f"Erro ao criar diretório {directory}: {e}")
            raise RuntimeError(f"Não foi possível criar o diretório {directory}")

def locate_7zip():
    try:
        for access_key in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY]:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\7-Zip", 0, winreg.KEY_READ | access_key)
                path_value, _ = winreg.QueryValueEx(key, "Path")
                winreg.CloseKey(key)
                exe_path = Path(path_value) / "7z.exe"
                if exe_path.exists():
                    return str(exe_path)
            except FileNotFoundError:
                continue
            except Exception as e:
                logging.debug(f"Erro ao buscar 7-Zip no registro ({access_key}): {e}")
                
        common_paths = [
            Path("C:\\Program Files\\7-Zip\\7z.exe"),
            Path("C:\\Program Files (x86)\\7-Zip\\7z.exe")
        ]
        
        for path in common_paths:
            if path.exists():
                return str(path)
                
        return None
    except Exception as e:
        logging.error(f"Erro ao localizar 7-Zip: {e}")
        return None

def download_file(url, destination_path, max_retries=3):
    destination = Path(destination_path)
    if destination.exists():
        logging.info(f"Arquivo já existe: {destination}")
        return True
        
    for attempt in range(1, max_retries + 1):
        try:
            print_status(f"Baixando {destination.name}... ({attempt}/{max_retries})", "progress")
            with urllib.request.urlopen(url, timeout=60) as response, open(destination, 'wb') as out_file:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                block_size = 8192
                
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    downloaded += len(buffer)
                    out_file.write(buffer)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print_status(f"Baixando {destination.name}... {percent:.1f}% ({attempt}/{max_retries})", "progress")
            
            print_status(f"Download de {destination.name} concluído", "success")
            return True
        except Exception as e:
            logging.error(f"Tentativa {attempt} falhou ao baixar {url}: {e}")
            if attempt == max_retries:
                print_status(f"Falha no download de {destination.name} após {max_retries} tentativas", "error")
                return False
            time.sleep(2)  # Espera antes de tentar novamente

def extract_archive(archive_path, extract_to, seven_zip_path):
    try:
        extract_path = Path(extract_to)
        archive = Path(archive_path)
        
        print_status(f"Extraindo {archive.name}...", "progress")
        
        process = subprocess.run(
            [seven_zip_path, "x", str(archive), f"-o{extract_path}", "-y"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding='utf-8', errors='replace'
        )
        
        if extract_path.exists():
            print_status(f"Extração de {archive.name} concluída", "success")
            return True
        else:
            print_status(f"Diretório de extração não encontrado após operação: {extract_path}", "error")
            return False
    except subprocess.CalledProcessError as e:
        print_status(f"Erro no processo de extração: {e.stderr}", "error")
        return False
    except Exception as e:
        print_status(f"Erro ao extrair {archive_path}: {str(e)}", "error")
        return False

def calculate_sha256(file_path):
    try:
        file = Path(file_path)
        if not file.exists():
            logging.error(f"Arquivo não encontrado para cálculo de hash: {file}")
            return None
            
        sha256_hash = hashlib.sha256()
        
        with open(file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    except Exception as e:
        logging.error(f"Erro ao calcular hash SHA-256 para {file_path}: {e}")
        return None

def set_fixed_date_thread():
    global keep_date_fixed
    target_date = datetime(2023, 8, 7, 12, 0, 0)
    
    logging.debug("Thread de data fixa iniciada")
    
    while keep_date_fixed:
        try:
            subprocess.run(
                ["powershell", "-Command", f"Set-Date '{target_date.strftime('%Y/%m/%d %H:%M:%S')}'"],
                check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            time.sleep(0.01)
        except Exception as e:
            logging.debug(f"Erro na thread de data fixa: {e}")
    
    logging.debug("Thread de data fixa encerrada")

def set_timezone_and_fixed_time():
    global keep_date_fixed
    global date_thread
    
    try:
        print_status("Configurando fuso horário para UTC...", "progress")
        result = subprocess.run(
            ["powershell", "-Command", "Set-TimeZone -Id 'UTC'"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding='utf-8', errors='replace'
        )
        
        if result.returncode == 0:
            print_status("Fuso horário configurado para UTC", "success")
        else:
            print_status(f"Erro ao configurar fuso horário: {result.stderr}", "error")
            return False
        
        print_status("Iniciando processo para manter data fixa em 2023-08-07 12:00 UTC...", "progress")
        keep_date_fixed = True
        date_thread = threading.Thread(target=set_fixed_date_thread, daemon=True)
        date_thread.start()
        
        time.sleep(2)
        
        now = datetime.now()
        if abs((now - datetime(2023, 8, 7, 12, 0, 0)).total_seconds()) > 60:
            print_status(f"Data não configurada corretamente: {now}", "warning")
            logging.warning(f"Data atual após tentativa de ajuste: {now}")
        else:
            print_status("Data fixa configurada com sucesso", "success")
        
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Erro ao configurar fuso horário: {e.stderr}", "error")
        keep_date_fixed = False
        return False
    except Exception as e:
        print_status(f"Erro ao configurar fuso horário e data: {str(e)}", "error")
        keep_date_fixed = False
        return False

def restore_time():
    global keep_date_fixed
    
    keep_date_fixed = False
    if date_thread and date_thread.is_alive():
        time.sleep(1)
    
    try:
        print_status("Restaurando data e hora do sistema...", "progress")
        
        commands = [
            ["w32tm", "/resync", "/force"],
            ["net", "stop", "w32time"],
            ["net", "start", "w32time"],
            ["w32tm", "/resync", "/force"]
        ]
        
        for cmd in commands:
            subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(1)
        
        print_status("Data e hora do sistema restauradas", "success")
        return True
    except Exception as e:
        print_status(f"Erro ao restaurar data e hora: {str(e)}", "warning")
        print_status("A data e hora precisam ser ajustadas manualmente", "warning")
        return False

def setup_compilation_environment():
    try:
        # Criar link simbólico para mingw64 em C:\mingw64 como exigido pelas instruções
        if not Path("C:\\mingw64").exists():
            print_status("Configurando ambiente para compilação - mingw64...", "progress")
            subprocess.run(
                ["cmd", "/c", f"mklink /J C:\\mingw64 {MINGW64_DIR}"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            print_status("Link simbólico para mingw64 criado", "success")
        
        # Criar link simbólico para mingw32 em C:\mingw32 como exigido pelas instruções
        if not Path("C:\\mingw32").exists():
            print_status("Configurando ambiente para compilação - mingw32...", "progress")
            subprocess.run(
                ["cmd", "/c", f"mklink /J C:\\mingw32 {MINGW32_DIR}"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            print_status("Link simbólico para mingw32 criado", "success")
        
        # Criar link simbólico para ohook em C:\ohook como exigido pelas instruções
        if not OHOOK_COMPILE_DIR.exists():
            print_status("Configurando ambiente para compilação - ohook...", "progress")
            subprocess.run(
                ["cmd", "/c", f"mklink /J C:\\ohook {SOURCE_DIR}"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            print_status("Link simbólico para ohook criado", "success")
        
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Erro ao configurar ambiente de compilação: {e.stderr}", "error")
        return False
    except Exception as e:
        print_status(f"Erro ao configurar ambiente de compilação: {str(e)}", "error")
        return False

def compile_sppc_dll():
    try:
        if not OHOOK_COMPILE_DIR.exists():
            print_status(f"Diretório {OHOOK_COMPILE_DIR} não encontrado!", "error")
            return False
        
        mingw_make = Path("C:\\mingw64\\bin\\mingw32-make.exe")
        if not mingw_make.exists():
            print_status(f"Compilador não encontrado: {mingw_make}", "error")
            return False
        
        print_status("Compilando arquivos sppc.dll...", "progress")
        
        os.chdir(OHOOK_COMPILE_DIR)
        
        compile_process = subprocess.run(
            [str(mingw_make)],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding='utf-8', errors='replace'
        )
        
        dll32 = OHOOK_COMPILE_DIR / "sppc32.dll"
        dll64 = OHOOK_COMPILE_DIR / "sppc64.dll"
        
        if dll32.exists() and dll64.exists():
            dll32_size = dll32.stat().st_size
            dll64_size = dll64.stat().st_size
            
            logging.info(f"DLL 32-bit compilada: {dll32_size} bytes")
            logging.info(f"DLL 64-bit compilada: {dll64_size} bytes")
            
            if dll32_size > 0 and dll64_size > 0:
                print_status("Compilação concluída com sucesso", "success")
                return True
            else:
                print_status("As DLLs foram criadas mas podem estar vazias", "error")
                return False
        else:
            print_status("Os arquivos DLL não foram criados após a compilação", "error")
            logging.error(f"Saída do compilador: {compile_process.stdout}")
            logging.error(f"Erros do compilador: {compile_process.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print_status(f"Erro na compilação: {e.stderr}", "error")
        logging.error(f"Comando que falhou: {e.cmd}")
        logging.error(f"Código de saída: {e.returncode}")
        return False
    except Exception as e:
        print_status(f"Erro na compilação: {str(e)}", "error")
        logging.exception("Exceção durante compilação")
        return False

def verify_checksums():
    results = {}
    
    for dll_file, expected_hash in EXPECTED_CHECKSUMS.items():
        dll_path = OHOOK_COMPILE_DIR / dll_file
        if dll_path.exists():
            actual_hash = calculate_sha256(dll_path)
            if actual_hash == expected_hash:
                print_status(f"Verificação do {dll_file}: Checksum correto", "success")
                results[dll_file] = True
            else:
                print_status(f"Verificação do {dll_file}: Checksum incorreto!", "error")
                print_status(f"  Esperado: {expected_hash}", "info")
                print_status(f"  Obtido:   {actual_hash}", "info")
                results[dll_file] = False
        else:
            print_status(f"Arquivo {dll_file} não encontrado!", "error")
            results[dll_file] = False
    
    return all(results.values())

def copy_to_output_dir():
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        for dll_file in EXPECTED_CHECKSUMS.keys():
            src_path = OHOOK_COMPILE_DIR / dll_file
            dst_path = OUTPUT_DIR / dll_file
            
            if src_path.exists():
                shutil.copy2(src_path, dst_path)
                if dst_path.exists():
                    print_status(f"Arquivo {dll_file} copiado para {OUTPUT_DIR}", "success")
                else:
                    print_status(f"Falha ao copiar {dll_file} para {OUTPUT_DIR}", "error")
                    return False
            else:
                print_status(f"Arquivo fonte {src_path} não encontrado!", "error")
                return False
        
        return True
    except Exception as e:
        print_status(f"Erro ao copiar arquivos para diretório de saída: {str(e)}", "error")
        logging.exception("Exceção ao copiar arquivos para saída")
        return False

def cleanup_symlinks():
    try:
        symlinks = ["C:\\mingw64", "C:\\mingw32", "C:\\ohook"]
        for link in symlinks:
            if Path(link).exists():
                print_status(f"Removendo link simbólico {link}...", "progress")
                subprocess.run(
                    ["cmd", "/c", f"rmdir {link}"],
                    check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
        return True
    except Exception as e:
        print_status(f"Erro ao remover links simbólicos: {str(e)}", "warning")
        return False

def cleanup_temp():
    try:
        print_status("Limpando arquivos temporários...", "progress")
        
        if TEMP_DIR.exists():
            shutil.rmtree(TEMP_DIR, ignore_errors=True)
            
        print_status("Limpeza concluída", "success")
        return True
    except Exception as e:
        print_status(f"Erro na limpeza: {str(e)}", "warning")
        return False

def main():
    global keep_date_fixed
    
    print("\n" + "="*60)
    print("COMPILADOR AUTOMATIZADO DE SPPC.DLL (OHOOK 0.5)")
    print("="*60 + "\n")
    
    try:
        initialize_directories()
        setup_logging()
        
        logging.info("Iniciando compilação de SPPC.DLL")
        
        if not check_admin():
            print_status("Este script precisa ser executado como administrador", "error")
            print_status("Por favor, feche e execute novamente como administrador", "info")
            return False
        
        seven_zip_path = locate_7zip()
        if not seven_zip_path:
            print_status("7-Zip não encontrado no sistema", "error")
            print_status("Por favor, instale o 7-Zip e execute o script novamente", "info")
            print_status("Download disponível em: https://www.7-zip.org/download.html", "info")
            return False
        
        logging.info(f"7-Zip encontrado: {seven_zip_path}")
        
        # Download de recursos
        downloads = {}
        for name, url in RESOURCES.items():
            file_name = os.path.basename(url)
            downloads[name] = TEMP_DIR / file_name
            if not download_file(url, downloads[name]):
                return False
        
        # Extração do ohook para o diretório temporário
        ohook_temp_dir = TEMP_DIR / "ohook-extract"
        ohook_temp_dir.mkdir(parents=True, exist_ok=True)
        
        if not extract_archive(downloads["ohook"], ohook_temp_dir, seven_zip_path):
            return False
        
        # Copiar os arquivos extraídos para o diretório de código-fonte
        ohook_extracted = ohook_temp_dir / "ohook-0.5"
        if not ohook_extracted.exists():
            print_status("Diretório do ohook não encontrado após extração", "error")
            return False
        
        try:
            if SOURCE_DIR.exists():
                shutil.rmtree(SOURCE_DIR)
            shutil.copytree(ohook_extracted, SOURCE_DIR)
        except Exception as e:
            print_status(f"Erro ao copiar arquivos para {SOURCE_DIR}: {str(e)}", "error")
            return False
        
        # Extrair compiladores para diretórios apropriados
        if not extract_archive(downloads["mingw32"], MINGW32_DIR.parent, seven_zip_path):
            return False
        
        if not extract_archive(downloads["mingw64"], MINGW64_DIR.parent, seven_zip_path):
            return False
        
        # Configurar ambiente de compilação (links simbólicos)
        if not setup_compilation_environment():
            return False
        
        # Configurar timezone e data fixa
        success = set_timezone_and_fixed_time()
        if not success:
            print_status("Falha ao configurar data e hora", "error")
            return False
        
        # Processo de compilação
        try:
            compile_success = compile_sppc_dll()
        finally:
            restore_time()
        
        if not compile_success:
            print_status("A compilação falhou", "error")
            return False
        
        # Verificar checksums
        if not verify_checksums():
            print_status("A verificação dos checksums falhou! Os arquivos compilados não são idênticos aos esperados.", "error")
            return False
        
        # Copiar arquivos compilados para pasta de saída
        if not copy_to_output_dir():
            return False
        
        # Limpeza
        cleanup_symlinks()
        cleanup_temp()
        
        print("\n" + "-"*60)
        print_status("Processo concluído com sucesso!", "success")
        print_status(f"Os arquivos DLL foram salvos em: {OUTPUT_DIR}", "info")
        print("-"*60 + "\n")
        
        logging.info(f"Compilação finalizada com sucesso. Arquivos salvos em {OUTPUT_DIR}")
        return True
        
    except Exception as e:
        print_status(f"Erro não tratado: {str(e)}", "error")
        logging.exception("Exceção não tratada no processo principal")
        cleanup_symlinks()  # Tentar limpar links simbólicos mesmo em caso de erro
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\nO script encontrou erros e não pôde ser concluído corretamente.")
        
        input("\nPressione Enter para sair...")
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário")
        keep_date_fixed = False
        restore_time()
        cleanup_symlinks()
    except Exception as e:
        print(f"\n\nErro não tratado: {str(e)}")
        logging.exception("Exceção fatal")
        keep_date_fixed = False
        restore_time()
        cleanup_symlinks()
        input("\nPressione Enter para sair...")
