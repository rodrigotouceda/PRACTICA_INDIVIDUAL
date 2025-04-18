from FileReader import FileReader
import pandas as pd
from pathlib import Path
import sqlite3

class MenuCLI:
    def __init__(self):
        self.estado = {
            "archivo_cargado": False,
            "seleccion_columnas": False,
            "valores_faltantes": False,
            "transformacion": False,
            "normalizacion": False,
            "outliers": False,
            "visualizacion": False,
            "exportacion": False
        }

    def mostrar_menu(self):
        print("\n" + "=" * 29)
        print("Menú Principal")
        print("=" * 29)

        # Opción 1: Cargar datos
        archivo_estado = "(archivo: datos.csv)" if self.estado["archivo_cargado"] else "(ningún archivo cargado)"
        check = "[✓]" if self.estado["archivo_cargado"] else "[-]"
        print(f"{check} 1. Cargar datos {archivo_estado}")

        # Opción 2: Preprocesado
        if not self.estado["archivo_cargado"]:
            print("[✗] 2. Preprocesado de datos (requiere carga de datos)")
        else:
            print("[-] 2. Preprocesado de datos")
            self._mostrar_subetapas()

        # Opción 3: Visualización
        if all([self.estado[k] for k in ["seleccion_columnas", "valores_faltantes", "transformacion", "normalizacion", "outliers"]]):
            check = "[✓]" if self.estado["visualizacion"] else "[-]"
            print(f"{check} 3. Visualización de datos")
        else:
            print("[✗] 3. Visualización de datos (requiere preprocesado completo)")

        # Opción 4: Exportación
        if self.estado["visualizacion"]:
            check = "[✓]" if self.estado["exportacion"] else "[-]"
            print(f"{check} 4. Exportar datos")
        else:
            print("[✗] 4. Exportar datos (requiere visualización de datos)")

        print("[✓] 5. Salir")
        print("Seleccione una opción: ", end='')

    def _mostrar_subetapas(self):
        etapas = [
            ("seleccion_columnas", "2.1 Selección de columnas"),
            ("valores_faltantes", "2.2 Manejo de valores faltantes"),
            ("transformacion", "2.3 Transformación de datos categóricos"),
            ("normalizacion", "2.4 Normalización y escalado"),
            ("outliers", "2.5 Detección y manejo de valores atípicos"),
        ]
        requisitos = [
            None,
            "seleccion_columnas",
            "valores_faltantes",
            "transformacion",
            "normalizacion"
        ]

        for (clave, texto), req in zip(etapas, requisitos):
            if req and not self.estado[req]:
                print(f"[✗] {texto} (requiere {self._nombre_etapa(req)})")
            else:
                status = "[✓]" if self.estado[clave] else "[-]"
                estado_texto = "(completado)" if self.estado[clave] else "(pendiente)"
                print(f"{status} {texto} {estado_texto}")

    def _nombre_etapa(self, clave):
        nombres = {
            "seleccion_columnas": "selección de columnas",
            "valores_faltantes": "manejo de valores faltantes",
            "transformacion": "transformación categórica",
            "normalizacion": "normalización",
            "outliers": "detección de outliers"
        }
        return nombres.get(clave, clave)


    def cargar_datos(self):
        print("\n" + "=" * 29)
        print("Cargar datos")
        print("=" * 29)
        
        opcion = input("Seleccione el tipo de archivo a cargar:\n1 - CSV\n2 - Excel\n3 - SQLite\n> ")

        diccionario = {
            "1": "del archivo CSV",
            "2": "sel archivo Excel",
            "3": "de la base de datos SQLite"
        }
 
        if opcion == "1"  or opcion == "2":
            ruta = input(f"Ingrese la ruta {diccionario[opcion]}: ")
            ruta = Path(ruta)
            extension = ruta.suffix.lower()
            if (opcion == "1" and extension == ".csv") or (opcion == "2" and extension == ".xlsx"):
            
                reader = FileReader()
                try:
                    df = reader.parse_file(ruta)
                    print("Datos cargados correctamente")
                    print("Número de filas: ", df.shape[0])
                    print("Número de columnas: ", df.shape[1])
                    print("Primeras filas :")
                    print(df.head())
                except: 
                    print("\nError al cargar el archivo. Asegúrese de que el formato sea correcto.")
            else:
                print(f"\nError: El archivo no es del tipo especificado.")
                return

        elif opcion == "3":
            ruta = input(f"Ingrese la ruta {diccionario[opcion]}: ")
            ruta = Path(ruta)
            extension = ruta.suffix.lower()
            if extension not in [".db", ".sqlite", ".sqlite3"]:
                print("\nError: El archivo no es del tipo especificado.")
                return
            
            reader = FileReader()
            tablas = reader.get_db_tables(ruta)

            print("Tablas disponibles en la base de datos :")
            for i, tabla in enumerate(tablas, start=1):
                print(f"[{i}] {tabla}")

            tabla_seleccionada = input("Seleccione una tabla:")
            if tabla_seleccionada not in [str(i) for i in range(1, len(tablas) + 1)]:
                print("\nError: Tabla no válida.")
                return
            
            
            try:
                df = reader.parse_sqlite_table(ruta, tablas[int(tabla_seleccionada) - 1])
                print("Datos cargados correctamente")
                print("Número de filas: ", df.shape[0])
                print("Número de columnas: ", df.shape[1])
                print("Primeras filas :")
                print(df.head())
                print("Datos cargados correctamente")
            except: 
                print("\nError al cargar el archivo. Asegúrese de que el formato sea correcto.")
       
        

    def iniciar(self):
        while True:
            self.mostrar_menu()
            opcion = input()

            if opcion == "1":
                self.estado["archivo_cargado"] = True
                self.cargar_datos()
            elif opcion == "2":
                if not self.estado["archivo_cargado"]:
                    print("\nPrimero debe cargar un archivo.")
                else:
                    self._navegar_preprocesado()
            elif opcion == "3":
                if all([self.estado[k] for k in ["seleccion_columnas", "valores_faltantes", "transformacion", "normalizacion", "outliers"]]):
                    self.estado["visualizacion"] = True
                    print("\nVisualización completada.")
                else:
                    print("\nDebe completar todo el preprocesado antes de visualizar.")
            elif opcion == "4":
                if self.estado["visualizacion"]:
                    self.estado["exportacion"] = True
                    print("\nDatos exportados correctamente.")
                else:
                    print("\nDebe completar la visualización antes de exportar.")
            elif opcion == "5":
                if self._confirmar_salida():
                    print("\nCerrando la aplicación...")
                    break
                else:
                    print("\nRegresando al menú principal...")
            else:
                print("\nOpción no válida.")

    def _navegar_preprocesado(self):
        print("\n-- Preprocesado --")
        print("Seleccione subetapa:")
        print("  1. Selección de columnas")
        print("  2. Manejo de valores faltantes")
        print("  3. Transformación categórica")
        print("  4. Normalización y escalado")
        print("  5. Manejo de outliers")
        subop = input("Opción: ")
        mapeo = {
            "1": "seleccion_columnas",
            "2": "valores_faltantes",
            "3": "transformacion",
            "4": "normalizacion",
            "5": "outliers"
        }
        etapa = mapeo.get(subop)
        if etapa:
            requisitos = {
                "valores_faltantes": "seleccion_columnas",
                "transformacion": "valores_faltantes",
                "normalizacion": "transformacion",
                "outliers": "normalizacion"
            }
            req = requisitos.get(etapa)
            if req and not self.estado[req]:
                print(f"\nPrimero debe completar: {self._nombre_etapa(req)}.")
            else:
                self.estado[etapa] = True
                print(f"\nEtapa '{self._nombre_etapa(etapa)}' completada.")
        else:
            print("\nSubopción no válida.")

    def _confirmar_salida(self):
        print("\n" + "=" * 29)
        print("Salir de la Aplicación")
        print("=" * 29)
        print("¿Está seguro de que desea salir?")
        print("  [1] Sí")
        print("  [2] No")
        opcion = input("Seleccione una opción: ")
        return opcion == "1"
