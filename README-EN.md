# ohook-compiler

### This tool is not affiliated with massgrave.  
Official Massgrave Website: https://massgrave.dev/

[🔗Manual Office Activation](https://massgrave.dev/manual_ohook_activation) - Follow these steps after you have finished compiling the Dll's.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Warning: In some cases, the script may return a compilation error, but this could be a false positive. Check the ohook directory ```C:\OHookBuilder\ohook``` or ```C:\OHookBuilder\Output``` to see if the DLL was generated—if it was, everything worked fine.  
### Recommendation: Use a virtual machine to run the script, ensuring a controlled environment.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# OHook Compiler Documentation (OHook Builder)

## 1. Overview

The OHook Builder is an automated Python script that compiles the [OHook 0.5](https://github.com/asdcorp/ohook/releases/download/0.5/ohook_0.5.zip) dynamic link libraries (DLLs), which are used for specific software activation. The script automates the entire compilation process described in the original instructions, handling downloads, environment setup, compilation, and checksum verification.

## 2. Purpose

The script aims to:
- Automate the compilation process of the `sppc32.dll` and `sppc64.dll` libraries
- Ensure the compiled files are identical to the originals (via SHA-256 checksums)
- Simplify a complex process that involves:
  - Downloading specific resources
  - Configuring compilers
  - Modifying system date/time
  - Verifying file integrity

## 3. System Requirements

### 3.1 Required Software
- Windows (with administrator privileges)
- Python 3.x
- 7-Zip installed
- PowerShell

### 3.2 Minimum Hardware
- x86/x64 processor
- 2 GB RAM (4 GB recommended)
- 2 GB free disk space
- Internet connection for downloading resources

## 4. Directory Structure

The script creates and uses the following directory structure:

```
C:\OHookBuilder\
├── ohook\                  # OHook 0.5 source code
├── Compiladores\           
│   ├── mingw32\           # Compiler for 32-bit files
│   └── mingw64\           # Compiler for 64-bit files
├── Temp\                  # Temporary files
├── Output\                # Compiled DLLs
└── ohook_compiler.log     # Log file
```

## 5. Detailed Operation

### 5.1 Environment Preparation
1. Verifies administrator privileges  
2. Creates the required directory structure  
3. Locates 7-Zip on the system  

### 5.2 Resource Download
The script automatically downloads:
- OHook 0.5 source code (.zip)  
- MinGW 32-bit compiler (.7z)  
- MinGW 64-bit compiler (.7z)

### 5.3 Extraction and Setup
1. Extracts all downloaded files  
2. Creates symbolic links as per instructions:
   - `C:\mingw32` → 32-bit compiler directory  
   - `C:\mingw64` → 64-bit compiler directory  
   - `C:\ohook` → Source code directory  

### 5.4 Date/Time Configuration
The script:
1. Sets the time zone to UTC  
2. Sets the date to "07/08/2023 12:00:00"  
3. Maintains this date during the compilation process  
4. Restores the original system date/time after completion  

### 5.5 Compilation
1. Runs the compilation command using mingw32-make  
2. Generates the `sppc32.dll` and `sppc64.dll` files  

### 5.6 Integrity Check
The script checks whether the SHA-256 checksums of the compiled files match the expected values:  
- `sppc32.dll`: `09865ea5993215965e8f27a74b8a41d15fd0f60f5f404cb7a8b3c7757acdab02`  
- `sppc64.dll`: `393a1fa26deb3663854e41f2b687c188a9eacd87b23f17ea09422c4715cb5a9f`  

### 5.7 Finalization
1. Copies the DLL files to the output directory  
2. Removes the created symbolic links  
3. Cleans up temporary files  
4. Restores the original system date/time settings  

## 6. Script Usage

### 6.1 Basic Execution
1. Run PowerShell or CMD as Administrator  
2. Navigate to the directory containing the script  
3. Run the command: `python ohook-builder.py`

### 6.2 Script Output
- Compiled DLLs: Saved in `C:\OHookBuilder\Output\`  
- Execution log: `C:\OHookBuilder\ohook_compiler.log`

### 6.3 Troubleshooting

#### Error: "This script must be run as Administrator"  
- Solution: Close PowerShell and reopen it with administrator privileges  

#### Error: "7-Zip not found on the system"  
- Solution: Install 7-Zip and restart the script  

#### Error: "Failed to set date and time"  
- Solution: Make sure the Windows Time service is running  

#### Error: "Checksum verification failed"  
- Solution: Ensure the downloaded resources are complete and not corrupted  

## 7. Advanced Features

### 7.1 Logging System
The script implements a robust logging system that:
- Records all operations to a file  
- Displays messages in the console  
- Captures errors and exceptions  

### 7.2 Integrity Control
- SHA-256 checksum verification  
- Download validation with retry  
- File size verification  

### 7.3 Resource Management
- Downloading with timeout handling  
- Progress display for large downloads  
- Automatic cleanup of temporary files  

### 7.4 Error Handling
- Exception handling at all levels  
- Automatic rollback of changes in case of errors  
- Safe restoration of system date/time  

## 8. Security and Best Practices

### 8.1 Security
- Requires administrator privileges for critical operations  
- Verifies the integrity of all files  
- Uses temporary symbolic links  

### 8.2 Best Practices
- Maintains a detailed operation log  
- Provides clear visual feedback  
- Cleans up the environment after completion  

## 9. Limitations and Considerations

### 9.1 Limitations
- Works only on Windows systems  
- Requires internet access for downloading  
- Depends on the availability of specific URLs  

### 9.2 Important Considerations
- The script temporarily changes the system date/time  
- Creates and removes symbolic links in `C:\`  
- Requires administrator privileges  

## 10. Conclusion

The OHook Builder automates a complex compilation process that would otherwise require several manual steps. By ensuring reproducibility through checksums and automating the entire setup and build process, the script makes it accessible and reliable for technical users.

The script is especially useful for:
- Developers who need to recompile OHook DLLs  
- Auditors verifying code integrity  
- Technical users who require reproducible builds  

The implementation strictly follows the original instructions while adding automation, logging, and integrity verification features that make the process more robust and user-friendly.
