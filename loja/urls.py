from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_livros, name='lista_livros'),
    path('adicionar/', views.adicionar_livro, name='adicionar_livro'),
    path('carrinho/adicionar/<int:livro_id>/', views.adicionar_carrinho, name='adicionar_carrinho'),
    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('', views.lista_livros, name='lista_livros'),
    path('carrinho/finalizar/', views.finalizar_compra, name='finalizar_compra'),
]