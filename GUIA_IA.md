# Guía de uso de IA en Simplex Project

## Cómo usar la IA

### 1. Verificar que Ollama esté corriendo

```powershell
# Agregar Ollama al PATH (solo para la sesión actual)
$env:Path += ";$env:LOCALAPPDATA\Programs\Ollama"

# Verificar modelos disponibles
ollama list
```

Deberías ver:

```
NAME           ID              SIZE      MODIFIED
llama3.1:8b    46e0c10c039e    4.9 GB    X minutes ago
```

### 2. Ejecutar pruebas básicas

```powershell
# Activar el entorno virtual
.\.venv\Scripts\Activate.ps1

# Prueba simple y rápida
python test_ia_simple.py

# Prueba completa (incluye todos los procesadores)
python test_ia.py
```

### 3. Usar el sistema completo

```python
from src.nlp import NLPConnectorFactory, NLPModelType

# Crear conector con Ollama
conector = NLPConnectorFactory.create_connector(
    nlp_model_type=NLPModelType.LLAMA3_1_8B,
    use_mock_nlp=False  # Usar IA real
)

# Problema en lenguaje natural
problema = """
Una empresa fabrica dos productos: A y B.
Cada unidad de A genera $50 de ganancia.
Cada unidad de B genera $40 de ganancia.

Restricciones:
- Cada A requiere 2 horas de trabajo, cada B requiere 1 hora
- Hay 100 horas de trabajo disponibles

¿Cuántas unidades se deben producir para maximizar la ganancia?
"""

# Procesar y resolver
resultado = conector.process_and_solve(problema)

if resultado["success"]:
    print(f"Valor óptimo: ${resultado['solution']['optimal_value']:.2f}")
    print(f"Solución: {resultado['solution']['solution']}")
```

## Modelos disponibles

El proyecto soporta varios modelos de Ollama:

| Modelo          | Tamaño | Velocidad | Precisión | Recomendado para           |
| --------------- | ------ | --------- | --------- | -------------------------- |
| **llama3.1:8b** | 4.9 GB | Media     | Alta      | **Problemas complejos** ⭐ |
| llama3.2:3b     | 2 GB   | Rápida    | Media     | Problemas simples          |
| mistral:7b      | 4 GB   | Rápida    | Alta      | Uso general                |
| qwen2.5:14b     | 8 GB   | Lenta     | Muy alta  | Problemas muy complejos    |

### Descargar otros modelos

```powershell
# Modelo más rápido para pruebas
ollama pull llama3.2:3b

# Modelo para problemas muy complejos
ollama pull qwen2.5:14b
```

## Tiempos esperados

- **Mock processor**: < 1 segundo (sin IA real)
- **Ollama (primera vez)**: 30-120 segundos (carga el modelo)
- **Ollama (ya cargado)**: 10-30 segundos
- **Problema complejo**: hasta 2 minutos

## Troubleshooting

### Ollama no responde

```powershell
# Verificar si está corriendo
Get-Process -Name "ollama*"

# Si no está corriendo, abrirlo desde el menú inicio
# o ejecutar:
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve
```

### Modelo muy lento

1. **Primera ejecución**: El modelo se está cargando en memoria (normal)
2. **Siempre lento**: Tu sistema puede necesitar un modelo más pequeño
   ```powershell
   ollama pull llama3.2:3b  # Modelo más ligero
   ```

### Error "Model not found"

```powershell
# Verificar modelos instalados
ollama list

# Descargar el modelo si falta
ollama pull llama3.1:8b
```

### Uso de memoria

- Llama 3.1 8B requiere ~8 GB de RAM
- Si tienes poca RAM, usa `llama3.2:3b` (requiere ~4 GB)

## Próximos pasos

1. ✅ Probar con problemas simples (2-3 variables)
2. ⏳ Probar con problemas complejos (problema_complejo.txt)
3. ⏳ Optimizar el tiempo de respuesta
4. ⏳ Agregar caché para problemas similares
5. ⏳ Integrar con interfaz web

## Archivos importantes

- `test_ia.py` - Suite completa de pruebas
- `test_ia_simple.py` - Prueba rápida con un problema
- `src/nlp/ollama_processor.py` - Procesador que conecta con Ollama
- `src/nlp/config.py` - Configuración de modelos y prompts
- `ejemplos/nlp/` - Problemas de ejemplo para probar

## Comandos útiles

```powershell
# Ver logs detallados
$env:PYTHONUNBUFFERED=1
python test_ia_simple.py

# Probar solo el procesador Mock (sin IA)
python -c "from src.nlp.connector import NLPConnectorFactory; c = NLPConnectorFactory.create_connector(use_mock_nlp=True); print(c.process_and_solve('Maximizar 2x + 3y sujeto a x+y<=10'))"

# Verificar uso de memoria de Ollama
Get-Process ollama* | Select-Object Name, @{Name='Memory (MB)';Expression={[math]::Round($_.WorkingSet / 1MB)}}
```
