import tkinter as tk
from tkinter import filedialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from automata.base.exceptions import InfiniteLanguageException
import argparse

class AutomataApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Automata Finito")
        self.master.state('zoomed')  # Abrir en pantalla completa
        self.afn = None
        self.afd = None
        self.expresion_regular = ""
        self.create_widgets()
    def create_widgets(self):
        frame = tk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH)
        tk.Button(frame, text="Ingreso", command=self.ingreso, font=("Helvetica", 16), bg="lightblue", width=20).pack(pady=10)
        tk.Button(frame, text="Generar AFN", command=self.generar_afn, font=("Helvetica", 16), bg="lightgreen", width=20).pack(pady=10)
        tk.Button(frame, text="Convertir a AFD", command=self.convertir_afd, font=("Helvetica", 16), bg="lightyellow", width=20).pack(pady=10)
        tk.Button(frame, text="Validar Cadenas", command=self.validar_cadenas, font=("Helvetica", 16), bg="lightcoral", width=20).pack(pady=10)
        tk.Button(frame, text="Mostrar Gramática", command=self.mostrar_gramatica, font=("Helvetica", 16), bg="lightpink", width=20).pack(pady=10)
        tk.Button(frame, text="Grabar", command=self.grabar, font=("Helvetica", 16), bg="lightgray", width=20).pack(pady=10)
        tk.Button(frame, text="Salir", command=self.master.quit, font=("Helvetica", 16), bg="red", fg="white", width=20).pack(pady=10)
    def ingreso(self):
        self.ingreso_window = tk.Toplevel(self.master)
        self.ingreso_window.title("Ingreso de Expresión Regular")
        tk.Label(self.ingreso_window, text="Expresión Regular:", font=("Helvetica", 14), fg="blue").pack(pady=10)
        self.expresion_entry = tk.Entry(self.ingreso_window, font=("Helvetica", 12), width=50)
        self.expresion_entry.pack(pady=10)
        tk.Button(self.ingreso_window, text="Guardar", command=self.guardar_expresion, font=("Helvetica", 12), bg="green", fg="white").pack(pady=10)
        tk.Button(self.ingreso_window, text="Cargar desde archivo", command=self.cargar_expresion, font=("Helvetica", 12), bg="orange", fg="white").pack(pady=10)
    def cargar_expresion(self):
        archivo = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if archivo:
            with open(archivo, "r") as file:
                self.expresion_regular = file.read().strip()
            messagebox.showinfo("Cargado", "Expresión Regular cargada desde archivo.")
            self.ingreso_window.destroy()
    def guardar_expresion(self):
        self.expresion_regular = self.expresion_entry.get()
        messagebox.showinfo("Guardado", "Expresión Regular guardada.")
        self.ingreso_window.destroy()
    def generar_afn(self):
        if not self.expresion_regular:
            messagebox.showwarning("Advertencia", "Por favor ingrese una expresión regular primero.")
            return
        try:
            self.afn = NFA.from_regex(self.expresion_regular.replace('λ', ''))
            self.dibujar_automata(self.afn, "AFN")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al generar el AFN: {str(e)}")
    def convertir_afd(self):
        if not self.afn:
            messagebox.showwarning("Advertencia", "Primero debe generar el AFN.")
            return
        try:
            self.afd = DFA.from_nfa(self.afn)
            self.guardar_afd(self.afd)
            self.dibujar_automata(self.afd, "AFD")
        except InfiniteLanguageException:
            messagebox.showerror("Error", "El AFD generado tiene un lenguaje infinito y no se puede procesar.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al convertir a AFD: {str(e)}")
    def dibujar_automata(self, automata, tipo):
        graph = nx.DiGraph()
        for estado in automata.states:
            graph.add_node(estado)
        for estado in automata.transitions:
            for simbolo in automata.transitions[estado]:
                destino = automata.transitions[estado][simbolo]
                if isinstance(destino, frozenset):
                    destino = list(destino)
                if isinstance(destino, set):
                    for d in destino:
                        graph.add_edge(estado, d, label=simbolo)
                else:
                    graph.add_edge(estado, destino, label=simbolo)
        pos = nx.spring_layout(graph)
        labels = nx.get_edge_attributes(graph, 'label')
        nx.draw(graph, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=10, font_weight='bold', arrows=True)
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
        plt.title(f"Diagrama del {tipo}")
        plt.show()
    def guardar_afd(self, afd):
        with open("AFD.txt", "w") as file:
            file.write(f"S = {list(afd.states)}\n")
            file.write(f"S0 = {{{afd.initial_state}}}\n")
            file.write(f"T = {list(afd.final_states)}\n")
            file.write(f"A = {list(afd.input_symbols)}\n")
            for estado in afd.transitions:
                for simbolo in afd.transitions[estado]:
                    destino = afd.transitions[estado][simbolo]
                    if isinstance(destino, frozenset):
                        destino = list(destino)
                    file.write(f"F({estado},{simbolo}) = {{{destino}}}\n")
    def validar_cadenas(self):
        if not self.afd:
            messagebox.showwarning("Advertencia", "Primero debe convertir a AFD.")
            return
        self.validar_window = tk.Toplevel(self.master)
        self.validar_window.title("Validar Cadenas")
        tk.Label(self.validar_window, text="Ingrese cadena:", font=("Helvetica", 14), fg="blue").pack(pady=10)
        self.cadena_entry = tk.Entry(self.validar_window, font=("Helvetica", 12), width=50)
        self.cadena_entry.pack(pady=10)
        tk.Button(self.validar_window, text="Validar", command=self.validar_cadena, font=("Helvetica", 12), bg="green", fg="white").pack(pady=10)
    def validar_cadena(self):
        cadena = self.cadena_entry.get().replace('λ', '')
        try:
            if self.afd and self.afd.accepts_input(cadena):
                messagebox.showinfo("Resultado", "Cadena reconocida.")
            else:
                messagebox.showinfo("Resultado", "Cadena no reconocida.")
        except InfiniteLanguageException:
            messagebox.showerror("Error", "El AFD tiene un lenguaje infinito y no se puede procesar.")
    def mostrar_gramatica(self):
        if not self.afn:
            messagebox.showwarning("Advertencia", "Primero debe generar el AFN.")
            return
        gramatica = self.generar_gramatica()
        self.gramatica_window = tk.Toplevel(self.master)
        self.gramatica_window.title("Mostrar Gramática")
        tk.Label(self.gramatica_window, text=gramatica, justify="left", font=("Helvetica", 12), fg="black").pack(pady=10)
    def generar_gramatica(self):
        variables = list(self.afn.states)
        terminales = list(self.afn.input_symbols)
        inicial = self.afn.initial_state
        producciones = []
        for estado in self.afn.transitions:
            for simbolo in self.afn.transitions[estado]:
                destinos = self.afn.transitions[estado][simbolo]
                if isinstance(destinos, frozenset):
                    destinos = list(destinos)
                for destino in destinos:
                    producciones.append(f"{estado} -> {simbolo}{destino}")
        gramatica = f"G = {{V: {variables}, T: {terminales}, S: {inicial}, P: {producciones}}}"
        return gramatica
    def grabar(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if archivo:
            with open(archivo, "w") as file:
                file.write(f"Expresión Regular: {self.expresion_regular}\n")
                file.write(f"Estados AFN: {list(self.afn.states)}\n")
                file.write(f"Transiciones AFN: {self.afn.transitions}\n")
                file.write(f"Estados AFD: {list(self.afd.states)}\n")
                file.write(f"Transiciones AFD: {self.afd.transitions}\n")
    def validar_cadenas_cmd(self):
        while True:
            cadena = input("Ingrese cadena (o 'exit' para salir): ").replace('λ', '')
            if cadena.lower() == 'exit':
                break
            try:
                if self.afd and self.afd.accepts_input(cadena):
                    print("Cadena reconocida.")
                else:
                    print("Cadena no reconocida.")
            except InfiniteLanguageException:
                print("El AFD tiene un lenguaje infinito y no se puede procesar.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automata Finito")
    parser.add_argument('--cmd', action='store_true', help="Modo línea de comando")
    args = parser.parse_args()
    if args.cmd:
        app = AutomataApp(None)
        app.validar_cadenas_cmd()
    else:
        root = tk.Tk()
        app = AutomataApp(root)
        root.mainloop()
