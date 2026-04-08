using System;
using System.Collections.Generic;
using System.Text;

namespace Plataforma_de_Ensino_Online__E_Learning_.Model
{
    public class Estudante : Utilizador
    {
        public Dictionary<Curso, double> Progresso { get; set; } = new();
        public List<Certificado> Certificados { get; set; } = new();

        public override string GetPerfil() => "Estudante";
    }
}
