using System;
using System.Collections.Generic;
using System.Text;

namespace Loja_Online___Catálogo_de_Produtos.Model
{
    public class ProdutoDigital:Produto
    {
        public double TamanhoMB { get; set; }
        public string FormatoFicheiro { get; set; }

        public override double CalcularFrete()
        {
            return 0;
        }

        public string GerarLink()
        {
            return "link-download";
        }
    }
}
