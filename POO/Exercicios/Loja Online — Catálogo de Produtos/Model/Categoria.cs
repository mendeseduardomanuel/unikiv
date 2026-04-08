using System;
using System.Collections.Generic;
using System.Text;

namespace Loja_Online___Catálogo_de_Produtos.Model
{
    public class Categoria
    {
        public int Id { get; set; }
        public string Nome { get; set; }
        public string Descricao { get; set; }

        public List<Produto> Produtos { get; set; } = new List<Produto>();
    }
}
