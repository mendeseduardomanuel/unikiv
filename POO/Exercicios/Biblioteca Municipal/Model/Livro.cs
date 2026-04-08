using System;
using System.Collections.Generic;
using System.Text;

namespace Biblioteca_Municipal.Model
{
    public class Livro
    {
        public string Isbn { get; set; }
        public string Titulo { get; set; }
        public string Autor { get; set; }
        public int AnoPublicacao { get; set; }
        public bool Disponivel { get; set; }

        public bool EstaDisponivel()
        {
            return Disponivel;
        }

        public void MarcarEmprestado()
        {
            Disponivel = false;
        }

        public void MarcarDevolvido()
        {
            Disponivel = true;
        }
    }
}
