import pyodbc
import time  # Para el descanso del CPU
import sys

def ejecutar_kendit_ai():
    servidor = 'KENDALLPC'
    db = 'AcademiaDB'
    conn_str = f"Driver={{ODBC Driver 17 for SQL Server}};Server={servidor};Database={db};Trusted_Connection=yes;"

    try:
        # OPTIMIZACIÓN 1: Abrimos la conexión UNA SOLA VEZ fuera del bucle
        print("🔌 Conectando a los circuitos de KenditAI...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        while True:
            print("\n" + "="*40)
            print("🧠 KENDIT-AI v1.1 (Optimizado)")
            print("="*40)
            print("1. Consultar memoria")
            print("2. Guardar conocimiento")
            print("3. Salir")
            
            opcion = input("\n¿Qué deseas hacer, Kendall?: ").strip()

            if opcion == "3":
                print("💤 Cerrando sistemas... ¡Hasta luego!")
                break

            if opcion == "1":
                tema = input("🔍 Buscar: ")
                # Usamos parámetros (?) para evitar inyecciones y ser más rápidos
                query = "SELECT Categoria, Titulo, Contenido FROM KenditMemoria WHERE Contenido LIKE ? OR Titulo LIKE ?"
                cursor.execute(query, (f'%{tema}%', f'%{tema}%'))
                
                resultados = cursor.fetchall()
                if resultados:
                    for r in resultados:
                        print(f"\n📌 [{r[0]}] {r[1]}\n   -> {r[2]}")
                else:
                    print("❌ No hay registros.")

            elif opcion == "2":
                cat = input("Categoría: ")
                tit = input("Título: ")
                cont = input("Contenido: ")
                cursor.execute("INSERT INTO KenditMemoria (Categoria, Titulo, Contenido) VALUES (?, ?, ?)", (cat, tit, cont))
                conn.commit()
                print("✨ Guardado.")

            # OPTIMIZACIÓN 2: Evita que el menú "parpadee" demasiado rápido
            time.sleep(0.1) 

        # Cerramos la conexión solo al salir del programa
        conn.close()

    except Exception as e:
        print(f"⚠️ Error crítico: {e}")
    finally:
        print("🖥️  Estado: Programa finalizado de forma segura.")

if __name__ == "__main__":
    ejecutar_kendit_ai()