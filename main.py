import tkinter as tk
from tkinter import filedialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from automata.base.exceptions import InfiniteLanguageException

class AutomataApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Automata Finito")
        self.afn = None
        self.afd = None
        self.expresion_regular = ""
        self.create_widgets()

    def create_widgets(self):
        menu_bar = tk.Menu(self.master)
        menu_bar.add_command(label="Ingreso", command=self.ingreso)
        menu_bar.add_command(label="AFN", command=self.generar_afn)
        menu_bar.add_command(label="Conversión AFD", command=self.convertir_afd)
        menu_bar.add_command(label="Validar Cadenas", command=self.validar_cadenas)
        menu_bar.add_command(label="Mostrar Gramática", command=self.mostrar_gramatica)
        menu_bar.add_command(label="Grabar", command=self.grabar)
        menu_bar.add_command(label="Salir", command=self.master.quit)
        self.master.config(menu=menu_bar)

    def ingreso(self):
        self.ingreso_window = tk.Toplevel(self.master)
        self.ingreso_window.title("Ingreso de Expresión Regular")
        tk.Label(self.ingreso_window, text="Expresión Regular:").pack()
        self.expresion_entry = tk.Entry(self.ingreso_window)
        self.expresion_entry.pack()
        tk.Button(self.ingreso_window, text="Guardar", command=self.guardar_expresion).pack()

    def guardar_expresion(self):
        self.expresion_regular = self.expresion_entry.get()
        messagebox.showinfo("Guardado", "Expresión Regular guardada.")
        self.ingreso_window.destroy()

    def generar_afn(self):
        if not self.expresion_regular:
            messagebox.showwarning("Advertencia", "Por favor ingrese una expresión regular primero.")
            return
        try:
            self.afn = NFA.from_regex(self.expresion_regular)
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
            file.write(f"Estados: {afd.states}\n")
            file.write(f"Alfabeto: {afd.input_symbols}\n")
            file.write(f"Estado Inicial: {afd.initial_state}\n")
            file.write(f"Estados Finales: {afd.final_states}\n")
            file.write(f"Transiciones: {afd.transitions}\n")

    def validar_cadenas(self):
        if not self.afd:
            messagebox.showwarning("Advertencia", "Primero debe convertir a AFD.")
            return
        self.validar_window = tk.Toplevel(self.master)
        self.validar_window.title("Validar Cadenas")
        tk.Label(self.validar_window, text="Ingrese cadena:").pack()
        self.cadena_entry = tk.Entry(self.validar_window)
        self.cadena_entry.pack()
        tk.Button(self.validar_window, text="Validar", command=self.validar_cadena).pack()

    def validar_cadena(self):
        cadena = self.cadena_entry.get()
        if self.afd and self.afd.accepts_input(cadena):
            messagebox.showinfo("Resultado", "Cadena reconocida.")
        else:
            messagebox.showinfo("Resultado", "Cadena no reconocida.")

    def mostrar_gramatica(self):
        if not self.afn:
            messagebox.showwarning("Advertencia", "Primero debe generar el AFN.")
            return
        self.gramatica_window = tk.Toplevel(self.master)
        self.gramatica_window.title("Mostrar Gramática")
        gramatica_text = (f"Expresión Regular: {self.expresion_regular}\n"
                          f"Estados: {self.afn.states}\n"
                          f"Alfabeto: {self.afn.input_symbols}\n"
                          f"Transiciones: {self.afn.transitions}")
        tk.Label(self.gramatica_window, text=gramatica_text, justify="left").pack()

    def grabar(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if archivo:
            with open(archivo, "w") as file:
                file.write(f"Expresión Regular: {self.expresion_regular}\n")
                file.write(f"Estados AFN: {self.afn.states}\n")
                file.write(f"Transiciones AFN: {self.afn.transitions}\n")
                file.write(f"Estados AFD: {self.afd.states}\n")
                file.write(f"Transiciones AFD: {self.afd.transitions}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutomataApp(root)
    root.mainloop()
