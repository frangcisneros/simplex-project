"""
Script para verificar el sistema de logs.
"""

import sqlite3
import os
from pathlib import Path

# Ubicación de la BD
db_path = os.path.join(
    os.path.expanduser("~"),
    "AppData",
    "Roaming",
    "SimplexSolver",
    "logs",
    "simplex_logs.db",
)

print("=" * 70)
print("VERIFICACIÓN DEL SISTEMA DE LOGS")
print("=" * 70)
print(f"\nRuta de la BD: {db_path}")
print(f"Existe: {'✓ SÍ' if os.path.exists(db_path) else '✗ NO'}")

if not os.path.exists(db_path):
    print("\n⚠️  La base de datos no existe aún.")
    print("Ejecuta el programa al menos una vez para crear los logs.")
    exit(1)

# Tamaño del archivo
size = os.path.getsize(db_path)
print(f"Tamaño: {size:,} bytes ({size/1024:.2f} KB)")

# Conectar a la BD
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n" + "=" * 70)
print("ESTADÍSTICAS")
print("=" * 70)

# Total de logs
cursor.execute("SELECT COUNT(*) FROM logs")
total_logs = cursor.fetchone()[0]
print(f"\n📊 Total de logs registrados: {total_logs}")

# Logs por nivel
cursor.execute(
    """
    SELECT level, COUNT(*) as count 
    FROM logs 
    GROUP BY level 
    ORDER BY count DESC
"""
)
print("\n📈 Logs por nivel:")
for level, count in cursor.fetchall():
    print(f"   {level:10} : {count:4} logs")

# Sesiones
cursor.execute("SELECT COUNT(*) FROM sessions")
total_sessions = cursor.fetchone()[0]
print(f"\n🔄 Sesiones totales: {total_sessions}")

# Eventos del solver
cursor.execute('SELECT COUNT(*) FROM solver_events WHERE event_type="solve_complete"')
problems_solved = cursor.fetchone()[0]
print(f"🎯 Problemas resueltos: {problems_solved}")

# Última sesión
cursor.execute(
    """
    SELECT session_id, start_time, end_time 
    FROM sessions 
    ORDER BY start_time DESC 
    LIMIT 1
"""
)
last_session = cursor.fetchone()
if last_session:
    print(f"\n⏱️  Última sesión:")
    print(f"   ID: {last_session[0]}")
    print(f"   Inicio: {last_session[1][:19]}")
    print(f"   Fin: {last_session[2][:19] if last_session[2] else 'En curso'}")

# Últimos 10 logs
print("\n" + "=" * 70)
print("ÚLTIMOS 10 LOGS")
print("=" * 70)
cursor.execute(
    """
    SELECT timestamp, level, module, message 
    FROM logs 
    ORDER BY timestamp DESC 
    LIMIT 10
"""
)

for row in cursor.fetchall():
    timestamp = row[0][:19]
    level = row[1]
    module = row[2][:20]
    message = row[3][:50]
    print(f"\n[{timestamp}] [{level}] {module}")
    print(f"  → {message}")

# Último problema resuelto
print("\n" + "=" * 70)
print("ÚLTIMO PROBLEMA RESUELTO")
print("=" * 70)
cursor.execute(
    """
    SELECT timestamp, problem_type, num_variables, num_constraints, 
           iterations, execution_time_ms, status, optimal_value
    FROM solver_events 
    WHERE event_type = 'solve_complete'
    ORDER BY timestamp DESC 
    LIMIT 1
"""
)

result = cursor.fetchone()
if result:
    print(f"\n⏰ Timestamp: {result[0][:19]}")
    print(f"📝 Tipo: {result[1]}")
    print(f"🔢 Variables: {result[2]}, Restricciones: {result[3]}")
    print(f"🔄 Iteraciones: {result[4]}")
    print(f"⚡ Tiempo: {result[5]:.2f} ms")
    print(f"✅ Estado: {result[6]}")
    print(f"🎯 Valor óptimo: {result[7]:.6f}" if result[7] else "🎯 Valor óptimo: N/A")
else:
    print("\n⚠️  No hay problemas resueltos registrados.")

conn.close()

print("\n" + "=" * 70)
print("✓ VERIFICACIÓN COMPLETADA")
print("=" * 70)
print("\nEl sistema de logs está funcionando correctamente! 🎉")
print("\nPara ver más detalles, ejecuta: python view_logs.py")
