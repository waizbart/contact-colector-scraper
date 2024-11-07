import tkinter as tk
from tkinter import messagebox
from spider import LeadSpider, get_urls
from scrapy.crawler import CrawlerProcess
import os

def run_spider():
    termo_busca = entry_termo.get()
    n_url = int(entry_n_url.get())
    n_url_skip = int(entry_n_skip.get())
    depth_limit = int(entry_depth.get())
    reject_input = entry_reject.get()
    emails = var_emails.get()
    phones = var_phones.get()

    if not termo_busca:
        messagebox.showerror("Erro", "Por favor, insira um termo de busca.")
        return

    reject = [word.strip() for word in reject_input.split(',')] if reject_input else []

    google_urls = get_urls(termo_busca, n_url, n_url_skip, 'pt')

    settings = {
        'USER_AGENT': 'Mozilla/5.0',
        'ROBOTSTXT_OBEY': False,
    }

    if depth_limit > 0:
        settings['DEPTH_LIMIT'] = depth_limit

    process = CrawlerProcess(settings=settings)
    process.crawl(LeadSpider,
                  start_urls=google_urls,
                  output_path=os.getcwd(),
                  reject=reject,
                  emails=emails,
                  phones=phones)
    process.start()

    messagebox.showinfo("Concluído", "O spider foi executado com sucesso.")
    
    root.destroy()

root = tk.Tk()
root.title("Lead Spider Interface")

tk.Label(root, text="Termo de Busca:").grid(row=0, column=0, sticky='e')
entry_termo = tk.Entry(root, width=50)
entry_termo.grid(row=0, column=1)

tk.Label(root, text="Número de URLs:").grid(row=1, column=0, sticky='e')
entry_n_url = tk.Entry(root)
entry_n_url.insert(0, "10")
entry_n_url.grid(row=1, column=1)

tk.Label(root, text="URLs a Pular:").grid(row=2, column=0, sticky='e')
entry_n_skip = tk.Entry(root)
entry_n_skip.insert(0, "0")
entry_n_skip.grid(row=2, column=1)

tk.Label(root, text="Profundidade (DEPTH_LIMIT):").grid(row=3, column=0, sticky='e')
entry_depth = tk.Entry(root)
entry_depth.insert(0, "1")
entry_depth.grid(row=3, column=1)

var_emails = tk.BooleanVar(value=True)
chk_emails = tk.Checkbutton(root, text="Coletar Emails", variable=var_emails)
chk_emails.grid(row=4, column=1, sticky='w')

var_phones = tk.BooleanVar(value=True)
chk_phones = tk.Checkbutton(root, text="Coletar Telefones", variable=var_phones)
chk_phones.grid(row=5, column=1, sticky='w')

tk.Label(root, text="Rejeitar URLs com as Palavras (separadas por vírgula):").grid(row=6, column=0, sticky='e')
entry_reject = tk.Entry(root, width=50)
entry_reject.insert(0, "facebook, instagram, twitter, linkedin, youtube")
entry_reject.grid(row=6, column=1)

btn_run = tk.Button(root, text="Executar Spider", command=run_spider)
btn_run.grid(row=7, column=1, pady=10)

root.mainloop()
