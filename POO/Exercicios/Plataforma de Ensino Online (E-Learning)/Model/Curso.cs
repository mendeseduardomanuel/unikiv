using System;
using System.Collections.Generic;
using System.Reflection;
using System.Text;

namespace Plataforma_de_Ensino_Online__E_Learning_.Model
{
    public class Curso : IAvaliavel
    {
        public int Id { get; set; }
        public string Titulo { get; set; }
        public NivelCurso Nivel { get; set; }

        public List<Modulo> Modulos { get; set; } = new();
        private List<double> avaliacoes = new();

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
