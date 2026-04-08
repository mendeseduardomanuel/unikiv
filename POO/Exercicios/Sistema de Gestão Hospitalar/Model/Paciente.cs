using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestão_Hospitalar.Model
{
    public class Paciente : Pessoa
    {
        public string NumProcesso { get; set; }
        public string GrupoSanguineo { get; set; }
    }
}
