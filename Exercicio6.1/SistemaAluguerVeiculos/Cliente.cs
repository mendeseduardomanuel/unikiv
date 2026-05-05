using System;
using System.Collections.Generic;
using System.Text;

namespace SistemaAluguerVeiculos
{
    public class Cliente
    {
        public string Nome { get; set; }
        public string BI { get; set; }

        public Cliente(string nome, string bi)
        {
            Nome = nome;
            BI = bi;
        }
    }
}
