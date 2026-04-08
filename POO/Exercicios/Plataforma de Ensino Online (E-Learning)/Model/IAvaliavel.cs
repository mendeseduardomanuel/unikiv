using System;
using System.Collections.Generic;
using System.Text;

namespace Plataforma_de_Ensino_Online__E_Learning_.Model
{
    public interface IAvaliavel
    {
        void Avaliar(double nota);
        double GetMediaAvaliacoes();
    }
}
