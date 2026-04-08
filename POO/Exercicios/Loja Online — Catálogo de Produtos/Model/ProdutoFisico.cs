using System;
using System.Collections.Generic;
using System.Text;

namespace Loja_Online___Catálogo_de_Produtos.Model
{
    public class ProdutoFisico:Produto
    {
        public double Peso { get; set; }
        public string Dimensoes { get; set; }

        public override double CalcularFrete()
        {
            return Peso * 5;
        }
    }
}
