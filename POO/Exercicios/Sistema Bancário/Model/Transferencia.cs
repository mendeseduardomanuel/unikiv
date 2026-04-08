using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_Bancário.Model
{
    public class Transferencia : Transaccao
    {
        public ContaBancaria ContaOrigem { get; set; }
        public ContaBancaria ContaDestino { get; set; }
    }
}
