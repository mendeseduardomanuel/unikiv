using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_Bancário.Model
{
    public interface IAuditavel
    {
        void RegistarAuditoria(string mensagem);
        List<string> ObterLog();
    }
}
