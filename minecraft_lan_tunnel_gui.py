import os
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import pyperclip
import subprocess
from lan_tunnel import detect_minecraft_port, restart_playit_tunnel  # Import backend functions

def start_tunnel(public_address, log_path, status_label, ip_entry, manual_port=None):
    """Start the Playit tunnel and update the GUI."""
    port = manual_port if manual_port else detect_minecraft_port()
    if port is None:
        status_label.config(text="⚠️ Port not detected.", fg="red")
        return

    try:
        restart_playit_tunnel(port)
        tunnel_address = f"{public_address}:{port}"
        pyperclip.copy(tunnel_address)
        ip_entry.delete(0, tk.END)
        ip_entry.insert(0, tunnel_address)
        status_label.config(text=f"✅ Tunnel started: {tunnel_address}", fg="green")
    except FileNotFoundError:
        status_label.config(text="⚠️ playit.exe not found in PATH!", fg="red")
    except Exception as e:
        status_label.config(text=f"⚠️ Unexpected error: {e}", fg="red")

def start_tunnel_thread(public_address, log_path, status_label, ip_entry, manual_port=None):
    """Run the tunnel start process in a separate thread."""
    threading.Thread(target=start_tunnel, args=(public_address, log_path, status_label, ip_entry, manual_port), daemon=True).start()

def stop_tunnel(status_label):
    """Stop the Playit tunnel."""
    try:
        subprocess.run(["taskkill", "/IM", "playit.exe", "/F"], check=True)
        status_label.config(text="🛑 Tunnel stopped.", fg="red")
    except subprocess.CalledProcessError:
        status_label.config(text="⚠️ Failed to stop tunnel. Playit may not be running.", fg="red")
    except Exception as e:
        status_label.config(text=f"⚠️ Unexpected error: {e}", fg="red")

class MinecraftLanTunnelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MineTunnel - Minecraft LAN Tunneling Made Easy")

        # Default paths
        self.default_log_path = os.path.expanduser("~\\AppData\\Roaming\\.minecraft\\logs\\latest.log")
        self.default_public_address = "name-leo.gl.joinmc.link"

        # Widgets
        self.create_widgets()

    def create_widgets(self):
        # Minecraft log file path
        tk.Label(self.root, text="Minecraft Log File Path:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.log_path_entry = tk.Entry(self.root, width=50)
        self.log_path_entry.insert(0, self.default_log_path)
        self.log_path_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_log_file).grid(row=0, column=2, padx=5, pady=5)

        # Public tunnel address
        tk.Label(self.root, text="🌍 Public Tunnel Address:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.public_address_entry = tk.Entry(self.root, width=50)
        self.public_address_entry.insert(0, self.default_public_address)
        self.public_address_entry.grid(row=1, column=1, padx=5, pady=5)

        # Manual port entry
        tk.Label(self.root, text="Manual Port:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.port_entry = tk.Entry(self.root, width=50)
        self.port_entry.grid(row=2, column=1, padx=5, pady=5)

        # Tunnel public address
        tk.Label(self.root, text="Tunnel Public Address:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.tunnel_address_entry = tk.Entry(self.root, width=50)
        self.tunnel_address_entry.grid(row=3, column=1, padx=5, pady=5)

        # Buttons
        tk.Button(self.root, text="Launch Minecraft World", command=self.launch_minecraft).grid(row=4, column=0, padx=5, pady=10)
        tk.Button(
            self.root, text="🚀 Start Tunnel",
            command=lambda: self.start_tunnel()
        ).grid(row=4, column=1, padx=5, pady=10)
        tk.Button(self.root, text="🛑 Stop Tunnel", command=lambda: self.stop_tunnel()).grid(row=4, column=2, padx=5, pady=10)
        tk.Button(self.root, text="Copy IP", command=self.copy_ip).grid(row=5, column=1, padx=5, pady=10)

        # Status label
        self.status_label = tk.Label(self.root, text="Status: Ready", fg="green")
        self.status_label.grid(row=6, column=0, columnspan=3, pady=10)

        # Output log area
        tk.Label(self.root, text="Output Log:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.output_text = tk.Text(self.root, height=10, width=70, state="disabled", wrap="word")
        self.output_text.grid(row=8, column=0, columnspan=3, padx=5, pady=5)

    def append_output(self, message):
        """Append a message to the output log."""
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state="disabled")

    def browse_log_file(self):
        path = filedialog.askopenfilename(filetypes=[("Log Files", "*.log"), ("All Files", "*.*")])
        if path:
            self.log_path_entry.delete(0, tk.END)
            self.log_path_entry.insert(0, path)

    def launch_minecraft(self):
        messagebox.showinfo("Launch Minecraft", "This feature is a placeholder. Customize as needed.")

    def start_tunnel(self):
        """Override the existing start_tunnel method to use the new logic."""
        threading.Thread(
            target=self.run_tunnel_with_output,
            args=(
                self.public_address_entry.get(),
                self.log_path_entry.get(),
                self.status_label,
                self.tunnel_address_entry,
                self.port_entry.get(),
            ),
            daemon=True,
        ).start()

    def run_tunnel_with_output(self, public_address, log_path, status_label, ip_entry, manual_port=None):
        """Run the tunnel and capture backend outputs."""
        port = manual_port if manual_port else detect_minecraft_port()
        if port is None:
            self.append_output("⚠️ Port not detected.")
            status_label.config(text="⚠️ Port not detected.", fg="red")
            return

        try:
            self.append_output(f"🌐 Starting tunnel on port {port}...")
            restart_playit_tunnel(port)
            tunnel_address = f"{public_address}:{port}"
            pyperclip.copy(tunnel_address)
            ip_entry.delete(0, tk.END)
            ip_entry.insert(0, tunnel_address)
            status_label.config(text=f"✅ Tunnel started: {tunnel_address}", fg="green")
            self.append_output(f"✅ Tunnel started: {tunnel_address}")
        except FileNotFoundError:
            error_message = "⚠️ playit.exe not found in PATH!"
            self.append_output(error_message)
            status_label.config(text=error_message, fg="red")
        except Exception as e:
            error_message = f"⚠️ Unexpected error: {e}"
            self.append_output(error_message)
            status_label.config(text=error_message, fg="red")

    def stop_tunnel(self):
        """Stop the tunnel and log the output."""
        try:
            subprocess.run(["taskkill", "/IM", "playit.exe", "/F"], check=True)
            self.append_output("🛑 Tunnel stopped.")
            self.status_label.config(text="🛑 Tunnel stopped.", fg="red")
        except subprocess.CalledProcessError:
            error_message = "⚠️ Failed to stop tunnel. Playit may not be running."
            self.append_output(error_message)
            self.status_label.config(text=error_message, fg="red")
        except Exception as e:
            error_message = f"⚠️ Unexpected error: {e}"
            self.append_output(error_message)
            self.status_label.config(text=error_message, fg="red")

    def copy_ip(self):
        address = self.tunnel_address_entry.get()
        if address:
            pyperclip.copy(address)
            self.update_status("IP copied to clipboard.", "green")
        else:
            self.update_status("Error: No IP to copy.", "red")

    def update_status(self, message, color):
        self.status_label.config(text=f"Status: {message}", fg=color)

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftLanTunnelGUI(root)
    root.mainloop()
