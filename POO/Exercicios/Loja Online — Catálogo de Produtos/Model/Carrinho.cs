using System;
using System.Collections.Generic;
using System.Text;

namespace Loja_Online___Catálogo_de_Produtos.Model
{
    public class Carrinho
    {
        public int Id { get; set; }
        public DateTime DataCriacao { get; set; }

        public List<ItemCarrinho> Itens { get; set; } = new List<ItemCarrinho>();
    }
}
