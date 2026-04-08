using System;
using System.Collections.Generic;
using System.Text;

namespace Biblioteca_Municipal.Model
{
    public class Membro
    {
        public int IdMembro { get; set; }
        public string Nome { get; set; }
        public string Email { get; set; }
        public DateTime DataRegisto { get; set; }

        private List<Emprestimo> emprestimos = new List<Emprestimo>();

        public List<Emprestimo> GetEmprestimosActivos()
        {
            return emprestimos.Where(e => e.DataDevolucaoReal == null).ToList();
        }

        public bool TemMulta()
        {
            return emprestimos.Any(e => e.EstaAtrasado());
        }
    }
}
