import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import pyperclip
import subprocess
from lan_tunnel import detect_minecraft_port, restart_playit_tunnel, stop_playit_tunnel  # Import backend functions

class MinecraftLanTunnelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MineTunnel - Minecraft LAN Tunneling Made Easy")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        self.root.configure(bg="#f4f4f4")

        # Center the window
        self.center_window()

        # Default values
        self.default_port = "25565"  # Default manual port value
        self.default_public_address = "name-leo.gl.joinmc.link"  # Default public tunnel address

        # Styles
        self.setup_styles()

        # Widgets
        self.create_widgets()

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")

    def setup_styles(self):
        """Set up ttk styles for modern aesthetics."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 10), background="#f4f4f4")
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        style.configure("TEntry", font=("Segoe UI", 10), padding=5)
        style.configure("Green.TButton", background="#28a745", foreground="white")
        style.configure("Red.TButton", background="#dc3545", foreground="white")
        style.configure("Blue.TButton", background="#007bff", foreground="white")
        style.configure("Output.TFrame", background="black")
        style.configure("Output.TLabel", font=("Consolas", 10), background="black", foreground="green")

    def create_widgets(self):
        """Create and layout all widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Public tunnel address
        ttk.Label(main_frame, text="🌍 Public Tunnel Address:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.public_address_entry = ttk.Entry(main_frame, width=50)
        self.public_address_entry.insert(0, self.default_public_address)
        self.public_address_entry.grid(row=0, column=1, padx=5, pady=5)

        # Manual port entry
        ttk.Label(main_frame, text="Manual Port:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.port_entry = ttk.Entry(main_frame, width=50)
        self.port_entry.insert(0, self.default_port)  # Set default port value
        self.port_entry.grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        ttk.Button(main_frame, text="🚀 Start Tunnel", style="Green.TButton", command=self.start_tunnel).grid(row=2, column=0, padx=5, pady=10)
        ttk.Button(main_frame, text="🛑 Stop Tunnel", style="Red.TButton", command=self.stop_tunnel).grid(row=2, column=1, padx=5, pady=10)
        ttk.Button(main_frame, text="Copy Port", style="Blue.TButton", command=self.copy_port).grid(row=2, column=2, padx=5, pady=10)

        # Status label
        self.status_label = ttk.Label(main_frame, text="Status: Ready", foreground="green")
        self.status_label.grid(row=3, column=0, columnspan=3, pady=10)

        # Output log area
        ttk.Label(main_frame, text="Output Log:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        output_frame = ttk.Frame(main_frame, style="Output.TFrame")
        output_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.output_text = tk.Text(output_frame, height=10, width=70, state="disabled", wrap="word", bg="black", fg="green", font=("Consolas", 10))
        self.output_text.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.output_text["yscrollcommand"] = scrollbar.set

        # Make the layout responsive
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)

    def append_output(self, message):
        """Append a message to the output log."""
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state="disabled")

    def start_tunnel(self):
        """Override the existing start_tunnel method to use the new logic."""
        threading.Thread(
            target=self.run_tunnel_with_output,
            args=(
                self.public_address_entry.get(),
                self.status_label,
                self.port_entry.get(),
            ),
            daemon=True,
        ).start()

    def run_tunnel_with_output(self, public_address, status_label, manual_port=None):
        """Run the tunnel and capture backend outputs."""
        port = manual_port if manual_port else detect_minecraft_port()
        if port is None:
            self.append_output("⚠️ Port not detected.")
            status_label.config(text="⚠️ Port not detected.", foreground="red")
            return

        try:
            self.append_output(f"🌐 Starting tunnel on port {port} with address {public_address}...")
            tunnel_output = restart_playit_tunnel(port)  # Capture the output from playit.exe
            self.append_output(tunnel_output)  # Display the output in the log
            self.append_output(f"✅ Tunnel started on port {port} with address {public_address}")
            status_label.config(text=f"✅ Tunnel started on port {port}", foreground="green")
        except FileNotFoundError:
            error_message = "⚠️ playit.exe not found in PATH!"
            self.append_output(error_message)
            status_label.config(text=error_message, foreground="red")
        except Exception as e:
            error_message = f"⚠️ Unexpected error: {e}"
            self.append_output(error_message)
            status_label.config(text=error_message, foreground="red")

    def stop_tunnel(self):
        """Stop the tunnel and log the output."""
        self.append_output("🛑 Stopping tunnel...")
        result = stop_playit_tunnel()  # Call the backend function to stop the tunnel
        if "successfully" in result:
            self.append_output(result)
            self.status_label.config(text=result, foreground="green")
        else:
            self.append_output(result)
            self.status_label.config(text=result, foreground="red")

    def copy_port(self):
        port = self.port_entry.get()
        if port:
            pyperclip.copy(port)
            self.append_output("Port copied to clipboard.")
            self.status_label.config(text="Port copied to clipboard.", foreground="blue")
        else:
            self.append_output("Error: No port to copy.")
            self.status_label.config(text="Error: No port to copy.", foreground="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftLanTunnelGUI(root)
    root.mainloop()
