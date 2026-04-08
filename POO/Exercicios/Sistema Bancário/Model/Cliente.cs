using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_Bancário.Model
{
    public class Cliente
    {
        public int Id { get; set; }
        public string Nome { get; set; }
        public string Nif { get; set; }
        public string Telefone { get; set; }
        public string Email { get; set; }

        public List<ContaBancaria> Contas { get; set; } = new List<ContaBancaria>();
    }
}
