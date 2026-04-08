using System;
using System.Collections.Generic;
using System.Text;

namespace Plataforma_de_Ensino_Online__E_Learning_.Model
{
    public class Modulo
    {
        public int Id { get; set; }
        public string Titulo { get; set; }

        public List<Licao> Licoes { get; set; } = new();
    }
}
