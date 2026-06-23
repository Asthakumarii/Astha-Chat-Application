from cryptography.fernet import Fernet
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter import filedialog
import os
from plyer import notification


class ChatClient:
    def __init__(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.client_socket.connect((host, port))
        except Exception as e:
            messagebox.showerror("Connection Error", "Cannot connect to the server! Please run server.py first.")
            exit()

        # 1. Main GUI Window Setup (Ultra Dark Theme)
        self.window = tk.Tk()
        self.window.title("Oasis Infobyte Premium Chat")
        self.window.geometry("850x650")
        self.window.minsize(850, 650)
        self.window.configure(bg="#313338") # Premium black background

        self.main_frame = tk.Frame(self.window, bg="#313338")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.nickname = ""

        with open("secret.key", "rb") as file:
            key = file.read()

        self.cipher = Fernet(key)

        # 2. Chat Display Area (Dark background and white text)

        chat_frame = tk.Frame(self.main_frame, bg="#313338")
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Search Bar Frame
        search_frame = tk.Frame(chat_frame, bg="#313338")
        search_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        self.search_entry = tk.Entry(
            search_frame,
            bg="#2D2D2D",
            fg="white",
            insertbackground="white",
            font=("Arial", 11)
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        search_btn = tk.Button(
            search_frame,
            text="🔍 Search",
            bg="#5865F2",
            fg="white",
            command=self.search_chat
        )
        search_btn.pack(side=tk.LEFT, padx=5)

        # Chat Area
        self.chat_area = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg="#2B2D31",
            fg="#FFFFFF",
            font=("Arial", 12),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )

        self.chat_area.pack(
            padx=10,
            pady=15,
            fill=tk.BOTH,
            expand=True
        )

        self.chat_area.config(state=tk.NORMAL)

        self.chat_area.insert(tk.END,"👋 Welcome to Oasis Infobyte Premium Chat\n\n")

        self.chat_area.config(state=tk.DISABLED)

        # Online Users Panel
        users_frame = tk.Frame(self.main_frame,bg="#232428",width=150)
        users_frame.pack(side=tk.RIGHT,fill=tk.Y)

        users_label = tk.Label(
            users_frame,
            text="🟢 Online Users",
            bg="#232428",
            fg="white",
            font=("Arial", 11, "bold")
        )
        users_label.pack(pady=10)

        self.users_listbox = tk.Listbox(
            users_frame,
            bg="#2B2D31",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT
        )
        self.users_listbox.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5
        )

        # 3. Input Frame (Bottom section)
        self.input_frame = tk.Frame(self.window, bg="#313338")
        self.input_frame.pack(padx=20, pady=(0, 20), fill=tk.X)

        # 4. Message Entry Box (Large and modern look)
        self.msg_entry = tk.Entry(
            self.input_frame, 
            bg="#2D2D2D", 
            fg="#FFFFFF", 
            insertbackground="white",
            font=("Arial", 13), 
            relief=tk.FLAT,
            bd=8
        )
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.msg_entry.insert(0, "Type a message...")
        self.msg_entry.config(fg="gray")

        self.msg_entry.bind("<FocusIn>", self.clear_placeholder)
        self.msg_entry.bind("<FocusOut>", self.add_placeholder)
        self.msg_entry.bind("<Return>", self.send_message)

        # 5. Send Button
        self.send_button = tk.Button(
            self.input_frame, 
            text="Send", 
            bg="#5865F2", 
            fg="white", 
            font=("Segoe UI", 11, "bold"), 
            relief=tk.FLAT,
            padx=20,
            command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_button = tk.Button(
            self.input_frame,
            text="📁",
            bg="#57F287",
            fg="black",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            padx=15,
            command=self.send_file
        )
        self.file_button.pack(side=tk.RIGHT, padx=5)

        self.logout_button = tk.Button(
            self.input_frame,
            text="Logout",
            bg="#ED4245",
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            padx=15,
            command=self.logout
        )
        self.logout_button.pack(side=tk.RIGHT, padx=5)
        
        # Emoji Row
        emoji_frame = tk.Frame(self.window, bg="#313338")
        emoji_frame.pack(pady=(5, 15))

        emojis = ["😀", "😂", "😍", "👍", "🔥", "❤️", "🎉"]

        for e in emojis:
            btn = tk.Button(
                emoji_frame,
                text=e,
                font=("Segoe UI Emoji", 14),
                bg="#2D2D2D",
                fg="white",
                relief=tk.FLAT,
                command=lambda emoji=e: self.add_emoji(emoji)
            )
            btn.pack(side=tk.LEFT, padx=3)

        # Open the name setup popup right after the chat window appears
        self.window.after(100, self.ask_nickname_popup)
        self.window.protocol("WM_DELETE_WINDOW", self.logout)
        self.window.mainloop()

    def ask_nickname_popup(self):
        """A large and beautiful dark popup to input username"""
        self.dialog = tk.Toplevel(self.window)
        self.dialog.title("Chat Setup")
        self.dialog.geometry("450x400")
        self.dialog.configure(bg="#1E1E1E")
        self.dialog.resizable(False, False)
        
        # Keep this popup always on top of the main window
        self.dialog.transient(self.window)
        self.dialog.grab_set()
        
        # If user closes this popup using the 'X' button, close the entire program
        self.dialog.protocol("WM_DELETE_WINDOW", exit)

        # Large Heading Label
        self.popup_label = tk.Label(
            self.dialog, 
            text="Enter Username and Password", 
            bg="#1E1E1E", 
            fg="#FFFFFF", 
            font=("Arial", 14, "bold"),
            pady=15
        )
        self.popup_label.pack()

        username_label = tk.Label(
            self.dialog,
            text="Username",
            bg="#1E1E1E",
            fg="white",
            font=("Arial", 11, "bold")
        )
        username_label.pack(anchor="w", padx=30)

        # Username Entry
        self.name_entry = tk.Entry(
            self.dialog, 
            bg="#2D2D2D", 
            fg="#FFFFFF", 
            insertbackground="white", 
            font=("Arial", 14), 
            relief=tk.FLAT,
            justify="center"
        )
        self.name_entry.pack(padx=30, pady=10, fill=tk.X)

        password_label = tk.Label(
            self.dialog,
            text="Password",
            bg="#1E1E1E",
            fg="white",
            font=("Arial", 11, "bold")
        )
        password_label.pack(anchor="w", padx=30)
        
        # Password Entry Box
        self.password_entry = tk.Entry(
            self.dialog,
            bg="#2D2D2D",
            fg="#FFFFFF",
            insertbackground="white",
            font=("Arial", 14),
            relief=tk.FLAT,
            justify="center",
            show="*"
        )
        self.password_entry.pack(padx=30, pady=10, fill=tk.X)

        # Room Selection
        room_label = tk.Label(
            self.dialog,
            text="Select Room",
            bg="#1E1E1E",
            fg="white",
            font=("Arial", 11, "bold")
        )
        room_label.pack(anchor="w", padx=30)

        self.room_var = tk.StringVar()
        self.room_var.set("General")

        room_menu = tk.OptionMenu(
            self.dialog,
            self.room_var,
            "General",
            "Python",
            "Placement"
        )
        room_menu.pack(padx=30, pady=10, fill=tk.X)

        self.name_entry.focus_set()
        self.name_entry.bind("<Return>", self.submit_nickname)

        # Submit Button
        submit_btn = tk.Button(
            self.dialog, 
            text="Login", 
            bg="#2ECC71", 
            fg="white", 
            font=("Segoe", 11, "bold"),
            relief=tk.FLAT,
            command=self.submit_nickname,
            pady=5
        )
        submit_btn.pack(pady=15)

    def submit_nickname(self, event=None):
        username = self.name_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.popup_label.config(
                text="⚠️ Username and Password required!",
                fg="#E74C3C"
            )
            return

        try:
            login_data = f"{username},{password}"
            self.client_socket.send(login_data.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')
            if response == "AUTH_SUCCESS":
                self.nickname = username
                selected_room = self.room_var.get()
                
                self.client_socket.send(selected_room.encode('utf-8'))
                self.window.title(
                    f"{selected_room} Room - ({self.nickname})"
                )

                self.dialog.destroy()
                self.receive_thread = threading.Thread(
                    target=self.receive_messages
                )
                self.receive_thread.daemon = True
                self.receive_thread.start()

            else:
                self.popup_label.config(
                    text="❌ Invalid Username or Password",
                    fg="#E74C3C"
                )

        except:
            messagebox.showerror(
                "Login Error",
                "Could not authenticate with server."
            )

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                if message.startswith("[SYSTEM] Online Users:"):

                    users = message.replace("[SYSTEM] Online Users:","").strip()

                    self.users_listbox.delete(0, tk.END)

                    for user in users.split(","):
                        self.users_listbox.insert(
                            tk.END,
                            user.strip()
                        )

                    continue
                
                self.chat_area.config(state=tk.NORMAL)
                self.chat_area.insert(tk.END, f"{message}\n\n")
                self.chat_area.config(state=tk.DISABLED)
                self.chat_area.yview(tk.END) 

                self.show_notification(message)
            except:
                break

    def add_emoji(self, emoji):
        self.msg_entry.insert(tk.END, emoji)

    def show_notification(self, message):
        notification.notify(title="New Message",message=message,timeout=5)

    def clear_placeholder(self, event):

        if self.msg_entry.get() == "Type a message...":
            self.msg_entry.delete(0, tk.END)
            self.msg_entry.config(fg="white")

    def add_placeholder(self, event):
        if not self.msg_entry.get().strip():
            self.msg_entry.delete(0, tk.END)
            self.msg_entry.insert(0, "Type a message...")
            self.msg_entry.config(fg="gray")

    def search_chat(self):
        keyword = self.search_entry.get().lower()

        self.chat_area.tag_remove("highlight","1.0",tk.END)

        if not keyword:
            return

        start = "1.0"

        while True:
            pos = self.chat_area.search(
                keyword,
                start,
                stopindex=tk.END,
                nocase=True
            )

            if not pos:
                break

            end = f"{pos}+{len(keyword)}c"

            self.chat_area.tag_add("highlight",pos,end)

            start = end

        self.chat_area.tag_config("highlight",background="yellow",foreground="black")
    

    def send_message(self, event=None):
    
        message = self.msg_entry.get().strip()

        #message = message.replace("Type a message...","").strip()

        if not message:
            return

        if message == "Type a message...":
            return
        if message:
            try:
                encrypted_message = self.cipher.encrypt(message.encode('utf-8'))

                self.client_socket.send(encrypted_message)
                
                self.chat_area.config(state=tk.NORMAL)
                self.chat_area.insert(tk.END, f"[You]: {message}\n\n")
                self.chat_area.config(state=tk.DISABLED)
                self.chat_area.yview(tk.END)
                
                self.msg_entry.delete(0, tk.END)
                self.msg_entry.focus_set() 
            except Exception as e:
                messagebox.showerror("Error", "Failed to send message.",e)

    def send_file(self):
        filepath = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("All Files", "*.*")]
        )

        if filepath:
            filename = os.path.basename(filepath)

            try:
                with open(filepath, "rb") as file:
                    data = file.read()

                header = self.cipher.encrypt(f"FILE:{filename}".encode('utf-8'))

                self.client_socket.send(header)

                self.client_socket.send(data)

                self.chat_area.config(state=tk.NORMAL)
                self.chat_area.insert(
                    tk.END,
                    f"[You] shared file: {filename}\n\n"
                )
                self.chat_area.config(state=tk.DISABLED)
                self.chat_area.yview(tk.END)

            except Exception:
                 pass

    def logout(self):
        try:
            self.client_socket.close()
        except:
            pass

        self.window.destroy()

if __name__ == "__main__":
    ChatClient('127.0.0.1', 5000)