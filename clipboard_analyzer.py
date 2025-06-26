import time
import threading
import requests
import pyperclip
import tkinter as tk

BACKEND_URL = "http://127.0.0.1:5000/analyze"
CHECK_INTERVAL = 2  # seconds

last_text = ""

def analyze_text(text, output_frame):
    try:
        res = requests.post(BACKEND_URL, json={"text": text})
        res.raise_for_status()
        data = res.json()
        results = data.get("results", [])

        verdict_display = "\n".join(
            f"[{r['verdict']}] {r['sentence']} ({r['confidence']}%)"
            for r in results
        )

        for widget in output_frame.winfo_children():
            widget.destroy()

        lbl = tk.Label(output_frame, text=verdict_display, justify="left", fg="black", font=("Segoe UI", 10), wraplength=400)
        lbl.pack()

    except Exception as e:
        lbl = tk.Label(output_frame, text=f"Error: {e}", fg="red")
        lbl.pack()

def popup_analyzer(text):
    window = tk.Tk()
    window.title("Fake News Checker")
    window.geometry("+{}+{}".format(window.winfo_pointerx(), window.winfo_pointery()))
    window.attributes("-topmost", True)

    tk.Label(window, text="Copied text:", font=("Segoe UI", 9, "bold")).pack()
    tk.Message(window, text=text.strip(), width=400).pack()

    output_frame = tk.Frame(window)
    output_frame.pack()

    tk.Button(window, text="Analyze", command=lambda: analyze_text(text, output_frame)).pack(pady=5)
    tk.Button(window, text="Close", command=window.destroy).pack()

    window.mainloop()

def watch_clipboard():
    global last_text
    while True:
        try:
            text = pyperclip.paste()
            if text != last_text and text.strip():
                last_text = text
                popup_thread = threading.Thread(target=popup_analyzer, args=(text,))
                popup_thread.start()
        except Exception as e:
            print("Clipboard error:", e)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print("📋 Clipboard Analyzer is running. Copy any text to trigger analysis...")
    watch_clipboard()