using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestão_Hospitalar.Model
{
    public class Consulta
    {
        public int Id { get; set; }
        public DateTime Data { get; set; }

        public Medico Medico { get; set; }
        public Paciente Paciente { get; set; }

        public List<Prescricao> Prescricoes { get; set; } = new();
    }
}
