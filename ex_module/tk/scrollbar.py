import tkinter as tk

programming = ['Java', 'Python', 'C++',
               'C#', 'JavaScript', 'NodeJS',
               'Kotlin', 'VB.Net', 'MySql', 'SQLite',
               'Java', 'Python', 'C++',
               'C#', 'JavaScript', 'NodeJS',
               'Kotlin', 'VB.Net', 'MySql', 'SQLite',
               'Java', 'Python', 'C++',
               'C#', 'JavaScript', 'NodeJS',
               'Kotlin', 'VB.Net', 'MySql', 'SQLite',
               'Java', 'Python', 'C++',
               'C#', 'JavaScript', 'NodeJS',
               'Kotlin', 'VB.Net', 'MySql', 'SQLite']

# Création de la fenêtre principale
window = tk.Tk()
window.title("Exemple de Scrollbar")
window.geometry("600x300")
# Création du widget Listbox
listbox = tk.Listbox(window)

# Création du widget Scrollbar
scrollbar = tk.Scrollbar(window)

# Configuration de la relation entre le Listbox et le Scrollbar
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

# Ajout des éléments à la liste
for item in programming:
    listbox.insert(tk.END, item)

# Placement des widgets dans la fenêtre
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Lancement de la boucle principale
window.mainloop()