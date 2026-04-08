using System;
using System.Collections.Generic;
using System.Text;

namespace Plataforma_de_Ensino_Online__E_Learning_.Model
{
    public class Instrutor : Utilizador, IAvaliavel
    {
        public string Bio { get; set; }
        public List<string> Especialidades { get; set; } = new();
        private List<double> avaliacoes = new();

        public override string GetPerfil() => "Instrutor";

        public void Avaliar(double nota)
        {
            avaliacoes.Add(nota);
        }

        public double GetMediaAvaliacoes()
        {
            return avaliacoes.Count == 0 ? 0 : avaliacoes.Average();
        }
    }
}
