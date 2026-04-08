using System;
using System.Collections.Generic;
using System.Text;

namespace Biblioteca_Municipal.Model
{
    public class Emprestimo
    {
        public int Id { get; set; }
        public DateTime DataEmprestimo { get; set; }
        public DateTime DataDevolucaoPrevista { get; set; }
        public DateTime? DataDevolucaoReal { get; set; }

        public Livro Livro { get; set; }
        public Membro Membro { get; set; }

        public int CalcularAtraso()
        {
            if (DataDevolucaoReal == null) return 0;

            int dias = (DataDevolucaoReal.Value - DataDevolucaoPrevista).Days;
            return dias > 0 ? dias : 0;
        }

        public bool EstaAtrasado()
        {
            return DataDevolucaoReal != null && DataDevolucaoReal > DataDevolucaoPrevista;
        }

        public double CalcularMulta(int diasAtraso)
        {
            return diasAtraso * 5; 
        }

        public void RegistarDevolucao()
        {
            DataDevolucaoReal = DateTime.Now;
            Livro.MarcarDevolvido();
        }
    }
}
