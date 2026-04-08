using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestão_Hospitalar.Model
{
    public class Internamento : ITratamento
    {
        public int Id { get; set; }
        public Paciente Paciente { get; set; }

        public void IniciarTratamento() { }
        public void ConcluirTratamento() { }
        public void RegistarEvolucao(string obs) { }
    }
}
