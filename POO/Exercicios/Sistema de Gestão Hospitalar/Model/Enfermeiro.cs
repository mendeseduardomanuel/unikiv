using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestão_Hospitalar.Model
{
    public class Enfermeiro : Pessoa
    {
        public TipoTurno Turno { get; set; }
    }
}
