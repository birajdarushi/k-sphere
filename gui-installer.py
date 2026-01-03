#!/usr/bin/env python3
"""
K-Sphere GUI Installer
A simple graphical installer for K-Sphere (future enhancement).  ..........
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os

class KSphereInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("K-Sphere Installer")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Logo/Header
        header = tk.Label(root, text="🌐 K-Sphere", font=("Helvetica", 24, "bold"))
        header.pack(pady=20)
        
        subtitle = tk.Label(root, text="AI-Powered Knowledge Management System", 
                           font=("Helvetica", 12))
        subtitle.pack()
        
        # Status
        self.status = tk.Label(root, text="Ready to install", font=("Helvetica", 10))
        self.status.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(root, length=500, mode='indeterminate')
        self.progress.pack(pady=10)
        
        # Log text
        self.log = tk.Text(root, height=10, width=70, state='disabled')
        self.log.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)
        
        self.install_btn = tk.Button(button_frame, text="Install K-Sphere", 
                                     command=self.start_installation,
                                     bg="#4CAF50", fg="white", 
                                     font=("Helvetica", 12, "bold"),
                                     padx=20, pady=10)
        self.install_btn.pack(side=tk.LEFT, padx=5)
        
        self.quit_btn = tk.Button(button_frame, text="Quit", 
                                  command=root.quit,
                                  padx=20, pady=10)
        self.quit_btn.pack(side=tk.LEFT, padx=5)
        
    def log_message(self, message):
        self.log.config(state='normal')
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.config(state='disabled')
        
    def start_installation(self):
        self.install_btn.config(state='disabled')
        self.progress.start()
        self.status.config(text="Installing K-Sphere...")
        
        # Run installation in thread
        thread = threading.Thread(target=self.run_installation)
        thread.daemon = True
        thread.start()
        
    def run_installation(self):
        try:
            self.log_message("✓ Starting installation...")
            
            # Check Docker
            self.log_message("Checking Docker...")
            result = subprocess.run(['docker', 'info'], 
                                   capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Docker is not running. Please start Docker Desktop.")
            self.log_message("✓ Docker is ready")
            
            # Run installer
            self.log_message("Running installer...")
            process = subprocess.Popen(['./install.sh'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      text=True)
            
            for line in process.stdout:
                self.log_message(line.strip())
                
            process.wait()
            
            if process.returncode == 0:
                self.status.config(text="✓ Installation complete!")
                messagebox.showinfo("Success", 
                                   "K-Sphere is now running!\n\n"
                                   "Opening browser to:\n"
                                   "http://localhost:3000")
                
                # Open browser
                subprocess.run(['open', 'http://localhost:3000'])
            else:
                raise Exception("Installation failed")
                
        except Exception as e:
            self.status.config(text="✗ Installation failed")
            self.log_message(f"\n✗ Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self.progress.stop()
            self.install_btn.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = KSphereInstaller(root)
    root.mainloop()
