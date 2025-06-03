from django.shortcuts import render, redirect
from .models import Livro
from .forms import LivroForm
from django.shortcuts import get_object_or_404 
from django.conf import settings
from datetime import datetime 
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def lista_livros(request):
    livros = Livro.objects.all()
    return render(request, 'loja/listar_livros.html', {'livros': livros})

def adicionar_livro(request):
    if request.method == 'POST':
        form = LivroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_livros')
    else:
        form = LivroForm()
    return render(request, 'loja/adicionar_livro.html', {'form': form})

def adicionar_carrinho(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)

    if livro.estoque < 1:
        return render(request, 'mensagem.html', {'mensagem': 'Estoque esgotado!'})

    carrinho = request.session.get('carrinho', {})

    if str(livro_id) in carrinho:
        if carrinho[str(livro_id)] < livro.estoque:
            carrinho[str(livro_id)] += 1
        else:
            return render(request, 'mensagem.html', {'mensagem': 'Quantidade máxima em estoque atingida.'})
    else:
        carrinho[str(livro_id)] = 1

    request.session['carrinho'] = carrinho
    return redirect('lista_livros')

def ver_carrinho(request):
    carrinho = request.session.get('carrinho', {})
    livros = []
    total = 0

    for livro_id, quantidade in carrinho.items():
        livro = get_object_or_404(Livro, id=livro_id)
        subtotal = livro.preco * quantidade
        livros.append({
            'livro': livro,
            'quantidade': quantidade,
            'subtotal': subtotal,
        })
        total += subtotal

    return render(request, 'ver_carrinho.html', {'livros': livros, 'total': total})

def finalizar_compra(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
            # Se carrinho vazio, redireciona para lista
                return redirect('lista_livros')

    livros = []
    total = 0

    for livro_id, quantidade in carrinho.items():
        livro = get_object_or_404(Livro, id=livro_id)
        subtotal = livro.preco * quantidade
        livros.append({
            'livro': livro,
            'quantidade': quantidade,
            'subtotal': subtotal,
        })
        total += subtotal

    # Criar pasta para salvar notas fiscais, se não existir
    pasta_notas = os.path.join(settings.BASE_DIR, 'notas_fiscais')
    os.makedirs(pasta_notas, exist_ok=True)

    # Nome do arquivo com timestamp para ser único
    nome_arquivo = f"nota_fiscal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    caminho_arquivo = os.path.join(pasta_notas, nome_arquivo)

    # Gerar PDF
    c = canvas.Canvas(caminho_arquivo, pagesize=letter)
    largura, altura = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, altura - 50, "Nota Fiscal - Loja de Livros")

    c.setFont("Helvetica", 12)
    y = altura - 100
    c.drawString(50, y, "Itens comprados:")
    y -= 25

    for item in livros:
        texto = f"{item['livro'].titulo} - Qtde: {item['quantidade']} - Unit: R$ {item['livro'].preco:.2f} - Subtotal: R$ {item['subtotal']:.2f}"
        c.drawString(60, y, texto)
        y -= 20

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Total: R$ {total:.2f}")

    c.showPage()
    c.save()

    for livro_id, quantidade in carrinho.items():
        livro = get_object_or_404(Livro, id=livro_id)
        if livro.estoque >= quantidade:
            livro.estoque -= quantidade
            livro.save()

    # Limpar carrinho após finalizar compra
    request.session['carrinho'] = {}

    return render(request, 'finalizar_compra.html', {'nome_arquivo': nome_arquivo})
