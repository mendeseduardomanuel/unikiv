using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_Bancário.Model
{
    public abstract class ContaBancaria : IAuditavel
    {
        public string Iban { get; set; }
        public Cliente Titular { get; set; }
        public double Saldo { get; set; }
        public DateTime DataAbertura { get; set; }

        protected List<Transaccao> historico = new List<Transaccao>();
        protected List<string> logs = new List<string>();

        public virtual bool Depositar(double valor)
        {
            Saldo += valor;
            return true;
        }

        public virtual bool Levantar(double valor)
        {
            if (Saldo >= valor)
            {
                Saldo -= valor;
                return true;
            }
            return false;
        }

        public double GetSaldo() => Saldo;

        public abstract double CalcularJuros();

        public List<Transaccao> GetHistorico() => historico;

        public void RegistarAuditoria(string mensagem)
        {
            logs.Add(mensagem);
        }

        public List<string> ObterLog() => logs;
    }
}
