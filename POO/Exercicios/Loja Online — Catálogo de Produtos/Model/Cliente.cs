using System;
using System.Collections.Generic;
using System.Text;

namespace Loja_Online___Catálogo_de_Produtos.Model
{
    public class Cliente
    {
        public string Nome { get; set; }
        public string Email { get; set; }
        public string Morada { get; set; }

        public Carrinho Carrinho { get; set; }
    }
}
