using System;
using System.Collections.Generic;
using System.Text;

namespace Loja_Online___Catálogo_de_Produtos.Model
{
    public abstract class Produto
    {
        public int Id { get; set; }
        public string Nome { get; set; }
        public string Descricao { get; set; }
        public double Preco { get; set; }
        public int Stock { get; set; }

        public double GetPreco() => Preco;

        public bool TemStock() => Stock > 0;

        public void ReduzirStock(int qtd)
        {
            Stock -= qtd;
        }

        public abstract double CalcularFrete();
    }
}
