@echo off
:: Wrapper batch para resolver con IA desde el menú contextual

:: Obtener la ruta del archivo que se pasó como argumento
set "INPUT_FILE=%~1"

:: Obtener la ruta del proyecto (parent de context_menu)
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."

:: Cambiar al directorio del proyecto y ejecutar con NLP
cd /d "%PROJECT_DIR%"

echo ===============================================
echo  SIMPLEX SOLVER - Resolviendo con IA
echo ===============================================
echo.
echo Archivo: %INPUT_FILE%
echo Procesando con modelo de lenguaje...
echo.

:: Leer el contenido del archivo y procesarlo con IA
python -c "import sys; sys.path.insert(0, 'src'); from nlp import NLPConnectorFactory, NLPModelType; connector = NLPConnectorFactory.create_connector(NLPModelType.LLAMA3_1_8B); content = open(r'%INPUT_FILE%', 'r', encoding='utf-8').read(); result = connector.process_and_solve(content); print('\n' + '='*50); print('RESULTADO'); print('='*50); print(f'Estado: {\"Exitoso\" if result[\"success\"] else \"Error\"}'); print(f'Mensaje: {result.get(\"message\", \"\")}'); sol = result.get('solution', {}); print(f'Valor optimo: {sol.get(\"optimal_value\", \"N/A\")}'); print('\nVariables:'); vars_dict = sol.get('variables', {}); [print(f'  {k} = {v}') for k, v in vars_dict.items()]; print('='*50)"

pause
