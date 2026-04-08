using System;
using System.Collections.Generic;
using System.Text;

namespace Plataforma_de_Ensino_Online__E_Learning_.Model
{
    public abstract class Utilizador
    {
        public int Id { get; set; }
        public string Email { get; set; }
        public string Senha { get; set; }
        public bool Activo { get; set; }

        public abstract string GetPerfil();
    }
}
