using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestão_Hospitalar.Model
{
    public interface ITratamento
    {
        void IniciarTratamento();
        void ConcluirTratamento();
        void RegistarEvolucao(string obs);
    }
}
