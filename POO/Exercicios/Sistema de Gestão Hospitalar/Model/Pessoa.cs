using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestão_Hospitalar.Model
{
    public abstract class Pessoa
    {
        public string Nome { get; set; }
        public DateTime DataNascimento { get; set; }
        public string Telefone { get; set; }
    }
}
