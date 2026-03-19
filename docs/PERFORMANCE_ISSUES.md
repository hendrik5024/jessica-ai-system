# Performance Issues & Troubleshooting

## Known Issue: High Memory Usage on Low-RAM Systems

**Date Identified:** January 9, 2026  
**Status:** Hardware limitation - requires system upgrade

### Symptoms
- Jessica desktop UI freezes after receiving a command
- Response time exceeds 10-20 minutes
- llama-cli process shows high memory usage (1.5GB+)
- System memory usage reaches 98%+
- Task Manager shows llama-cli consuming significant resources

### Root Cause
The GGUF models require substantial RAM to load and run inference:
- **Chat Model (Mistral 7B Q4_K_M):** ~4-6GB RAM
- **Code Model (CodeLlama 13B Q4_K_M):** ~8-10GB RAM
- **System Overhead:** 2-4GB for Windows + other applications

**Total requirement:** 16GB minimum, 32GB recommended

### Systems Affected
- Laptops/PCs with 8GB RAM or less
- Systems with 16GB RAM running many background applications
- Systems without sufficient swap/page file space

### Temporary Workarounds

#### Option 1: Use Smaller Models
Replace current models with quantized versions:
- Use Q2_K or Q3_K_S quantization (lower quality, less memory)
- Use smaller base models (3B or 7B instead of 13B for coding)

Download from: https://huggingface.co/TheBloke/

#### Option 2: Single-Model Mode
Disable the coding model to reduce memory:
1. Remove or rename `codellama-13b-instruct.Q4_K_M.gguf`
2. Jessica will use only the chat model for all tasks

#### Option 3: Terminal Mode Instead of GUI
The desktop GUI loads models at startup. Use terminal mode instead:
```powershell
python run_jessica.py
```
This loads models on-demand per query.

#### Option 4: Increase Virtual Memory (Page File)
Windows Settings → System → About → Advanced system settings → Performance Settings → Advanced → Virtual Memory
- Set custom size: Initial = 16GB, Maximum = 32GB
- This uses SSD/HDD as extended RAM (slower but prevents crashes)

### Permanent Solution
**Upgrade to a system with 32GB+ RAM** for optimal performance.

### Related Files
- [README.md](../README.md) - Updated with system requirements
- [jessica/llama_cpp_engine/llama_runner.py](../jessica/llama_cpp_engine/llama_runner.py) - Model loading logic

### Future Improvements
- [ ] Add memory usage detection before loading models
- [ ] Show warning if system RAM < 16GB
- [ ] Implement lazy loading (load models only when needed)
- [ ] Add configuration option for lightweight mode
- [ ] Support for cloud/API fallback for low-resource systems

---
**Next Steps:** User will retry after upgrading to a higher-spec laptop.
