import random
from collections import deque, OrderedDict
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font

class VirtualMemorySimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Memoria Virtual")
        
        # Configuración inicial
        self.physical_frames = 4
        self.page_size = 1024  # 1KB
        self.processes = []
        self.current_process_id = 0
        self.page_faults = 0
        self.algorithm = "FIFO"
        self.simulation_speed = 1
        
        # Inicializar la memoria física
        self.reset_memory()
        
        # Configurar la interfaz
        self.setup_ui()
    def animate_page_fault(self, old_page, new_page, frame_id):
    # Parpadeo al reemplazar
        for _ in range(3):
            self.mem_canvas.itemconfig(f"frame_{frame_id}", fill="#FFCDD2")  # Rojo claro
            self.root.update()
            time.sleep(0.2)
            self.mem_canvas.itemconfig(f"frame_{frame_id}", fill="#90CAF9")  # Azul
            self.root.update()
            time.sleep(0.2)

    def reset_memory(self):
        self.physical_memory = [None] * self.physical_frames
        self.page_table = {}  # {page_id: frame_id or None}
        self.fifo_queue = deque()
        self.lru_cache = OrderedDict()
        self.page_faults = 0
    
    def setup_ui(self):

        style = ttk.Style()
        style.configure("Custom.TButton", 
                foreground="#041183", 
                font=("Harrington", 8, "bold"))
        # Panel de control
        control_frame = ttk.LabelFrame(self.root, text="Controles")
        control_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # Configuración de memoria
        ttk.Label(control_frame, text="Marcos físicos:").grid(row=0, column=0)
        self.frames_entry = ttk.Entry(control_frame)
        self.frames_entry.insert(0, str(self.physical_frames))
        self.frames_entry.grid(row=0, column=1)
        
        ttk.Label(control_frame, text="Algoritmo:").grid(row=1, column=0)
        self.algorithm_var = tk.StringVar(value=self.algorithm)
        algo_menu = ttk.OptionMenu(control_frame, self.algorithm_var, 
                                  "FIFO", "FIFO", "LRU", "Óptimo")
        algo_menu.grid(row=1, column=1)
        

        # Botones
        ttk.Button(control_frame, text="Nuevo Proceso", command=self.create_process,
           style="Custom.TButton").grid(row=2, column=0)
        ttk.Button(control_frame, text="Simular Acceso", command=self.simulate_access,
                   style="Custom.TButton").grid(row=2, column=1)
        ttk.Button(control_frame, text="Reiniciar", command=self.reset_simulation,
                   style="Custom.TButton").grid(row=2, column=2)
        
        # Visualización de memoria
        mem_frame = ttk.LabelFrame(self.root, text="Estado de la Memoria")
        mem_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.mem_canvas = tk.Canvas(mem_frame, bg="white")
        self.mem_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Estadísticas
        stats_frame = ttk.LabelFrame(self.root, text="Estadísticas")
        stats_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.stats_label = ttk.Label(stats_frame, text="Fallos de página: 0")
        self.stats_label.pack()
    
    def create_process(self):
        try:
            self.physical_frames = int(self.frames_entry.get())
            if self.physical_frames <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Número de marcos no válido")
            return
        
        self.reset_memory()
        self.algorithm = self.algorithm_var.get()
        self.current_process_id += 1
        
        # Crear un nuevo proceso con páginas aleatorias
        process_pages = random.randint(3, 10)
        self.page_table = {f"P{self.current_process_id}-{i}": None 
                          for i in range(process_pages)}
        
        messagebox.showinfo("Proceso creado", 
                          f"Proceso {self.current_process_id} creado con {process_pages} páginas")
        self.update_display()
    
    def simulate_access(self):
        if not self.page_table:
            messagebox.showwarning("Advertencia", "No hay proceso creado")
            return
        
        # Seleccionar una página al azar para acceder
        page_id = random.choice(list(self.page_table.keys()))
        self.access_page(page_id)
        self.update_display()
    
    def access_page(self, page_id):
        # Verificar si la página está en memoria
        if self.page_table[page_id] is not None:
            # Actualizar LRU si es el algoritmo seleccionado
            if self.algorithm == "LRU":
                self.lru_cache.move_to_end(page_id)
            return True
        
        # Fallo de página
        self.page_faults += 1
        self.handle_page_fault(page_id)
        return False
    
    def handle_page_fault(self, page_id):
        # Buscar un marco libre
        for i, frame in enumerate(self.physical_memory):
            if frame is None:
                self.physical_memory[i] = page_id
                self.page_table[page_id] = i
                
                # Actualizar estructuras de algoritmos
                if self.algorithm == "FIFO":
                    self.fifo_queue.append(page_id)
                elif self.algorithm == "LRU":
                    self.lru_cache[page_id] = i
                return
        
        # No hay marcos libres, aplicar reemplazo
        if self.algorithm == "FIFO":
            # Implementación de FIFO
            victim_page = self.fifo_queue.popleft()
            victim_frame = self.page_table[victim_page]
            
            self.physical_memory[victim_frame] = page_id
            self.page_table[victim_page] = None
            self.page_table[page_id] = victim_frame
            
            self.fifo_queue.append(page_id)
        
        elif self.algorithm == "LRU":
            # Implementación de LRU
            victim_page, victim_frame = self.lru_cache.popitem(last=False)
            
            self.physical_memory[victim_frame] = page_id
            self.page_table[victim_page] = None
            self.page_table[page_id] = victim_frame
            
            self.lru_cache[page_id] = victim_frame
        
        elif self.algorithm == "Óptimo":
            # Implementación del algoritmo óptimo (no realista en práctica)
            # En una simulación real necesitarías conocer las referencias futuras
            pass
    
    def update_display(self):
        self.mem_canvas.delete("all")
        
        # Dibujar marcos de memoria física
        frame_width = 100
        frame_height = 60
        margin = 20
        start_x = margin
        start_y = margin
        
        for i, page in enumerate(self.physical_memory):
            x0 = start_x
            y0 = start_y + i * (frame_height + margin)
            x1 = x0 + frame_width
            y1 = y0 + frame_height
            
            color = "#90CAF9" if page else "#E0E0E0"  # Azul si está ocupado, gris si está libre
            self.mem_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black", width=2)
            self.mem_canvas.create_text((x0+x1)/2, (y0+y1)/2, 
                               text=f"Marco {i}\n{page if page else 'Libre'}",
                               font=("Courier", 8))
        
        # Dibujar tabla de páginas
        table_x = start_x + frame_width + 2*margin
        table_y = start_y
        
        self.mem_canvas.create_text(table_x, table_y-20, 
                                   text="Tabla de Páginas", anchor=tk.W)
        
        for i, (page, frame) in enumerate(self.page_table.items()):
            status = f"Marco {frame}" if frame is not None else "Disco"
            self.mem_canvas.create_text(table_x, table_y + i*20, 
                                       text=f"{page}: {status}", anchor=tk.W)
        
        # Actualizar estadísticas
        self.stats_label.config(text=f"Fallos de página: {self.page_faults}")
    
    def reset_simulation(self):
        self.reset_memory()
        self.current_process_id = 0
        self.update_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualMemorySimulator(root)
    root.geometry("800x600")
    root.mainloop()