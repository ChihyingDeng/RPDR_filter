import tkinter as tk

from main_application import MainApplication


def main():
    title = "Clinical Notes Convert and Filter Tool"
    root = tk.Tk()
    root.geometry('{}x{}'.format(500, 300))
    root.title(title)
    MainApplication(root).grid(column=0, row=0)
    root.mainloop()


if __name__ == '__main__':
    main()
